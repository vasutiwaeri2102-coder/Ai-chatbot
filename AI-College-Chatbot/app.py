"""
app.py
======
Application entry point. Creates and configures the Flask app,
registers all blueprints, and creates database tables on first run.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""
import os
from flask import Flask, render_template, jsonify
from config import Config
from extensions import db

# Importing models registers them with SQLAlchemy metadata
import models  # noqa: F401


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the database/ folder exists before SQLite tries to create the file
    db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "database")
    os.makedirs(db_dir, exist_ok=True)

    db.init_app(app)

    # ---- Register blueprints -------------------------------------------------
    from routes.chat import chat_bp
    from routes.admin import admin_bp
    from routes.faq import faq_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(dashboard_bp)

    # ---- Public student-facing homepage --------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    # ---- Friendly error handlers ----------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        if "/api/" in (str(e.description) or "") or _wants_json():
            return jsonify({"success": False, "error": "Resource not found."}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request."}), 400

    with app.app_context():
        db.create_all()

    return app


def _wants_json():
    from flask import request
    return request.path.startswith("/api/")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
