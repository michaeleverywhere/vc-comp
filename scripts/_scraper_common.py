"""Tiny shared helpers for Private Comps firm scrapers."""
from __future__ import annotations

import re
import time
from typing import Optional

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3


def fetch(url: str, as_json: bool = False):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json() if as_json else r.text
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def fetch_response(url: str) -> requests.Response:
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s) -> Optional[str]:
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def html_text(html: str) -> Optional[str]:
    from bs4 import BeautifulSoup
    if not html:
        return None
    return clean(BeautifulSoup(html, "html.parser").get_text(" ", strip=True))


# --- helpers added for the 2026-10-05 Daily 10 batch (additive) -------------

def round_label(raw) -> Optional[str]:
    """Funding-round label (Pre-Seed/Seed/Series A/...) from a firm-site string,
    via normalize_stages; None when the string carries no clear round."""
    if not raw:
        return None
    try:
        from normalize_stages import extract_rounds, format_rounds
    except ImportError:  # pragma: no cover
        return None
    return format_rounds(extract_rounds(str(raw))) or None


def tags_for(name, description, sectors=None, sector_map=None) -> list:
    """Firm sector labels mapped through sector_map first, then the shared
    keyword classifier (automation/tags.py); deduped, capped at 4."""
    import os as _os, sys as _sys
    _auto = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), _os.pardir, "automation")
    if _auto not in _sys.path:
        _sys.path.insert(0, _auto)
    from tags import classify, TAGS
    out = []
    for s in sectors or []:
        key = (s or "").strip().lower()
        for t in (sector_map or {}).get(key, []):
            if t not in out:
                out.append(t)
    for t in classify(name, description, sectors):
        if t not in out:
            out.append(t)
    return [t for t in out if t in TAGS][:4]


def fetch_many(urls, workers: int = 4, pause: float = 0.2) -> dict:
    """Polite parallel GET for detail pages: {url: html or None}."""
    from concurrent.futures import ThreadPoolExecutor

    def one(u):
        for attempt in range(1, RETRIES + 1):
            try:
                r = requests.get(u, headers=HEADERS, timeout=TIMEOUT)
                if r.status_code == 404:
                    return u, None
                r.raise_for_status()
                time.sleep(pause)
                return u, r.text
            except requests.RequestException:
                time.sleep(1.5 * attempt)
        return u, None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(ex.map(one, urls))


# --- helpers added for the 2026-10-06 Daily 20 batch (additive) -------------

def label_after(strings, *labels):
    """In a list of text fragments (e.g. soup.stripped_strings), return the
    fragment that follows the first fragment equal to one of `labels`
    (case-insensitive, trailing ':' ignored). None when the label is absent."""
    want = {l.lower().rstrip(":").strip() for l in labels}
    strings = [clean(s) for s in strings]
    strings = [s for s in strings if s]
    for i, s in enumerate(strings[:-1]):
        if s.lower().rstrip(":").strip() in want:
            nxt = strings[i + 1]
            if nxt.lower().rstrip(":").strip() in want:
                continue
            return nxt
    return None


def year_of(s):
    """First 4-digit year in a string, as int; None otherwise."""
    m = re.search(r"\b(19|20)\d{2}\b", str(s or ""))
    return int(m.group(0)) if m else None


def is_social(url) -> bool:
    u = (url or "").lower()
    return any(d in u for d in ("linkedin.com", "twitter.com", "x.com/", "facebook.com", "instagram.com",
                                "youtube.com", "medium.com", "tiktok.com", "crunchbase.com", "angel.co",
                                "wellfound.com", "github.com", "apple.com/app", "play.google.com"))
