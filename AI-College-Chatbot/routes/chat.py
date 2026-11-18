"""
routes/chat.py
===============
Public-facing endpoints used by the student chat UI:

    POST /api/chat            - ask the chatbot a question
    GET  /api/categories      - list distinct FAQ categories (for sidebar buttons)
    GET  /api/notices         - list active notices
    GET  /api/chat-history    - (admin only) view logged chat interactions

Also includes admin-only management of notices, kept here since the
project structure only defines one blueprint file per admin.py/faq.py
and notices are conceptually close to the public chat/notice feed.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db
from models.faq import FAQ
from models.notice import Notice
from models.chat_history import ChatHistory
from chatbot.response_engine import get_response
from routes import login_required, csrf_protect

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Main chatbot endpoint. Accepts {"message": "..."} and returns an answer."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"success": False, "error": "Invalid JSON request body."}), 400

    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify({"success": False, "error": "'message' must be a string."}), 400

    try:
        result = get_response(message)
    except Exception:
        return jsonify({
            "success": False,
            "error": "Something went wrong while processing your question. Please try again."
        }), 500

    return jsonify({"success": True, "data": result}), 200


@chat_bp.route("/categories", methods=["GET"])
def categories():
    """Return the distinct list of FAQ categories, used to build sidebar/category buttons."""
    try:
        rows = db.session.query(FAQ.category).distinct().order_by(FAQ.category).all()
        category_list = [r[0] for r in rows]
        return jsonify({"success": True, "data": category_list}), 200
    except Exception:
        return jsonify({"success": False, "error": "Could not load categories."}), 500


@chat_bp.route("/notices", methods=["GET"])
def get_notices():
    """Return active notices for the public homepage."""
    try:
        notices = (
            Notice.query.filter_by(active=True)
            .order_by(Notice.date.desc())
            .limit(20)
            .all()
        )
        return jsonify({"success": True, "data": [n.to_dict() for n in notices]}), 200
    except Exception:
        return jsonify({"success": False, "error": "Could not load notices."}), 500


@chat_bp.route("/notices", methods=["POST"])
@login_required
@csrf_protect
def create_notice():
    """Admin: create a new notice."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return jsonify({"success": False, "error": "Both 'title' and 'content' are required."}), 400

    notice = Notice(title=title, content=content, active=bool(data.get("active", True)))
    db.session.add(notice)
    db.session.commit()
    return jsonify({"success": True, "data": notice.to_dict()}), 201


@chat_bp.route("/notices/<int:notice_id>", methods=["PUT"])
@login_required
@csrf_protect
def update_notice(notice_id):
    """Admin: update an existing notice."""
    notice = Notice.query.get(notice_id)
    if not notice:
        return jsonify({"success": False, "error": "Notice not found."}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        notice.title = (data.get("title") or "").strip() or notice.title
    if "content" in data:
        notice.content = (data.get("content") or "").strip() or notice.content
    if "active" in data:
        notice.active = bool(data.get("active"))
    notice.date = notice.date or datetime.utcnow()

    db.session.commit()
    return jsonify({"success": True, "data": notice.to_dict()}), 200


@chat_bp.route("/notices/<int:notice_id>", methods=["DELETE"])
@login_required
@csrf_protect
def delete_notice(notice_id):
    """Admin: delete a notice."""
    notice = Notice.query.get(notice_id)
    if not notice:
        return jsonify({"success": False, "error": "Notice not found."}), 404

    db.session.delete(notice)
    db.session.commit()
    return jsonify({"success": True, "message": "Notice deleted."}), 200


@chat_bp.route("/chat-history", methods=["GET"])
@login_required
def chat_history():
    """Admin: view recent chatbot interactions (for the dashboard)."""
    try:
        limit = min(int(request.args.get("limit", 50)), 200)
    except ValueError:
        limit = 50

    rows = ChatHistory.query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
    return jsonify({"success": True, "data": [r.to_dict() for r in rows]}), 200
