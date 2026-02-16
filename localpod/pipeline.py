"""
Pipeline module — orchestrates the full podcast production workflow.

    ingest → narrate → stitch → publish

Each step is a standalone module, and this file just wires them
together in sequence. You can also call each module directly
for debugging or partial runs.

Usage:
    from localpod.pipeline import run
    url = run(text="Article body here...", title="Episode Title")
"""

from pathlib import Path
from datetime import datetime

from localpod import config
from localpod.ingest import ingest_text, ingest_url
from localpod.narrate import narrate
from localpod.stitch import stitch
from localpod.publish import publish


def run(
    title: str,
    text: str | None = None,
    url: str | None = None,
    skip_publish: bool = False,
) -> dict:
    """Run the full pipeline and return a summary dict.

    Provide either *text* (pasted article body) or *url* (will be fetched).
    Set *skip_publish* to True if you just want the audio file without uploading.

    Returns a dict with keys:
        text       — the cleaned article text
        narration  — path to the narration MP3
        episode    — path to the final stitched MP3
        url        — published episode URL (or None if skipped)
    """
    if not text and not url:
        raise ValueError("Provide either text= or url=")

    # Timestamp for unique filenames
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = config.OUTPUT_DIR / stamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Ingest ------------------------------------------------
    print(f"\n{'='*50}")
    print("Step 1/4 — Ingesting content")
    print(f"{'='*50}")
    if url:
        print(f"Fetching: {url}")
        article_text = ingest_url(url)
    else:
        article_text = ingest_text(text)
    print(f"Got {len(article_text)} characters of text.")

    # --- Step 2: Narrate ------------------------------------------------
    print(f"\n{'='*50}")
    print("Step 2/4 — Generating narration")
    print(f"{'='*50}")
    narration_path = narrate(article_text, output_dir / "narration.mp3")
    print(f"Narration saved: {narration_path}")

    # --- Step 3: Stitch -------------------------------------------------
    print(f"\n{'='*50}")
    print("Step 3/4 — Stitching episode")
    print(f"{'='*50}")
    episode_path = stitch(narration_path, output_dir / "episode.mp3")

    # --- Step 4: Publish ------------------------------------------------
    episode_url = None
    if skip_publish:
        print(f"\n{'='*50}")
        print("Step 4/4 — Publishing (SKIPPED)")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print("Step 4/4 — Publishing to Megaphone")
        print(f"{'='*50}")
        episode_url = publish(episode_path, title=title)

    # --- Summary --------------------------------------------------------
    print(f"\n{'='*50}")
    print("Done!")
    print(f"{'='*50}")
    print(f"  Episode file: {episode_path}")
    if episode_url:
        print(f"  Published to: {episode_url}")

    return {
        "text": article_text,
        "narration": narration_path,
        "episode": episode_path,
        "url": episode_url,
    }
