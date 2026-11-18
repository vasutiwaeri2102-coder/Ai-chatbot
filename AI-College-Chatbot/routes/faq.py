"""
routes/faq.py
==============
Full CRUD API for FAQs, used by the admin panel (templates/admin/faqs.html).
All endpoints require an authenticated admin session; mutating endpoints
also require a valid CSRF token.
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models.faq import FAQ
from routes import login_required, csrf_protect

faq_bp = Blueprint("faq", __name__, url_prefix="/api/faqs")


@faq_bp.route("", methods=["GET"])
@login_required
def list_faqs():
    """List FAQs, optionally filtered by category and/or a search term."""
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()

    query = FAQ.query
    if category and category.lower() != "all":
        query = query.filter(FAQ.category == category)
    if search:
        like_term = f"%{search}%"
        query = query.filter(
            db.or_(FAQ.question.ilike(like_term), FAQ.answer.ilike(like_term))
        )

    faqs = query.order_by(FAQ.category, FAQ.id).all()
    return jsonify({"success": True, "data": [f.to_dict() for f in faqs]}), 200


@faq_bp.route("/<int:faq_id>", methods=["GET"])
@login_required
def get_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"success": False, "error": "FAQ not found."}), 404
    return jsonify({"success": True, "data": faq.to_dict()}), 200


@faq_bp.route("", methods=["POST"])
@login_required
@csrf_protect
def create_faq():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    answer = (data.get("answer") or "").strip()
    category = (data.get("category") or "").strip()
    keywords = (data.get("keywords") or "").strip()

    if not question or not answer or not category:
        return jsonify({
            "success": False,
            "error": "'question', 'answer' and 'category' are required.",
        }), 400

    faq = FAQ(question=question, answer=answer, category=category, keywords=keywords)
    db.session.add(faq)
    db.session.commit()
    return jsonify({"success": True, "data": faq.to_dict()}), 201


@faq_bp.route("/<int:faq_id>", methods=["PUT"])
@login_required
@csrf_protect
def update_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"success": False, "error": "FAQ not found."}), 404

    data = request.get_json(silent=True) or {}
    if "question" in data and data["question"].strip():
        faq.question = data["question"].strip()
    if "answer" in data and data["answer"].strip():
        faq.answer = data["answer"].strip()
    if "category" in data and data["category"].strip():
        faq.category = data["category"].strip()
    if "keywords" in data:
        faq.keywords = (data.get("keywords") or "").strip()

    db.session.commit()
    return jsonify({"success": True, "data": faq.to_dict()}), 200


@faq_bp.route("/<int:faq_id>", methods=["DELETE"])
@login_required
@csrf_protect
def delete_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"success": False, "error": "FAQ not found."}), 404

    db.session.delete(faq)
    db.session.commit()
    return jsonify({"success": True, "message": "FAQ deleted."}), 200
