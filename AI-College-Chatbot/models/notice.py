from datetime import datetime
from extensions import db


class Notice(db.Model):
    """College notice / announcement shown to students."""

    __tablename__ = "notices"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "date": self.date.isoformat() if self.date else None,
            "active": self.active,
        }
