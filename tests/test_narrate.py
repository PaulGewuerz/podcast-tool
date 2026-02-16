"""Tests for the narration module."""

import os
from pathlib import Path

import pytest


class TestNarrateTestMode:
    """Test narration in test mode (no API calls)."""

    def test_creates_mp3_file(self, tmp_path, monkeypatch):
        # Force test mode on
        monkeypatch.setenv("LOCALPOD_TEST_MODE", "true")

        # Re-import to pick up the env change
        import importlib
        from localpod import config
        importlib.reload(config)

        from localpod.narrate import narrate
        output = tmp_path / "narration.mp3"
        result = narrate("Hello world, this is a test.", output)

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_file_starts_with_mp3_sync(self, tmp_path, monkeypatch):
        """The generated file should start with an MP3 frame header."""
        monkeypatch.setenv("LOCALPOD_TEST_MODE", "true")

        import importlib
        from localpod import config
        importlib.reload(config)

        from localpod.narrate import narrate
        output = tmp_path / "test.mp3"
        narrate("Some text", output)

        data = output.read_bytes()
        # MP3 sync word: first 11 bits are 1
        assert data[0] == 0xFF
        assert (data[1] & 0xE0) == 0xE0


class TestNarrateLiveMode:
    """Test that live mode calls ElevenLabs correctly."""

    def test_calls_elevenlabs_api(self, tmp_path, monkeypatch, mocker):
        monkeypatch.setenv("LOCALPOD_TEST_MODE", "false")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice-123")

        import importlib
        from localpod import config
        importlib.reload(config)

        mock_resp = mocker.Mock()
        mock_resp.content = b"\xff\xfb\x90\x00" + b"\x00" * 100
        mock_resp.raise_for_status = mocker.Mock()
        mock_post = mocker.patch("localpod.narrate.requests.post", return_value=mock_resp)

        from localpod.narrate import narrate
        output = tmp_path / "narration.mp3"
        narrate("Test content", output)

        # Verify the API was called
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert "voice-123" in call_kwargs[0][0]  # URL contains voice ID
        assert output.exists()
