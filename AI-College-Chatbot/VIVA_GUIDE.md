# How to Explain This Project in Viva

Short, easy-to-memorize answers for common viva questions.

**1. What is the project?**
A web-based AI chatbot that answers college-related questions (admissions, fees, exams, hostel, etc.) by understanding natural language, not just exact keywords.

**2. Why did we choose this project?**
Students repeatedly ask the same questions to the college office. An AI chatbot reduces that repetitive load while giving students instant, 24/7 answers.

**3. What problem does it solve?**
It solves the problem of students not getting quick answers to common queries outside office hours, and reduces the manual burden on administrative staff.

**4. Why Python?**
Python has strong, beginner-friendly libraries for both web development (Flask) and machine learning/NLP (scikit-learn, NLTK), so the whole project can be built with one language.

**5. Why Flask?**
Flask is a lightweight Python web framework — easy to understand, doesn't force a rigid structure, and is perfect for a project of this scale (unlike heavier frameworks like Django).

**6. What is NLP?**
NLP (Natural Language Processing) is the field of AI that helps computers understand and process human language, so a program can figure out what a sentence *means*, not just match exact text.

**7. What is TF-IDF?**
TF-IDF (Term Frequency–Inverse Document Frequency) is a way to convert text into numbers. It gives more weight to words that are frequent in a specific question but rare across all questions — so distinctive words matter more than common ones.

**8. What is Cosine Similarity?**
It's a way to measure how similar two pieces of text are by comparing the angle between their TF-IDF vectors. A smaller angle (closer to 1.0 similarity) means the texts are about the same topic.

**9. How does the chatbot understand differently worded questions?**
Every question is cleaned, tokenized, and converted into a TF-IDF vector. Then cosine similarity compares the user's question vector against every stored FAQ vector, and the FAQ with the highest similarity score is returned as the answer — this way, different phrasings of the same question can still match.

**10. How does the database work?**
SQLite stores five tables: `admins`, `faqs`, `chat_history`, `notices`, and `college_info`. Flask-SQLAlchemy (an ORM) lets us work with these tables using Python classes instead of writing raw SQL.

**11. What happens when there is no matching answer?**
If the highest similarity score is below a set threshold (e.g. 0.20), the chatbot doesn't guess — it returns a polite fallback message suggesting the student ask about a supported topic or contact administration.

**12. Why did we use SQLite?**
SQLite needs no separate server, stores the whole database in one file, and is perfect for a small-to-medium academic project that runs locally.

**13. What is an API?**
An API (Application Programming Interface) is a set of defined URLs (endpoints) the frontend can call to get or send data — for example, `POST /api/chat` sends a question and receives an answer as JSON.

**14. How does frontend communicate with backend?**
The JavaScript frontend uses the `fetch()` function to send AJAX requests to Flask API endpoints and receives JSON responses, updating the page without a full reload.

**15. What is the role of each team member?**
See `TEAM_RESPONSIBILITIES.md` for the full breakdown (Backend/DB, NLP engine, Frontend, Admin panel & testing).

**16. What are the limitations?**
The chatbot can only answer questions covered by its FAQ dataset; it can't reason about brand-new topics, doesn't support multiple languages yet, and its accuracy depends on how well the FAQ questions/keywords are written.

**17. What is the future scope?**
Adding Hindi/English support, voice input/output, WhatsApp integration, personalized student logins, and optionally a modern LLM API for more open-ended questions.
