# backend/models/request_models.py
#
# Dataclasses that represent validated inbound request payloads.
# Using Python's built-in dataclasses keeps this dependency-free while
# still providing clear type hints and a single source of truth for the
# shape of every request body.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


# ---------------------------------------------------------------------------
# Allowed values — validated at request time so that callers get a clear
# 400 error instead of a silent mismatch inside the generation service.
# ---------------------------------------------------------------------------

ALLOWED_PLATFORMS: tuple[str, ...] = (
    "Instagram",
    "TikTok",
    "LinkedIn",
    "YouTube Shorts",
)

ALLOWED_TONES: tuple[str, ...] = (
    "Professional",
    "Fun",
    "Cute",
    "Inspirational",
    "Informative",
)


@dataclass
class GenerateRequest:
    """Validated payload for POST /generate.

    Attributes:
        idea:     The user's raw content idea.  1–2 000 characters.
        platform: Target social-media platform.  Must be in ALLOWED_PLATFORMS.
        tone:     Desired content tone.           Must be in ALLOWED_TONES.
    """

    idea: str
    platform: str
    tone: str

    # Maximum length accepted for the idea field
    MAX_IDEA_LENGTH: ClassVar[int] = 2_000

    # ------------------------------------------------------------------
    # Factory / validation
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "GenerateRequest":
        """Parse and validate a raw request dictionary.

        Args:
            data: Dictionary parsed from the JSON request body.

        Returns:
            A fully validated :class:`GenerateRequest` instance.

        Raises:
            ValueError: With a human-readable message if validation fails.
        """
        idea = (data.get("idea") or "").strip()
        platform = (data.get("platform") or "").strip()
        tone = (data.get("tone") or "").strip()

        if not idea:
            raise ValueError("'idea' is required and must not be empty.")
        if len(idea) > cls.MAX_IDEA_LENGTH:
            raise ValueError(
                f"'idea' exceeds the maximum length of {cls.MAX_IDEA_LENGTH} characters."
            )
        if platform not in ALLOWED_PLATFORMS:
            raise ValueError(
                f"'platform' must be one of: {', '.join(ALLOWED_PLATFORMS)}."
            )
        if tone not in ALLOWED_TONES:
            raise ValueError(
                f"'tone' must be one of: {', '.join(ALLOWED_TONES)}."
            )

        return cls(idea=idea, platform=platform, tone=tone)
