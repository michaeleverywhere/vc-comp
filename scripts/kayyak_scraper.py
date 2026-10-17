#!/usr/bin/env python3
"""Kayyak Ventures portfolio scraper -> kayyak_companies.json
Source: https://www.kayyakventures.com/ — homepage portfolio blocks: company name (h3) and
the founder quote shown under it."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.kayyakventures.com/"
PRIMARY = "Kayyak Ventures"


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
    for h in s.select(".sqs-html-content h3"):
        nm = txt(h)
        if not nm or nm.lower() in seen or nm in ("Investment Philosophy",):
            continue
        seen.add(nm.lower())
        p = h.find_next_sibling("p")
        d = clean(re.sub(r"^[“\"]|[”\"]$", "", txt(p) or "")) if p else None
        out.append(rec(nm, d or None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "kayyak", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
