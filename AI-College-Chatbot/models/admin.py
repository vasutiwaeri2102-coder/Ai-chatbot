from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class Admin(db.Model):
    """Admin user who can log in to the admin panel."""

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        """Hash and store a plain-text password. Never store passwords in plain text."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
