"""
Configuration for LocalPod.

Loads settings from environment variables (or a .env file).
The TEST_MODE flag lets you run the full pipeline without
hitting external APIs or burning credits.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")


# ---------------------------------------------------------------------------
# Test mode — when True, API calls are replaced with local stubs
# ---------------------------------------------------------------------------
TEST_MODE: bool = os.getenv("LOCALPOD_TEST_MODE", "true").lower() in ("1", "true", "yes")

# ---------------------------------------------------------------------------
# ElevenLabs (text-to-speech)
# ---------------------------------------------------------------------------
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")

# ---------------------------------------------------------------------------
# Megaphone.fm (podcast hosting / publishing)
# ---------------------------------------------------------------------------
MEGAPHONE_API_TOKEN: str = os.getenv("MEGAPHONE_API_TOKEN", "")
MEGAPHONE_NETWORK_ID: str = os.getenv("MEGAPHONE_NETWORK_ID", "")
MEGAPHONE_PODCAST_ID: str = os.getenv("MEGAPHONE_PODCAST_ID", "")

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
# Directory containing intro.mp3 and outro.mp3
ASSETS_DIR: Path = Path(os.getenv("LOCALPOD_ASSETS_DIR", _project_root / "assets"))

# Where generated files are saved
OUTPUT_DIR: Path = Path(os.getenv("LOCALPOD_OUTPUT_DIR", _project_root / "output"))


def validate() -> list[str]:
    """Return a list of problems with the current config.

    Returns an empty list if everything looks good.
    """
    problems: list[str] = []

    if not TEST_MODE:
        # In live mode we need real API keys
        if not ELEVENLABS_API_KEY:
            problems.append("ELEVENLABS_API_KEY is not set")
        if not ELEVENLABS_VOICE_ID:
            problems.append("ELEVENLABS_VOICE_ID is not set")
        if not MEGAPHONE_API_TOKEN:
            problems.append("MEGAPHONE_API_TOKEN is not set")
        if not MEGAPHONE_NETWORK_ID:
            problems.append("MEGAPHONE_NETWORK_ID is not set")
        if not MEGAPHONE_PODCAST_ID:
            problems.append("MEGAPHONE_PODCAST_ID is not set")

    # Assets must exist regardless of mode
    intro = ASSETS_DIR / "intro.mp3"
    outro = ASSETS_DIR / "outro.mp3"
    if not intro.exists():
        problems.append(f"Intro file not found: {intro}")
    if not outro.exists():
        problems.append(f"Outro file not found: {outro}")

    return problems
