"""
Ingest module — accepts raw text or a URL and returns plain text
ready for narration.

Usage:
    text = ingest_text("Here is my article body ...")
    text = ingest_url("https://example.com/news/story")
"""

import requests
from bs4 import BeautifulSoup


def ingest_text(raw: str) -> str:
    """Clean up pasted text and return it ready for narration.

    Strips leading/trailing whitespace and collapses blank lines.
    """
    lines = raw.strip().splitlines()
    cleaned = "\n".join(line.strip() for line in lines if line.strip())
    return cleaned


def ingest_url(url: str) -> str:
    """Fetch a URL, extract the main article text, and return it.

    Uses BeautifulSoup to pull text from <article> tags first,
    then falls back to <body> if no <article> is found.
    """
    response = requests.get(url, timeout=30, headers={
        "User-Agent": "LocalPod/0.1 (podcast automation tool)"
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script/style elements that pollute text extraction
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Try <article> first — most news sites wrap content in one
    article = soup.find("article")
    if article:
        text = article.get_text(separator="\n")
    else:
        # Fall back to full body
        body = soup.find("body")
        text = body.get_text(separator="\n") if body else soup.get_text(separator="\n")

    return ingest_text(text)
