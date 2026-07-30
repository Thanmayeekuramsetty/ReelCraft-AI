# backend/services/generator.py
#
# Content-generation service for ReelCraft AI.
#
# ┌──────────────────────────────────────────────────────────────────────────┐
# │  How mode selection works                                                │
# │                                                                          │
# │  DEMO_MODE=true  (or unset)  →  generate_demo()   — instant, no creds   │
# │  DEMO_MODE=false             →  generate_with_ai() — IBM watsonx/Granite │
# │                                                                          │
# │  The public entry point generate_content() reads DEMO_MODE and calls    │
# │  the right function automatically.  Both functions share the same        │
# │  return shape so the route layer never needs to change.                  │
# │                                                                          │
# │  Return shape (all five keys always present):                            │
# │    caption, videoScript, hashtags, visualConcept, callToAction           │
# │                                                                          │
# │  To activate the live Granite model:                                     │
# │    1. pip install ibm-watsonx-ai  (already in requirements.txt)          │
# │    2. Copy .env.example → .env and fill in your IBM credentials.         │
# │    3. Set DEMO_MODE=false in .env.                                        │
# │    4. Restart the server.  No other code changes are required.           │
# └──────────────────────────────────────────────────────────────────────────┘

from __future__ import annotations

import json
import logging
import os
import re
import textwrap

from models.request_models import GenerateRequest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_demo_mode() -> bool:
    """Return True when DEMO_MODE is unset, empty, or the string 'true'.

    Any value other than the exact string ``"false"`` (case-insensitive)
    keeps the app in safe demo mode, so a misconfigured environment can
    never accidentally skip the AI call silently — it simply stays on demo.
    """
    return os.getenv("DEMO_MODE", "true").strip().lower() != "false"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_content(req: GenerateRequest) -> dict:
    """Dispatch to the correct back-end based on the DEMO_MODE env var.

    Args:
        req: A validated :class:`~models.GenerateRequest` instance.

    Returns:
        Dict with keys: ``caption``, ``videoScript``, ``hashtags``,
        ``visualConcept``, ``callToAction``.

    Raises:
        RuntimeError: Propagated from :func:`generate_with_ai` on
            unrecoverable watsonx errors (after safe-parse fallback).
    """
    if _is_demo_mode():
        logger.info("[generator] DEMO_MODE=true — using demo content")
        return generate_demo(req)

    logger.info(
        "[generator] DEMO_MODE=false — calling watsonx (model=%s)",
        os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-3-8b-instruct"),
    )
    return generate_with_ai(req)


# ---------------------------------------------------------------------------
# Demo back-end  ── deterministic, no external calls
# ---------------------------------------------------------------------------

def generate_demo(req: GenerateRequest) -> dict:
    """Return template-based placeholder content without any AI call.

    This function is the safe default. It is always available, requires no
    credentials, and produces structurally valid output so the frontend can
    render results immediately during development or when credentials are not
    yet configured.

    Args:
        req: Validated request containing ``idea``, ``platform``, ``tone``.

    Returns:
        Dict with the five content keys populated with placeholder strings.
    """
    idea        = req.idea
    platform    = req.platform
    tone        = req.tone
    tone_lower  = tone.lower()

    aspect_ratios = {
        "TikTok":          "9:16",
        "YouTube Shorts":  "9:16",
        "LinkedIn":        "1:1",
        "Instagram":       "4:5",
    }
    aspect = aspect_ratios.get(platform, "4:5")

    return {
        "caption": (
            f"A compelling {tone_lower} caption for {platform} about: \"{idea}\""
        ),
        "videoScript": textwrap.dedent(f"""\
            [Hook]   Start with an attention-grabbing opener related to: "{idea}".
            [Body]   Dive into the core message with a {tone_lower} tone.
            [Outro]  Wrap up with a memorable close tailored for {platform}."""),
        "hashtags": (
            f"#{platform.replace(' ', '')} #ContentCreator #AI "
            f"#{tone} #ReelCraftAI #Trending #ViralContent"
        ),
        "visualConcept": (
            f"Scene: Bright, clean setting. Use a {tone_lower} colour palette — "
            f"warm tones for energy. Show the subject prominently with minimal "
            f"background clutter. Overlay animated text matching the caption. "
            f"Aspect ratio: {aspect}."
        ),
        "callToAction": (
            f"Follow for more {tone_lower} {platform} content! "
            f"Drop a 🔥 if this resonated with you, and share with someone "
            f"who needs to see this."
        ),
    }


