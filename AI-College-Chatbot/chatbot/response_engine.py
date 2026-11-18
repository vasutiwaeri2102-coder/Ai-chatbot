"""
response_engine.py
===================
Sits on top of nlp_engine.py and wires the NLP logic to the database.

Responsibilities:
    - load_faqs(): fetch the current FAQ list from the database (so the
      chatbot always reflects the latest data added/edited from the
      admin panel, with no code changes needed).
    - process_query(): full pipeline from raw question -> final answer.
    - get_response(): convenience wrapper that also logs the interaction
      to chat_history.
"""
from flask import current_app
from extensions import db
from models.faq import FAQ
from models.chat_history import ChatHistory
from chatbot.nlp_engine import find_best_match

FALLBACK_MESSAGE = (
    "I'm sorry, I couldn't find a reliable answer to that question. "
    "Please try asking about admissions, courses, fees, exams, timetable, "
    "faculty, library, hostel, placements, scholarships, or contact the "
    "college administration directly."
)

EMPTY_QUERY_MESSAGE = "Please type a question so I can help you."

TOO_LONG_MESSAGE = (
    "That question is quite long. Could you please shorten it to a single, "
    "clear question so I can find the best answer?"
)

MAX_QUERY_LENGTH = 400


def load_faqs():
    """Load every FAQ from the database. Always reflects the latest admin edits."""
    return FAQ.query.all()


def process_query(user_query):
    """
    Run the full NLP pipeline on a raw user query and return a dict with
    the result. Does NOT touch the database (no logging) - see
    get_response() for the version that also logs to chat_history.
    """
    query = (user_query or "").strip()

    if not query:
        return {
            "answer": EMPTY_QUERY_MESSAGE,
            "category": None,
            "confidence": 0.0,
            "matched_faq_id": None,
            "is_fallback": True,
        }

    if len(query) > MAX_QUERY_LENGTH:
        return {
            "answer": TOO_LONG_MESSAGE,
            "category": None,
            "confidence": 0.0,
            "matched_faq_id": None,
            "is_fallback": True,
        }

    faqs = load_faqs()
    threshold = current_app.config.get("SIMILARITY_THRESHOLD", 0.20)

    best_faq, score = find_best_match(query, faqs)

    if best_faq is not None and score >= threshold:
        return {
            "answer": best_faq.answer,
            "category": best_faq.category,
            "confidence": round(float(score), 3),
            "matched_faq_id": best_faq.id,
            "is_fallback": False,
        }

    return {
        "answer": FALLBACK_MESSAGE,
        "category": None,
        "confidence": round(float(score), 3),
        "matched_faq_id": None,
        "is_fallback": True,
    }


def get_response(user_query):
    """
    Full pipeline + persistence: runs process_query() and stores the
    interaction in chat_history for admin analytics.
    """
    result = process_query(user_query)

    try:
        history_entry = ChatHistory(
            user_question=(user_query or "").strip()[:500],
            bot_answer=result["answer"],
            similarity_score=result["confidence"],
            matched_faq_id=result["matched_faq_id"],
        )
        db.session.add(history_entry)
        db.session.commit()
    except Exception:
        # Logging failures should never break the chat experience for
        # the student - roll back and continue.
        db.session.rollback()

    return result
