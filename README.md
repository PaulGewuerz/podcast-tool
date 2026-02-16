# LocalPod

Automated podcast production tool for local news publishers. Converts articles into narrated podcast episodes and publishes them to Megaphone.fm.

## Pipeline

```
Article (text or URL) → ElevenLabs TTS → Stitch with intro/outro → Publish to Megaphone
```

## Setup

**Requirements:** Python 3.10+, ffmpeg

```bash
# Install ffmpeg (needed by pydub for audio processing)
# macOS:   brew install ffmpeg
# Ubuntu:  sudo apt install ffmpeg

# Install Python dependencies
pip install -e ".[dev]"

# Copy and edit config
cp .env.example .env
```

**Assets:** Place your `intro.mp3` and `outro.mp3` files in the `assets/` directory.

## Usage

```bash
# Check your config is valid
python cli.py --check-config

# Produce an episode from pasted text (test mode by default)
python cli.py --title "Episode Title" --text "Article body goes here..."

# Produce an episode from a URL
python cli.py --title "Episode Title" --url https://example.com/article

# Generate audio without publishing
python cli.py --title "Episode Title" --text "..." --skip-publish
```

## Test Mode

Test mode is **on by default** (`LOCALPOD_TEST_MODE=true`). It replaces API calls with local stubs so you can run the full pipeline without burning credits. Set `LOCALPOD_TEST_MODE=false` in your `.env` when you're ready to go live.

## Running Tests

```bash
pytest
```

## Project Structure

```
cli.py                  CLI entry point
localpod/
  config.py             Settings from environment variables
  ingest.py             Text and URL content extraction
  narrate.py            ElevenLabs text-to-speech
  stitch.py             Audio assembly (intro + narration + outro)
  publish.py            Megaphone.fm upload
  pipeline.py           Orchestrates the full workflow
tests/                  One test file per module
assets/                 Your intro.mp3 and outro.mp3
output/                 Generated episodes (gitignored)
```
