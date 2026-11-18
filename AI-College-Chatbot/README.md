# AI College Assistant — College Query Chatbot

A full-stack, NLP-powered chatbot that answers student questions about admissions, courses, fees, exams, timetable, faculty, library, hostel, placements, and more — built with **Flask**, **scikit-learn (TF-IDF + Cosine Similarity)**, and **SQLite**.

Built as a mini project by **Vasu Tiwari, Sheetla Vishwakarma, Pranav, and Anurag**.

---

## 1. Project Overview

Students often ask the same question in many different ways — *"What is the college fee?"*, *"How much fees do I need to pay?"*, *"Tell me about fee structure."* — and expect the same accurate answer. This project builds a chatbot that understands the **meaning** of a question, not just exact keywords, using a real NLP pipeline (TF-IDF vectorization + cosine similarity), and answers from a FAQ database that admins can update anytime without touching code.

## 2. Features

**Student-facing**
- Natural-language chat with typing indicator, timestamps, and chat bubbles
- Category quick-buttons (Admissions, Courses, Fees, Exams, Timetable, Faculty, Library, Hostel, Placements, Contact)
- Popular queries panel and live notices feed
- Clear chat, Enter-to-send, no page reloads (AJAX/fetch)
- Friendly fallback message when no confident answer is found
- Fully responsive (desktop / tablet / mobile)

**Admin panel**
- Secure session-based login (hashed passwords, CSRF-protected mutations)
- Dashboard with FAQ/category/query/unanswered-query stats and recent queries
- Full FAQ CRUD with search + category filter
- Notice CRUD (create/edit/delete/activate)

**NLP engine**
- Text cleaning → normalization → tokenization → stopword removal → lemmatization → TF-IDF → cosine similarity → confidence threshold → fallback
- Reads FAQs live from the database, so admin edits take effect immediately with zero code changes

## 3. Technology Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | HTML5, CSS3, vanilla JavaScript (fetch/AJAX) |
| Backend   | Python 3, Flask, Flask blueprints |
| NLP       | scikit-learn (TF-IDF, cosine similarity), NLTK (tokenizing, stopwords, lemmatization) |
| Database  | SQLite via Flask-SQLAlchemy |
| Auth      | Session-based admin auth, Werkzeug password hashing, custom CSRF token |

No paid APIs, no Docker, no cloud infrastructure required. Runs 100% locally after `pip install`.

## 4. Architecture

```
Browser (student)  ──fetch──▶  Flask routes (chat.py)  ──▶  response_engine.py
                                                                   │
                                                          nlp_engine.py (TF-IDF)
                                                                   │
                                                          FAQ table (SQLite)

Browser (admin)  ──fetch──▶  Flask routes (admin.py / faq.py / dashboard.py)
                                                                   │
                                                        SQLAlchemy models (SQLite)
```

- **`chatbot/nlp_engine.py`** — pure NLP logic (no Flask/DB imports): cleaning, TF-IDF, cosine similarity.
- **`chatbot/response_engine.py`** — glues NLP to the database: loads FAQs, applies the confidence threshold, logs chat history.
- **`routes/*.py`** — Flask blueprints exposing the REST API and server-rendered admin pages.
- **`models/*.py`** — one file per SQLAlchemy model.
- **`templates/` + `static/`** — student UI (`index.html`) and admin UI (`templates/admin/*`).

## 5. Folder Structure

```
AI-College-Chatbot/
├── app.py                     # App factory, blueprint registration, error handlers
├── config.py                  # Config from environment variables
├── extensions.py              # Shared `db = SQLAlchemy()` instance
├── requirements.txt
├── .env.example
├── README.md
│
├── chatbot/
│   ├── nlp_engine.py           # TF-IDF + cosine similarity pipeline
│   └── response_engine.py      # DB-aware wrapper + chat history logging
│
├── models/
│   ├── admin.py | faq.py | chat_history.py | notice.py | college_info.py
│
├── routes/
│   ├── chat.py      # /api/chat, /api/categories, /api/notices, /api/chat-history
│   ├── admin.py      # /api/admin/login|logout + admin page routes
│   ├── faq.py         # /api/faqs CRUD
│   └── dashboard.py   # /api/dashboard/stats
│
├── templates/
│   ├── index.html
│   └── admin/ (login.html, dashboard.html, faqs.html, notices.html, _sidebar.html)
│
├── static/
│   ├── css/ (style.css, admin.css)
│   └── js/ (chat.js, admin.js)
│
├── data/
│   └── sample_faqs.json        # 70+ DEMO FAQs — replace before deployment
│
├── database/
│   └── college.db              # created automatically on first run
│
└── scripts/
    └── seed_database.py        # creates tables, admin user, sample data
```

## 6. Installation (Windows + VS Code)

