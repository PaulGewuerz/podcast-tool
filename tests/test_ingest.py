"""Tests for the ingest module."""

import pytest
from localpod.ingest import ingest_text, ingest_url


class TestIngestText:
    def test_strips_whitespace(self):
        raw = "  Hello world  \n\n  Second line  \n\n"
        result = ingest_text(raw)
        assert result == "Hello world\nSecond line"

    def test_removes_blank_lines(self):
        raw = "Line one\n\n\n\nLine two\n\n\nLine three"
        result = ingest_text(raw)
        assert result == "Line one\nLine two\nLine three"

    def test_empty_input(self):
        assert ingest_text("") == ""
        assert ingest_text("   \n\n  ") == ""


class TestIngestUrl:
    def test_extracts_article_text(self, mocker):
        """Mock requests.get so we don't hit the network."""
        html = """
        <html>
        <body>
            <nav>Menu stuff</nav>
            <article>
                <h1>Test Headline</h1>
                <p>First paragraph of the article.</p>
                <p>Second paragraph.</p>
            </article>
            <footer>Footer stuff</footer>
        </body>
        </html>
        """
        mock_resp = mocker.Mock()
        mock_resp.text = html
        mock_resp.raise_for_status = mocker.Mock()
        mocker.patch("localpod.ingest.requests.get", return_value=mock_resp)

        result = ingest_url("https://example.com/article")

        assert "First paragraph of the article." in result
        assert "Second paragraph." in result
        # Nav/footer should be stripped
        assert "Menu stuff" not in result
        assert "Footer stuff" not in result

    def test_falls_back_to_body(self, mocker):
        """When there's no <article> tag, use <body>."""
        html = "<html><body><p>Just body text.</p></body></html>"
        mock_resp = mocker.Mock()
        mock_resp.text = html
        mock_resp.raise_for_status = mocker.Mock()
        mocker.patch("localpod.ingest.requests.get", return_value=mock_resp)

        result = ingest_url("https://example.com/page")
        assert "Just body text." in result
