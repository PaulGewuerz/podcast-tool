"""Tests for the publisher module."""

from pathlib import Path

import pytest


class TestPublishTestMode:
    def test_returns_fake_url(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LOCALPOD_TEST_MODE", "true")

        import importlib
        from localpod import config
        importlib.reload(config)

        from localpod.publish import publish

        # Create a dummy audio file
        audio = tmp_path / "episode.mp3"
        audio.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 100)

        url = publish(audio, title="Test Episode")

        assert "FAKE-EPISODE-ID" in url
        assert url.startswith("https://")


class TestPublishLiveMode:
    def test_calls_megaphone_api(self, tmp_path, monkeypatch, mocker):
        monkeypatch.setenv("LOCALPOD_TEST_MODE", "false")
        monkeypatch.setenv("MEGAPHONE_API_TOKEN", "test-token")
        monkeypatch.setenv("MEGAPHONE_NETWORK_ID", "net-123")
        monkeypatch.setenv("MEGAPHONE_PODCAST_ID", "pod-456")

        import importlib
        from localpod import config
        importlib.reload(config)

        # Mock the POST (create episode) and PUT (upload audio) calls
        mock_create_resp = mocker.Mock()
        mock_create_resp.json.return_value = {
            "id": "ep-789",
            "externalUrl": "https://megaphone.fm/episodes/ep-789",
        }
        mock_create_resp.raise_for_status = mocker.Mock()

        mock_upload_resp = mocker.Mock()
        mock_upload_resp.raise_for_status = mocker.Mock()

        mock_post = mocker.patch("localpod.publish.requests.post", return_value=mock_create_resp)
        mock_put = mocker.patch("localpod.publish.requests.put", return_value=mock_upload_resp)

        from localpod.publish import publish

        audio = tmp_path / "episode.mp3"
        audio.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 100)

        url = publish(audio, title="Live Test Episode")

        assert url == "https://megaphone.fm/episodes/ep-789"
        mock_post.assert_called_once()
        mock_put.assert_called_once()
