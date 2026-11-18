"""
scripts/seed_database.py
=========================
Run this once after installing dependencies to:
    1. Create all database tables (if they don't already exist)
    2. Create a default admin account (from .env / config.py)
    3. Load the sample FAQ dataset from data/sample_faqs.json
    4. Load a few sample notices and college info entries

Usage (Windows):
    venv\\Scripts\\activate
    python scripts/seed_database.py

Safe to re-run: it will not create duplicate FAQs/notices/admin accounts
if they already exist.
"""
import os
import sys
import json

# Allow running this script directly (python scripts/seed_database.py)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models.admin import Admin
from models.faq import FAQ
from models.notice import Notice
from models.college_info import CollegeInfo
from config import Config

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAQ_JSON_PATH = os.path.join(BASE_DIR, "data", "sample_faqs.json")


def seed_admin():
    existing = Admin.query.filter_by(username=Config.ADMIN_USERNAME).first()
    if existing:
        print(f"[skip] Admin '{Config.ADMIN_USERNAME}' already exists.")
        return

    admin = Admin(username=Config.ADMIN_USERNAME)
    admin.set_password(Config.ADMIN_PASSWORD)
    db.session.add(admin)
    db.session.commit()
    print(f"[ok]   Created admin user '{Config.ADMIN_USERNAME}' "
          f"with password '{Config.ADMIN_PASSWORD}' (change this after first login!).")


def seed_faqs():
    if FAQ.query.count() > 0:
        print(f"[skip] FAQs already exist ({FAQ.query.count()} rows). Skipping FAQ seed.")
        return

    if not os.path.exists(FAQ_JSON_PATH):
        print(f"[warn] Sample FAQ file not found at {FAQ_JSON_PATH}")
        return

    with open(FAQ_JSON_PATH, "r", encoding="utf-8") as f:
        faq_data = json.load(f)

    for item in faq_data:
        faq = FAQ(
            question=item["question"],
            answer=item["answer"],
            category=item["category"],
            keywords=item.get("keywords", ""),
        )
        db.session.add(faq)

    db.session.commit()
    print(f"[ok]   Inserted {len(faq_data)} sample FAQs "
          f"(DEMO DATA - replace with real college information before deployment).")


def seed_notices():
    if Notice.query.count() > 0:
        print(f"[skip] Notices already exist. Skipping notice seed.")
        return

    sample_notices = [
        {
            "title": "[DEMO] Welcome to the New Academic Year",
            "content": "This is sample/demo notice data. Replace it with your college's real "
                       "announcements from the Admin Panel before going live.",
        },
        {
            "title": "[DEMO] Semester Exam Schedule Released",
            "content": "The semester exam timetable has been published on the notice board. "
                       "(Sample notice - update with real exam dates.)",
        },
        {
            "title": "[DEMO] Annual Technical Fest Registrations Open",
            "content": "Registrations for the annual technical fest are now open. "
                       "(Sample notice - update with real event details.)",
        },
    ]
    for item in sample_notices:
        db.session.add(Notice(title=item["title"], content=item["content"], active=True))

    db.session.commit()
    print(f"[ok]   Inserted {len(sample_notices)} sample notices (DEMO DATA).")


def seed_college_info():
    if CollegeInfo.query.count() > 0:
        print(f"[skip] College info already exists. Skipping.")
        return

    sample_info = [
        {
            "category": "About",
            "title": "About the College [DEMO]",
            "content": "This is placeholder/demo text describing the college. "
                       "Replace with your actual college profile from the Admin Panel.",
        },
        {
            "category": "Contact",
            "title": "Contact Details [DEMO]",
            "content": "Address: [Add real address] | Phone: [Add real phone] | "
                       "Email: [Add real email]. Replace with actual contact information.",
        },
    ]
    for item in sample_info:
        db.session.add(CollegeInfo(category=item["category"], title=item["title"], content=item["content"]))

    db.session.commit()
    print(f"[ok]   Inserted {len(sample_info)} sample college info entries (DEMO DATA).")


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("=" * 60)
        print("Seeding AI College Chatbot database...")
        print("=" * 60)
        seed_admin()
        seed_faqs()
        seed_notices()
        seed_college_info()
        print("=" * 60)
        print("Done! You can now run: python app.py")
        print("=" * 60)


if __name__ == "__main__":
    main()
