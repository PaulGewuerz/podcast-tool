"""Tests for the pipeline orchestrator."""

from pathlib import Path

import pytest
from pydub import AudioSegment

from localpod.pipeline import run


@pytest.fixture
def test_env(tmp_path, monkeypatch):
    """Set up a complete test environment with assets and config."""
    monkeypatch.setenv("LOCALPOD_TEST_MODE", "true")

    # Create asset files
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    silence = AudioSegment.silent(duration=1000)
    silence.export(str(assets_dir / "intro.mp3"), format="mp3")
    silence.export(str(assets_dir / "outro.mp3"), format="mp3")

    output_dir = tmp_path / "output"

    # Reload config with our temp paths
    import importlib
    from localpod import config
    importlib.reload(config)
    monkeypatch.setattr(config, "ASSETS_DIR", assets_dir)
    monkeypatch.setattr(config, "OUTPUT_DIR", output_dir)

    return {"assets": assets_dir, "output": output_dir}


class TestPipeline:
    def test_full_run_with_text(self, test_env):
        result = run(
            title="Test Episode",
            text="This is a sample article for the podcast.",
            skip_publish=False,
        )

        assert result["text"] is not None
        assert result["narration"].exists()
        assert result["episode"].exists()
        assert result["url"] is not None  # Test mode returns a fake URL

    def test_skip_publish(self, test_env):
        result = run(
            title="No-Publish Test",
            text="Content that won't be published.",
            skip_publish=True,
        )

        assert result["episode"].exists()
        assert result["url"] is None

    def test_requires_text_or_url(self, test_env):
        with pytest.raises(ValueError, match="Provide either text= or url="):
            run(title="Bad Input")
