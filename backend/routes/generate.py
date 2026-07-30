# backend/routes/generate.py
#
# Blueprint that exposes:
#
#   POST /generate
#
# Request body (JSON):
#   {
#     "idea":     "<content idea>",
#     "platform": "<Instagram | TikTok | LinkedIn | YouTube Shorts>",
#     "tone":     "<Professional | Fun | Cute | Inspirational | Informative>"
#   }
#
# Success response (200):
#   {
#     "caption":       "...",
#     "script":        "...",
#     "hashtags":      "...",
#     "visualConcept": "...",
#     "callToAction":  "..."
#   }
#
# Error response (400 | 500):
#   { "error": "<human-readable message>" }

from __future__ import annotations

import logging
import os

from flask import Blueprint, jsonify, request

from models.request_models import GenerateRequest
from services.generator import generate_content, _is_demo_mode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint definition
# ---------------------------------------------------------------------------

generate_bp = Blueprint("generate", __name__)


# ---------------------------------------------------------------------------
# POST /generate
# ---------------------------------------------------------------------------

@generate_bp.route("/generate", methods=["POST"])
def generate() -> tuple:
    """Generate social-media content from a single idea.

    Validates the incoming JSON body, delegates to the generation service,
    and returns a structured JSON response.  The generation service is
    backend-agnostic: it uses a built-in stub by default and transparently
    switches to IBM watsonx.ai / Granite once credentials are configured.

    Returns:
        ``200`` with the generated content dict on success.
        ``400`` with ``{"error": "..."}`` for invalid input.
        ``500`` with ``{"error": "..."}`` for unexpected server errors.
    """
    # ── 1. Parse request body ─────────────────────────────────────────────
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    # ── 2. Validate & construct the request model ─────────────────────────
    try:
        gen_request = GenerateRequest.from_dict(body)
    except ValueError as exc:
        logger.warning("Invalid request: %s", exc)
        return jsonify({"error": str(exc)}), 400

    # ── 3. Generate content ───────────────────────────────────────────────
    try:
        result = generate_content(gen_request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Generation failed: %s", exc)
        return jsonify({"error": "Content generation failed. Please try again."}), 500

    # ── 4. Return result ──────────────────────────────────────────────────
    mode = "demo" if _is_demo_mode() else "ai"
    logger.info(
        "Generated content | mode=%s platform=%s tone=%s idea_len=%d",
        mode,
        gen_request.platform,
        gen_request.tone,
        len(gen_request.idea),
    )
    return jsonify({**result, "_mode": mode}), 200
