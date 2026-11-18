"""
Shared Flask extension instances.
Kept in a separate module to avoid circular imports between
app.py, models/*, and routes/*.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
