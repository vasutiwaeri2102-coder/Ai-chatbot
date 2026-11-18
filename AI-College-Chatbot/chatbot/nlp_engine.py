"""
nlp_engine.py
=============
This module contains all the Natural Language Processing logic used to
match a student's free-text question to the closest stored FAQ.

Pipeline (see README.md for a full explanation):

    raw user query
        -> preprocess_text()      (clean, lowercase, tokenize, remove
                                    stopwords, lemmatize)
        -> TF-IDF vectorization   (turn text into numeric vectors)
        -> cosine_similarity      (compare query vector to every FAQ vector)
        -> find_best_match()      (pick the highest scoring FAQ)
        -> confidence threshold   (reject weak matches)
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# NLTK setup (optional dependency)
# ---------------------------------------------------------------------------
# NLTK is used for tokenizing, stopword removal and lemmatization, which
# improves match quality. However the whole `nltk` package - and/or its
# small data packages (punkt, stopwords, wordnet) - may not be available
# in every environment (e.g. no internet access to download data). In
# that case we transparently fall back to a simpler regex/set-based
# implementation further below, so the chatbot always keeps working.
_NLTK_READY = False
STOPWORDS = None
LEMMATIZER = None

try:
    import nltk

    _NLTK_PACKAGES = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]

    for _path, _package in _NLTK_PACKAGES:
        try:
            nltk.data.find(_path)
        except LookupError:
            try:
                nltk.download(_package, quiet=True)
            except Exception:
                # If download fails (e.g. no internet), we fall back to a
                # simpler regex-based tokenizer defined below.
                pass

    from nltk.corpus import stopwords as nltk_stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize

    STOPWORDS = set(nltk_stopwords.words("english"))
    LEMMATIZER = WordNetLemmatizer()
    _NLTK_READY = True
except Exception:
    # Minimal fallback stopword list if the nltk package (or its data)
    # could not be loaded. Covers the most common English stopwords that
    # would otherwise add noise to the TF-IDF vectors.
    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were", "am", "be", "been",
        "being", "do", "does", "did", "of", "in", "on", "at", "to", "for",
        "and", "or", "but", "with", "about", "as", "i", "you", "your",
        "he", "she", "it", "its", "we", "they", "them", "their", "what",
        "which", "who", "whom", "this", "that", "these", "those", "how",
        "can", "could", "would", "should", "will", "shall", "there",
        "here", "from", "into", "than", "then", "so", "if", "my", "me",
        "have", "has", "had", "not", "no", "up", "out", "all", "any",
        "some", "when", "where", "why", "please", "also",
    }
    LEMMATIZER = None
    _NLTK_READY = False


def _simple_stem(word):
    """
    Very small, dependency-free suffix stripper used only when the real
    NLTK WordNetLemmatizer is unavailable. It is NOT linguistically
    perfect, but it is enough to merge common variants such as
    "fee"/"fees", "book"/"books", "apply"/"applies" so that TF-IDF
    matching still works reasonably well without NLTK installed.
    """
    if len(word) <= 3:
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("es") and word[-3] in ("s", "x", "z", "h"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    return word


def preprocess_text(text):
    """
    Clean and normalize a piece of text so it is ready for TF-IDF.

    Steps:
        1. Lowercase everything
        2. Remove punctuation / special characters
        3. Tokenize into words
        4. Remove common English stopwords
        5. Lemmatize each word to its base/dictionary form

    Returns a single cleaned string (words separated by spaces).
    """
    if not text:
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove punctuation and non-alphanumeric characters
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # 3. Tokenize
    if _NLTK_READY:
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()
    else:
        tokens = text.split()

    # 4. Remove stopwords (but keep short numeric tokens like years)
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    # 5. Reduce words to a common base form so variants like "fee"/"fees"
    # or "apply"/"applying" are treated as the same word by TF-IDF.
    if LEMMATIZER is not None:
        tokens = [LEMMATIZER.lemmatize(t) for t in tokens]
    else:
        tokens = [_simple_stem(t) for t in tokens]

    return " ".join(tokens)


def build_corpus(faqs):
    """
    Build the text corpus used to fit the TF-IDF vectorizer.

    Each FAQ contributes its question text plus its optional keywords,
    since keywords give the model extra signal for matching differently
    worded queries (e.g. "fee structure" FAQ tagged with keywords
    "fees, payment, tuition, cost").

    `faqs` is a list of FAQ model instances (or dicts with the same keys).
    Returns a list of cleaned strings, one per FAQ, in the same order.
    """
    corpus = []
    for faq in faqs:
        question = faq.question if hasattr(faq, "question") else faq.get("question", "")
        keywords = faq.keywords if hasattr(faq, "keywords") else faq.get("keywords", "")
        # The question text is repeated so it carries more weight than
        # the keyword list when TF-IDF scores are computed - the exact
        # wording of the stored question is the strongest signal we have.
        combined = f"{question} {question} {keywords or ''}"
        corpus.append(preprocess_text(combined))
    return corpus


def calculate_similarity(query, corpus):
    """
    Vectorize the query together with the FAQ corpus using TF-IDF and
    compute cosine similarity between the query and every FAQ.

    Returns a list of similarity scores (floats between 0 and 1), one
    per document in `corpus`, in the same order as `corpus`.
    """
    if not corpus:
        return []

    cleaned_query = preprocess_text(query)

    # Fit the vectorizer on FAQ corpus + the incoming query together so
    # that both live in the same vector space.
    documents = corpus + [cleaned_query]

    # ngram_range=(1, 2) lets the vectorizer also consider two-word
    # phrases (e.g. "fee structure"), which helps distinguish FAQs that
    # share individual words but mean different things.
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        # Happens if every document is empty after cleaning
        return [0.0] * len(corpus)

    query_vector = tfidf_matrix[-1]
    faq_vectors = tfidf_matrix[:-1]

    scores = cosine_similarity(query_vector, faq_vectors)[0]
    return scores.tolist()


def find_best_match(query, faqs):
    """
    Given a raw user query and a list of FAQ objects, find the single
    best matching FAQ.

    Returns a tuple: (best_faq_or_None, best_score_float)
    """
    if not faqs:
        return None, 0.0

    corpus = build_corpus(faqs)
    scores = calculate_similarity(query, corpus)

    if not scores:
        return None, 0.0

    best_index = max(range(len(scores)), key=lambda i: scores[i])
    best_score = scores[best_index]
    best_faq = faqs[best_index]

    return best_faq, best_score