# ---------------------------------------------------------------------------
# AI back-end  ── IBM watsonx.ai with IBM Granite
# ---------------------------------------------------------------------------
def _build_json_prompt(req: GenerateRequest) -> str:
    """Build a structured JSON-output prompt for IBM Granite."""
    return textwrap.dedent(f"""\
        You are ReelCraft AI, an expert social-media content creator.

        Generate polished, ready-to-publish social-media content for the brief below.

        Return ONLY one valid JSON object.
        Do not include markdown fences.
        Do not include commentary before or after the JSON.
        Do not return nested objects, lists, or Python dictionaries.
        Every value must be a plain string.

        Brief:
          Idea:     {req.idea}
          Platform: {req.platform}
          Tone:     {req.tone}

        Important rules:
        - Do not use placeholders such as [ShopName], [Product], [Bonus], [Brand], or [Location].
        - When specific details are missing, create natural and realistic details.
        - Keep the content appropriate for the selected platform and tone.
        - Do not repeat the same hashtags inside the caption and hashtags field unless natural.
        - The videoScript must be one plain string.
        - Format the videoScript using exactly these labels:
          [Hook]
          [Body]
          [Outro]
        - Do not return the videoScript as a dictionary or object.
        - Hashtags must be written as one space-separated string.
        - Ensure all JSON quotes and special characters are properly escaped.

        Required JSON schema:
        {{
          "caption": "<engaging caption, maximum 280 characters>",
          "videoScript": "[Hook] ... [Body] ... [Outro] ...",
          "hashtags": "#ExampleOne #ExampleTwo #ExampleThree",
          "visualConcept": "<brief description of the ideal visual or scene>",
          "callToAction": "<one strong call-to-action sentence>"
        }}

        JSON output:
    """)


# Expected keys in the model response
_REQUIRED_KEYS: tuple[str, ...] = (
    "caption",
    "videoScript",
    "hashtags",
    "visualConcept",
    "callToAction",
)


def _parse_json_response(raw: str, req: GenerateRequest) -> dict:
    """Safely extract the five content fields from a Granite text response.

    Parsing strategy (most-to-least strict):
      1. Parse the raw string directly as JSON.
      2. Strip common markdown code fences (```json … ```) and retry.
      3. Use a regex to extract the first ``{ … }`` block and retry.
      4. If all attempts fail, log a warning and return demo content so the
         caller always receives a structurally valid response.

    Args:
        raw: Raw text returned by the Granite model.
        req: Original request, used as fallback context.

    Returns:
        Dict with all five required keys guaranteed to be present.
    """
    def _try_parse(text: str) -> dict | None:
        try:
            data = json.loads(text)
            if isinstance(data, dict) and all(k in data for k in _REQUIRED_KEYS):
                return {k: str(data[k]).strip() for k in _REQUIRED_KEYS}
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    # ── Attempt 1: raw text ───────────────────────────────────────────────
    result = _try_parse(raw.strip())
    if result:
        logger.debug("[generator] JSON parsed on attempt 1 (raw)")
        return result

    # ── Attempt 2: strip markdown code fences ────────────────────────────
    stripped = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE).strip().rstrip("`").strip()
    result = _try_parse(stripped)
    if result:
        logger.debug("[generator] JSON parsed on attempt 2 (fence strip)")
        return result

    # ── Attempt 3: extract first {...} block ──────────────────────────────
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if match:
        result = _try_parse(match.group(0))
        if result:
            logger.debug("[generator] JSON parsed on attempt 3 (regex extract)")
            return result

    # ── Attempt 4: partial fill — use whatever keys parsed correctly ──────
    try:
        data = json.loads(stripped if match is None else match.group(0))
        if isinstance(data, dict):
            demo = generate_demo(req)
            # Overlay any valid keys from the model response onto demo output
            for k in _REQUIRED_KEYS:
                if k in data and isinstance(data[k], str) and data[k].strip():
                    demo[k] = data[k].strip()
            logger.warning(
                "[generator] Partial JSON parse — %d/%d keys recovered from model",
                sum(1 for k in _REQUIRED_KEYS if k in data),
                len(_REQUIRED_KEYS),
            )
            return demo
    except (json.JSONDecodeError, ValueError):
        pass

    # ── Fallback: demo content ─────────────────────────────────────────────
    logger.warning(
        "[generator] JSON parse failed entirely — falling back to demo content.\n"
        "Raw response (first 400 chars): %s",
        raw[:400],
    )
    return generate_demo(req)


