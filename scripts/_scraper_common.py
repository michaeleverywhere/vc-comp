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


# --- helpers added for the 2026-10-07 Daily 20 batch (additive) -------------

def webflow_pages(url: str, max_pages: int = 40) -> list:
    """Fetch a Webflow CMS list page plus every `?<hash>_page=N` page reached
    through its "next" pagination link. Returns the list of page HTML strings."""
    from urllib.parse import urljoin
    pages, seen, nxt = [], set(), url
    while nxt and nxt not in seen and len(pages) < max_pages:
        seen.add(nxt)
        html = fetch(nxt)
        pages.append(html)
        m = re.search(r'href="([^"]*\?[a-z0-9]+_page=\d+[^"]*)"[^>]*class="[^"]*w-pagination-next', html) or \
            re.search(r'class="[^"]*w-pagination-next[^"]*"[^>]*href="([^"]*\?[a-z0-9]+_page=\d+[^"]*)"', html)
        nxt = urljoin(url, m.group(1).replace("&amp;", "&")) if m else None
    return pages


def first_external_link(soup, own_domains, extra_skip=()) -> Optional[str]:
    """First http(s) link on a detail page that is not the firm's own domain
    and not a social / database profile."""
    for a in soup.select("a[href^=http]"):
        h = a["href"].strip()
        low = h.lower()
        if any(d in low for d in own_domains) or is_social(h) or any(s in low for s in extra_skip):
            continue
        return h
    return None


_ROUND_RX = re.compile(r"^(pre[- ]?seed|seed|seed\+|pre[- ]?series [a-e]|series [a-h]\+?|series [a-h]\d?)$", re.I)


def stage_label(raw) -> Optional[str]:
    """Funding round from a firm-site stage string. Exact round names are kept
    verbatim (title-cased); anything else goes through round_label(); labels
    that are not a round (Growth, Early stage, years...) return None."""
    s = clean(raw)
    if not s:
        return None
    if _ROUND_RX.match(s):
        s = re.sub(r"(?i)^pre[- ]?seed$", "Pre-Seed", s)
        s = re.sub(r"(?i)^pre[- ]?series", "Pre-Series", s)
        s = re.sub(r"(?i)^series ([a-h])", lambda m: "Series " + m.group(1).upper(), s)
        return s[:1].upper() + s[1:]
    return round_label(s)


def clean_url(url) -> Optional[str]:
    """Strip ad/tracking query strings (utm_*, gclid, srsltid) from a company
    link; social / database profile links are not a company website -> None."""
    u = clean(url)
    if not u or not u.lower().startswith("http") or is_social(u):
        return None
    if re.search(r"[?&](utm_|gclid|srsltid|fbclid)", u):
        u = u.split("?", 1)[0]
    return u


def carry_forward_descriptions(records, out_path) -> list:
    """Keep descriptions filled earlier from company websites/Wikidata
    (scripts/fill_descriptions_web.py) when the firm site itself has none.
    Matches on company name (case-insensitive); only fills empty
    descriptions. Returns the records that were filled so callers can re-tag."""
    import json as _json
    try:
        with open(out_path, encoding="utf-8") as fh:
            old = _json.load(fh)
    except (OSError, ValueError):
        return []
    prev = {(r.get("company_name") or "").strip().lower(): r.get("description")
            for r in old if isinstance(r, dict) and r.get("description")}
    filled = []
    for r in records:
        if not r.get("description"):
            d = prev.get((r.get("company_name") or "").strip().lower())
            if d:
                r["description"] = d
                filled.append(r)
    return filled


def apply_tag_overrides(records, overrides) -> int:
    """Hand-reviewed everywhere_tags (judgment pass, no LLM) keyed by company
    name; replaces the keyword tags for those companies. Returns count applied."""
    n = 0
    for r in records:
        t = overrides.get(r.get("company_name"))
        if t is not None:
            r["everywhere_tags"] = list(t)[:4]
            n += 1
    return n
