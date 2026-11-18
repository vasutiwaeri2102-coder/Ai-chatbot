"""
routes/admin.py
================
Admin authentication (login/logout) plus the server-rendered admin
pages (login screen, dashboard, FAQ manager, notice manager).
"""
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.admin import Admin
from routes import generate_csrf_token, login_required

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# JSON API - authentication
# ---------------------------------------------------------------------------

@admin_bp.route("/api/admin/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required."}), 400

    admin = Admin.query.filter_by(username=username).first()

    # Deliberately vague error message - never reveal whether the
    # username or the password was wrong.
    if not admin or not admin.check_password(password):
        return jsonify({"success": False, "error": "Invalid username or password."}), 401

    session.clear()
    session.permanent = True
    session["admin_id"] = admin.id
    session["admin_username"] = admin.username
    csrf_token = generate_csrf_token()
    session["csrf_token"] = csrf_token

    return jsonify({
        "success": True,
        "data": {"username": admin.username, "csrf_token": csrf_token},
    }), 200


@admin_bp.route("/api/admin/logout", methods=["POST"])
@login_required
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."}), 200


# ---------------------------------------------------------------------------
# Server-rendered admin pages
# ---------------------------------------------------------------------------

@admin_bp.route("/admin")
@admin_bp.route("/admin/login")
def admin_login_page():
    if session.get("admin_id"):
        return redirect(url_for("admin.admin_dashboard_page"))
    return render_template("admin/login.html")


@admin_bp.route("/admin/dashboard")
def admin_dashboard_page():
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login_page"))
    return render_template(
        "admin/dashboard.html",
        username=session.get("admin_username"),
        csrf_token=session.get("csrf_token", ""),
    )


@admin_bp.route("/admin/faqs")
def admin_faqs_page():
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login_page"))
    return render_template(
        "admin/faqs.html",
        username=session.get("admin_username"),
        csrf_token=session.get("csrf_token", ""),
    )


@admin_bp.route("/admin/notices")
def admin_notices_page():
    if not session.get("admin_id"):
        return redirect(url_for("admin.admin_login_page"))
    return render_template(
        "admin/notices.html",
        username=session.get("admin_username"),
        csrf_token=session.get("csrf_token", ""),
    )
