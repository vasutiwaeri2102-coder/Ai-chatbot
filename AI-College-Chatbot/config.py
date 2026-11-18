"""
Application configuration.
Reads values from environment variables (see .env.example).
"""
import os
from dotenv import load_dotenv

# Load variables from a .env file if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key used for sessions / CSRF tokens
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Database
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database", "college.db")
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default admin credentials used ONLY by scripts/seed_database.py
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    # NLP matching
    SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.20"))

    # Session
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 2  # 2 hours
