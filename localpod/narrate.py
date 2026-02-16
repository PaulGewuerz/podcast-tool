"""
Narration module — converts text to speech audio.

In live mode:  calls the ElevenLabs API.
In test mode:  generates a short silent MP3 so you can test the
               rest of the pipeline without burning API credits.

Usage:
    audio_path = narrate(text, output_path=Path("output/narration.mp3"))
"""

from pathlib import Path

import requests

from localpod import config


def narrate(text: str, output_path: Path) -> Path:
    """Convert *text* to an MP3 file at *output_path*.

    Returns the path to the written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if config.TEST_MODE:
        return _narrate_test(text, output_path)
    return _narrate_elevenlabs(text, output_path)


# ---------------------------------------------------------------------------
# Live implementation — ElevenLabs TTS
# ---------------------------------------------------------------------------

def _narrate_elevenlabs(text: str, output_path: Path) -> Path:
    """Call the ElevenLabs text-to-speech API and save the result."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": config.ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()

    output_path.write_bytes(response.content)
    return output_path


# ---------------------------------------------------------------------------
# Test stub — generates a tiny valid MP3 so downstream modules work
# ---------------------------------------------------------------------------

# Minimal valid MP3 frame (silence, ~0.026 seconds).
# This avoids needing ffmpeg or pydub just to create a test file.
_SILENT_MP3_FRAME = (
    b"\xff\xfb\x90\x00"  # MPEG1 Layer3 header
    + b"\x00" * 413       # padded silent frame
)


def _narrate_test(text: str, output_path: Path) -> Path:
    """Write a short silent MP3 instead of calling the API.

    Prints the first 80 characters of the text so you can confirm
    the right content reached this stage.
    """
    preview = text[:80].replace("\n", " ")
    print(f"[TEST MODE] Narration skipped. Text preview: \"{preview}...\"")

    # Write enough frames to be recognized as audio (~1 second)
    output_path.write_bytes(_SILENT_MP3_FRAME * 40)
    return output_path
