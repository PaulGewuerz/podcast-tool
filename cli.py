#!/usr/bin/env python3
"""
LocalPod CLI — command-line interface for the podcast pipeline.

Examples:
    # Produce an episode from pasted text (test mode on by default):
    python cli.py --title "My Episode" --text "Article body goes here..."

    # Produce an episode from a URL:
    python cli.py --title "My Episode" --url https://example.com/article

    # Just generate audio without publishing:
    python cli.py --title "My Episode" --text "..." --skip-publish

    # Check your config before running:
    python cli.py --check-config
"""

import argparse
import sys

from localpod import config
from localpod.pipeline import run


def check_config() -> None:
    """Print config status and exit."""
    print(f"Test mode : {'ON' if config.TEST_MODE else 'OFF'}")
    print(f"Assets dir: {config.ASSETS_DIR}")
    print(f"Output dir: {config.OUTPUT_DIR}")
    print()

    problems = config.validate()
    if problems:
        print("Problems found:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("Config looks good.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="localpod",
        description="LocalPod — automated podcast production pipeline",
    )

    parser.add_argument(
        "--title", "-t",
        required=False,
        help="Episode title (required unless --check-config)",
    )
    parser.add_argument(
        "--text",
        help="Article text to narrate (use this OR --url)",
    )
    parser.add_argument(
        "--url", "-u",
        help="URL of article to fetch and narrate (use this OR --text)",
    )
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Generate audio but don't upload to Megaphone",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate config and exit",
    )

    args = parser.parse_args()

    # --- Config check mode ---
    if args.check_config:
        check_config()
        return

    # --- Normal pipeline run ---
    if not args.title:
        parser.error("--title is required")
    if not args.text and not args.url:
        parser.error("Provide either --text or --url")

    # Show mode at startup
    mode = "TEST MODE" if config.TEST_MODE else "LIVE MODE"
    print(f"\nLocalpod starting in {mode}")
    print(f"{'='*50}\n")

    result = run(
        title=args.title,
        text=args.text,
        url=args.url,
        skip_publish=args.skip_publish,
    )

    # Exit cleanly
    sys.exit(0)


if __name__ == "__main__":
    main()
