# backend/app.py
#from flask_cors import CORS
# Flask application factory.
#
# Usage
# -----
# Development (auto-reload):
#   cd backend
#   python app.py
#
# Production (via gunicorn):
#   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
#
# Environment
# -----------
# Copy .env.example → .env and fill in your credentials before running.
# The app works without any credentials using stub output.

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

# Load .env file from the same directory as this file (backend/.env)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.DEBUG if os.getenv("FLASK_DEBUG", "0") == "1" else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    """Create and configure the Flask application.

    Separating construction into a factory makes the app testable
    (you can call ``create_app()`` in test fixtures) and lets gunicorn /
    uWSGI create workers independently.

    Returns:
        A fully configured :class:`Flask` instance.
    """
    app = Flask(__name__)
    CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    }
)

    # ── CORS ──────────────────────────────────────────────────────────────
    # In development the React dev-server runs on http://localhost:5173.
    # In production, restrict origins to your actual frontend domain.
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(app, origins=[o.strip() for o in allowed_origins])

    # ── Register blueprints ───────────────────────────────────────────────
    from routes.generate import generate_bp  # local import keeps factory clean
    app.register_blueprint(generate_bp)

    # ── Health-check endpoint ─────────────────────────────────────────────
    @app.get("/health")
    def health():
        """Lightweight liveness probe used by load-balancers and CI checks."""
        return jsonify({"status": "ok", "service": "reelcraft-ai-backend"}), 200

    # ── Generic 404 / 405 JSON handlers ──────────────────────────────────
    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_err):
        return jsonify({"error": "Method not allowed."}), 405

    return app


# ---------------------------------------------------------------------------
# Entry point (python app.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
