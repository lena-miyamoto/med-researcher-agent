"""Fetch a paywalled article via archive.is using a headed browser + human CAPTCHA solve.

archive.is is gated by an interactive CAPTCHA that blocks every automated fetch
(WebFetch, curl/wget with browser headers, curl_cffi, Jina reader proxy). This
script opens a *visible* browser, waits for the user to solve the CAPTCHA, then
scrapes the archived article's text straight from the live page.

Usage:
    uv run fetch-archive <url> [-o PATH] [--timeout SECONDS] [--browser NAME]

<url> may be the paywalled article URL (an archive.is ``newest`` link is built
automatically) or an existing archive.is/archive.ph/archive.today link.
"""

import argparse
import sys
import time
from pathlib import Path

import utils

DEFAULT_TIMEOUT = 900
DEFAULT_BROWSER = "chromium"

CHALLENGE_MARKERS = (
    "complete the security check",
    "one more step",
    "i'm not a robot",
    "captcha",
)


def build_archive_url(url):
    """Return an archive.is ``newest`` link for *url* unless it already is one."""
    if any(domain in url for domain in ("archive.is", "archive.ph", "archive.today")):
        return url
    return f"https://archive.is/newest/{url}"


def scrape(url, browser_name, timeout):
    """Open a headed browser at *url*, wait for the CAPTCHA, and scrape the text."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "playwright is not installed; run 'uv sync' to install project dependencies"
        ) from exc

    target = build_archive_url(url)

    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=False)
        page = browser.new_page()
        page.goto(target, wait_until="domcontentloaded", timeout=90000)
        print(
            f"Opened {target} — solve the CAPTCHA in the browser window.",
            file=sys.stderr,
            flush=True,
        )

        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(3)
            try:
                body = page.evaluate("document.body ? document.body.innerText : ''") or ""
            except Exception:
                continue  # mid-navigation; retry
            low = body.lower()
            if not any(marker in low for marker in CHALLENGE_MARKERS) and len(body.strip()) > 300:
                browser.close()
                return body

        browser.close()
        raise TimeoutError(f"CAPTCHA not solved within {timeout}s")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch a paywalled article via archive.is + headed-browser CAPTCHA solve."
    )
    parser.add_argument("url", help="Paywalled article URL or an existing archive.is link.")
    parser.add_argument("-o", "--output", help="Write scraped text to this file instead of stdout.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Seconds to wait for the CAPTCHA solve. Default {DEFAULT_TIMEOUT}.",
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default=DEFAULT_BROWSER,
        help=f"Browser to drive. Default {DEFAULT_BROWSER}.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        text = scrape(args.url, args.browser, args.timeout)
    except (RuntimeError, TimeoutError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {len(text)} chars to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    utils.run_cli(main)
