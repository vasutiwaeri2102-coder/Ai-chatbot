from datetime import datetime
from extensions import db


class ChatHistory(db.Model):
    """Log of every question asked to the chatbot, used for admin analytics."""

    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    user_question = db.Column(db.String(500), nullable=False)
    bot_answer = db.Column(db.Text, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False, default=0.0)
    matched_faq_id = db.Column(db.Integer, db.ForeignKey("faqs.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_question": self.user_question,
            "bot_answer": self.bot_answer,
            "similarity_score": round(self.similarity_score, 3),
            "matched_faq_id": self.matched_faq_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
