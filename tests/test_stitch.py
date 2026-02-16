"""Tests for the stitcher module."""

from pathlib import Path

import pytest
from pydub import AudioSegment

from localpod.stitch import stitch


@pytest.fixture
def audio_files(tmp_path, monkeypatch):
    """Create minimal MP3 files for intro, narration, and outro.

    Points the config ASSETS_DIR at our temp directory so stitch()
    can find intro.mp3 and outro.mp3.
    """
    # Generate 2-second silent audio segments
    silence = AudioSegment.silent(duration=2000)

    intro_path = tmp_path / "assets" / "intro.mp3"
    outro_path = tmp_path / "assets" / "outro.mp3"
    narration_path = tmp_path / "narration.mp3"

    intro_path.parent.mkdir(parents=True, exist_ok=True)
    silence.export(str(intro_path), format="mp3")
    silence.export(str(outro_path), format="mp3")
    silence.export(str(narration_path), format="mp3")

    # Point config to our temp assets directory
    import localpod.config as cfg
    monkeypatch.setattr(cfg, "ASSETS_DIR", tmp_path / "assets")

    return {
        "intro": intro_path,
        "outro": outro_path,
        "narration": narration_path,
    }


class TestStitch:
    def test_produces_output_file(self, audio_files, tmp_path):
        output = tmp_path / "output" / "episode.mp3"
        result = stitch(audio_files["narration"], output)

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_output_longer_than_any_input(self, audio_files, tmp_path):
        """The final episode should be longer than any single input segment."""
        output = tmp_path / "output" / "episode.mp3"
        stitch(audio_files["narration"], output)

        combined = AudioSegment.from_mp3(str(output))
        narration = AudioSegment.from_mp3(str(audio_files["narration"]))

        # Combined should be longer than narration alone
        # (even accounting for crossfade overlap)
        assert len(combined) > len(narration)
