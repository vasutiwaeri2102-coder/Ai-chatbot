"""
routes/dashboard.py
====================
Admin dashboard statistics endpoint.
"""
from flask import Blueprint, jsonify
from extensions import db
from models.faq import FAQ
from models.chat_history import ChatHistory
from routes import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
@login_required
def stats():
    total_faqs = FAQ.query.count()
    total_categories = db.session.query(FAQ.category).distinct().count()
    total_queries = ChatHistory.query.count()
    unanswered_queries = ChatHistory.query.filter(
        ChatHistory.matched_faq_id.is_(None)
    ).count()

    recent = (
        ChatHistory.query.order_by(ChatHistory.created_at.desc()).limit(10).all()
    )

    return jsonify({
        "success": True,
        "data": {
            "total_faqs": total_faqs,
            "total_categories": total_categories,
            "total_queries": total_queries,
            "unanswered_queries": unanswered_queries,
            "recent_queries": [r.to_dict() for r in recent],
        },
    }), 200