**Step 1 — Open the project folder in VS Code**, then open a terminal (`` Ctrl+` ``).

**Step 2 — Create and activate a virtual environment**
```
python -m venv venv
venv\Scripts\activate
```
Your terminal prompt should now show `(venv)`.

**Step 3 — Install dependencies**
```
pip install -r requirements.txt
```

**Step 4 — Configure environment variables**
```
copy .env.example .env
```
Open `.env` and adjust `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` if you like (defaults work fine for a demo).

**Step 5 — Seed the database**
```
python scripts\seed_database.py
```
This creates `database/college.db`, a default admin account, ~70 sample FAQs, sample notices, and sample college info. Safe to re-run — it skips anything that already exists.

**Step 6 — Run the app**
```
python app.py
```

**Step 7 — Open in your browser**
- Student chatbot: `http://127.0.0.1:5000`
- Admin panel: `http://127.0.0.1:5000/admin` (default login: `admin` / `admin123`, unless changed in `.env`)

> ⚠️ **Change the default admin password** after your first login/demo, and never commit `.env` to version control.

## 7. How to Modify FAQs

Two ways:
1. **Admin panel (recommended):** log in at `/admin`, go to *Manage FAQs*, and Add/Edit/Delete. Changes apply to the chatbot immediately — no restart needed, because `response_engine.load_faqs()` queries the database fresh on every chat request.
2. **Bulk edit:** update `data/sample_faqs.json` and re-run `python scripts/seed_database.py` on a **fresh** database (delete `database/college.db` first, since the seed script skips FAQs if any already exist).

## 8. How the NLP Algorithm Works

1. **Text Cleaning** — lowercase, strip punctuation.
2. **Tokenization** — split into words (NLTK `word_tokenize`, with a lightweight fallback if NLTK data isn't available).
3. **Stopword Removal** — remove common words like "is", "the", "how" that carry no topic meaning.
4. **Lemmatization** — reduce words to their base form (e.g. "fees" → "fee") so different word forms match.
5. **TF-IDF Vectorization** — convert the user's question and every stored FAQ question+keywords into numeric vectors, where rarer/more distinctive words get more weight.
6. **Cosine Similarity** — measure the angle between the user's vector and every FAQ vector; a score closer to 1 means a closer topic match.
7. **Confidence Threshold** — if the best score is below `SIMILARITY_THRESHOLD` (default `0.20`, configurable in `.env`), the bot returns a fallback message instead of guessing.

This lives in `chatbot/nlp_engine.py` (algorithm) and `chatbot/response_engine.py` (database integration + logging).

## 9. API Documentation

All responses are JSON: `{"success": true/false, "data": ..., "error": "..."}`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/chat` | — | Ask the chatbot a question |
| GET | `/api/categories` | — | List distinct FAQ categories |
| GET | `/api/notices` | — | List active notices |
| POST/PUT/DELETE | `/api/notices[/:id]` | admin + CSRF | Manage notices |
| GET | `/api/chat-history` | admin | Recent logged chat interactions |
| GET/POST | `/api/faqs` | admin (POST needs CSRF) | List / create FAQs (supports `?search=` `&category=`) |
| GET/PUT/DELETE | `/api/faqs/:id` | admin (PUT/DELETE need CSRF) | Get / update / delete one FAQ |
| GET | `/api/dashboard/stats` | admin | Dashboard statistics |
| POST | `/api/admin/login` | — | Log in, returns a CSRF token |
| POST | `/api/admin/logout` | admin | Log out |

Admin-only endpoints require an active session (log in via `/admin`) and, for POST/PUT/DELETE, an `X-CSRF-Token` header matching the token issued at login.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on run | Make sure the venv is activated (`venv\Scripts\activate`) and you ran `pip install -r requirements.txt` |
| Chatbot always gives the fallback answer | Lower `SIMILARITY_THRESHOLD` in `.env` (e.g. `0.15`), or check `database/college.db` actually has FAQs (`python scripts/seed_database.py`) |
| Admin login fails | Confirm `.env` `ADMIN_USERNAME`/`ADMIN_PASSWORD` match what you seeded with; re-run the seed script on a fresh DB if unsure |
| "Invalid or missing CSRF token" | Your admin session may have expired — log out and log back in |
| NLTK download errors on first run | The app automatically falls back to a simpler built-in tokenizer/stemmer if NLTK data can't be downloaded (e.g. no internet) — the chatbot still works |
| Port 5000 already in use | Stop the other process, or run `app.run(port=5001)` in `app.py` |

## 11. Future Scope

- Hindi + English bilingual support
- Voice input/output
- Optional LLM API integration for open-ended questions
- WhatsApp / college-website widget integration
- Personalized student login and admission-status tracking
- Document upload and richer analytics dashboard

---

See **`VIVA_GUIDE.md`** for a plain-language explanation guide for your presentation/viva, and **`TEAM_RESPONSIBILITIES.md`** for the suggested division of work.
