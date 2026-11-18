# Suggested Team Responsibilities

A realistic 4-way split of this project, so each member can confidently own and explain their part in the viva.

## Vasu Tiwari — Backend & Database Lead
- `app.py`, `config.py`, `extensions.py`
- All files in `models/` (SQLAlchemy schema design)
- `scripts/seed_database.py`
- Database design decisions (tables, relationships, constraints)
- Security: password hashing, session handling, `.env` configuration

## Sheetla Vishwakarma — NLP / AI Engine Lead
- `chatbot/nlp_engine.py` — text preprocessing, TF-IDF, cosine similarity
- `chatbot/response_engine.py` — confidence threshold logic, chat history logging
- Building and curating `data/sample_faqs.json` (questions, keyword variants)
- Tuning the similarity threshold and testing matching accuracy
- Explaining the NLP pipeline in the viva (questions 6–11 in `VIVA_GUIDE.md`)

## Pranav — Student Frontend Lead
- `templates/index.html`, `static/css/style.css`, `static/js/chat.js`
- Chat UI/UX: bubbles, typing indicator, category buttons, suggested questions
- Responsive design across desktop/tablet/mobile
- Connecting the frontend to `/api/chat`, `/api/categories`, `/api/notices`

## Anurag — Admin Panel & Testing Lead
- `templates/admin/*`, `static/css/admin.css`, `static/js/admin.js`
- `routes/admin.py`, `routes/faq.py`, `routes/dashboard.py`
- Admin login flow, CSRF protection, FAQ/Notice CRUD screens
- End-to-end testing: empty inputs, long inputs, invalid logins, wrong routes
- Writing/updating `README.md` and coordinating the final demo run-through

**Shared responsibility for everyone:** understanding the full data flow (student question → API → NLP engine → database → response) well enough to answer any viva question, not just the part they personally built.
