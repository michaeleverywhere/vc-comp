#!/usr/bin/env python3
"""Alix Ventures portfolio scraper -> alixvc_companies.json
Source: https://www.alix.vc/portfolio-1 — 'Current Investments' list: company name
(heading) and description; 'Stealth' placeholders skipped."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.alix.vc/portfolio-1"
PRIMARY = "Alix Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    seen = set()
    start = next((h for h in s.select("h2") if txt(h) == "Current Investments"), None)
    if start is None:
        raise SystemExit("Current Investments heading not found")
    for h in start.find_all_next("h2"):
        nm = txt(h)
        if nm in ("Extended Family", "Request for Startups", "Anti-Requests", "Subscribe"):
            break
        if not nm or nm.lower() == "stealth" or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = h.find_next("p")
        d = txt(p) if p and p.find_previous("h2") is h else None
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "alixvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
