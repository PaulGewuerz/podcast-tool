"""
Publisher module — uploads a finished episode to Megaphone.fm.

In live mode:  uses the Megaphone REST API.
In test mode:  prints what *would* happen and returns a fake URL.

Megaphone API flow:
    1. Create a draft episode (POST /episodes)
    2. Upload the audio file to the episode
    3. (Optionally) schedule or publish it

Usage:
    url = publish(
        audio_path=Path("output/episode.mp3"),
        title="My Episode Title",
    )
"""

from pathlib import Path

import requests

from localpod import config


def publish(audio_path: Path, title: str, description: str = "") -> str:
    """Upload *audio_path* to Megaphone.fm and return the episode URL.

    Returns a URL string (real in live mode, fake in test mode).
    """
    if config.TEST_MODE:
        return _publish_test(audio_path, title)
    return _publish_megaphone(audio_path, title, description)


# ---------------------------------------------------------------------------
# Live implementation — Megaphone.fm API
# ---------------------------------------------------------------------------

_BASE_URL = "https://cms.megaphone.fm/api"


def _megaphone_headers() -> dict[str, str]:
    return {
        "Authorization": f"Token token={config.MEGAPHONE_API_TOKEN}",
        "Accept": "application/json",
    }


def _publish_megaphone(audio_path: Path, title: str, description: str) -> str:
    """Create a draft episode on Megaphone and upload audio to it."""

    # Step 1: Create episode draft
    create_url = (
        f"{_BASE_URL}/networks/{config.MEGAPHONE_NETWORK_ID}"
        f"/podcasts/{config.MEGAPHONE_PODCAST_ID}/episodes"
    )
    episode_data = {
        "title": title,
        "summary": description or title,
        "draft": True,  # Start as draft so you can review before going live
    }

    resp = requests.post(
        create_url,
        json=episode_data,
        headers=_megaphone_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    episode = resp.json()
    episode_id = episode["id"]

    # Step 2: Upload audio file
    upload_url = (
        f"{_BASE_URL}/networks/{config.MEGAPHONE_NETWORK_ID}"
        f"/podcasts/{config.MEGAPHONE_PODCAST_ID}"
        f"/episodes/{episode_id}/audio"
    )
    with open(audio_path, "rb") as f:
        upload_resp = requests.put(
            upload_url,
            data=f,
            headers={
                **_megaphone_headers(),
                "Content-Type": "audio/mpeg",
            },
            timeout=300,  # Audio uploads can be large
        )
    upload_resp.raise_for_status()

    episode_url = episode.get("externalUrl", f"https://megaphone.fm/episodes/{episode_id}")
    print(f"Published (draft): {episode_url}")
    return episode_url


# ---------------------------------------------------------------------------
# Test stub
# ---------------------------------------------------------------------------

def _publish_test(audio_path: Path, title: str) -> str:
    """Pretend to publish and return a fake URL."""
    print(f"[TEST MODE] Publish skipped.")
    print(f"  Title : {title}")
    print(f"  Audio : {audio_path}  ({audio_path.stat().st_size} bytes)")
    return "https://test.megaphone.fm/episodes/FAKE-EPISODE-ID"
