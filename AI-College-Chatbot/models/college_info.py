from datetime import datetime
from extensions import db


class CollegeInfo(db.Model):
    """General editable college information (about, address, timings, etc.)."""

    __tablename__ = "college_info"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
