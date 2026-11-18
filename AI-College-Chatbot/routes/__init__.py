"""
Routes package - shared helpers used across multiple blueprints.
"""
import secrets
from functools import wraps
from flask import session, jsonify, request


def login_required(view_func):
    """Decorator that blocks access unless an admin is logged in (session-based)."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return jsonify({"success": False, "error": "Authentication required. Please log in."}), 401
        return view_func(*args, **kwargs)

    return wrapped


def csrf_protect(view_func):
    """
    Very lightweight CSRF protection for state-changing admin requests.
    A token is issued at login time (see routes/admin.py) and stored in
    the session. The frontend must send it back in the X-CSRF-Token
    header for every POST / PUT / DELETE request.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if request.method in ("POST", "PUT", "DELETE"):
            token = request.headers.get("X-CSRF-Token")
            if not token or token != session.get("csrf_token"):
                return jsonify({"success": False, "error": "Invalid or missing CSRF token."}), 403
        return view_func(*args, **kwargs)

    return wrapped


def generate_csrf_token():
    return secrets.token_hex(16)