def generate_with_ai(req: GenerateRequest) -> dict:
    """Call IBM watsonx.ai to generate content using the configured Granite model.

    Reads all configuration exclusively from environment variables so no
    credentials are ever present in the source code or exposed to the frontend.

    Environment variables (all required when DEMO_MODE=false):
        WATSONX_API_KEY    — IBM Cloud API key
        WATSONX_PROJECT_ID — watsonx.ai project ID
        WATSONX_URL        — regional endpoint, e.g. https://us-south.ml.cloud.ibm.com
        WATSONX_MODEL_ID   — model to invoke, e.g. ibm/granite-3-3-8b-instruct

    Optional tuning variables:
        WATSONX_MAX_TOKENS   — maximum new tokens (default: 600)
        WATSONX_TEMPERATURE  — sampling temperature (default: 0.7)

    Args:
        req: Validated request containing ``idea``, ``platform``, ``tone``.

    Returns:
        Dict with the five content keys.  Falls back to demo content on any
        error so the endpoint always returns a 200 rather than a 500.

    Raises:
        RuntimeError: Only if ``ibm-watsonx-ai`` is not installed.
    """
    # ── Guard: ensure SDK is available ───────────────────────────────────
    try:
        from ibm_watsonx_ai import Credentials                         # noqa: PLC0415
        from ibm_watsonx_ai.foundation_models import ModelInference    # noqa: PLC0415
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "ibm-watsonx-ai is not installed. "
            "Run: pip install ibm-watsonx-ai"
        ) from exc

    # ── Guard: ensure credentials are present ────────────────────────────
    api_key    = os.getenv("WATSONX_API_KEY", "").strip()
    project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
    url        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").strip()
    model_id   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-3-8b-instruct").strip()

    if not api_key or api_key == "your_ibm_cloud_api_key_here":
        logger.error(
            "[generator] WATSONX_API_KEY is missing or placeholder — "
            "falling back to demo content."
        )
        return generate_demo(req)

    if not project_id or project_id == "your_watsonx_project_id_here":
        logger.error(
            "[generator] WATSONX_PROJECT_ID is missing or placeholder — "
            "falling back to demo content."
        )
        return generate_demo(req)

    # ── Build credentials & model client ─────────────────────────────────
    try:
        credentials = Credentials(url=url, api_key=api_key)

        params = {
            GenParams.MAX_NEW_TOKENS: int(os.getenv("WATSONX_MAX_TOKENS", "600")),
            GenParams.TEMPERATURE:    float(os.getenv("WATSONX_TEMPERATURE", "0.7")),
            GenParams.STOP_SEQUENCES: [],
        }

        model = ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=project_id,
            params=params,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("[generator] Failed to initialise watsonx client: %s", exc)
        return generate_demo(req)

    # ── Call the model ────────────────────────────────────────────────────
    try:
        prompt   = _build_json_prompt(req)
        raw_text = model.generate_text(prompt=prompt)
        logger.debug("[generator] Raw watsonx response: %s", raw_text[:200])
    except Exception as exc:  # noqa: BLE001
        logger.exception("[generator] watsonx inference call failed: %s", exc)
        return generate_demo(req)

    # ── Parse response ────────────────────────────────────────────────────
    return _parse_json_response(raw_text, req)
