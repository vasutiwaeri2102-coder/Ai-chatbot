"""
Models package.
Importing this package registers all models with SQLAlchemy so that
db.create_all() (called from app.py) can create every table.
"""
from models.admin import Admin
from models.faq import FAQ
from models.chat_history import ChatHistory
from models.notice import Notice
from models.college_info import CollegeInfo

__all__ = ["Admin", "FAQ", "ChatHistory", "Notice", "CollegeInfo"]
