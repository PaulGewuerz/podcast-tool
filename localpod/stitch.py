"""
Stitcher module — assembles the final podcast episode.

Combines:  intro.mp3  +  narration.mp3  +  outro.mp3
Output:    a single MP3 file ready for publishing.

Requires ffmpeg to be installed on the system (pydub uses it
under the hood).

Usage:
    final = stitch(
        narration_path=Path("output/narration.mp3"),
        output_path=Path("output/episode.mp3"),
    )
"""

from pathlib import Path

from pydub import AudioSegment

from localpod import config


# Short crossfade between segments (milliseconds).
# Keeps transitions smooth without cutting off words.
_CROSSFADE_MS = 500


def stitch(narration_path: Path, output_path: Path) -> Path:
    """Combine intro + narration + outro into one MP3 at *output_path*.

    Returns the path to the final file.
    """
    intro_path = config.ASSETS_DIR / "intro.mp3"
    outro_path = config.ASSETS_DIR / "outro.mp3"

    # Load each segment
    intro = AudioSegment.from_mp3(str(intro_path))
    narration = AudioSegment.from_mp3(str(narration_path))
    outro = AudioSegment.from_mp3(str(outro_path))

    # Combine with short crossfades
    combined = intro.append(narration, crossfade=_CROSSFADE_MS)
    combined = combined.append(outro, crossfade=_CROSSFADE_MS)

    # Export final episode
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(output_path), format="mp3")

    print(f"Stitched episode: {output_path}  "
          f"(duration: {len(combined) / 1000:.1f}s)")
    return output_path
