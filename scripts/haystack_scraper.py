#!/usr/bin/env python3
"""Haystack portfolio scraper -> haystack_companies.json
Source: https://haystack.vc/portfolio — Framer portfolio cards (server-rendered subset): company
name (exit notes in parentheses as published, e.g. '(IPO: $DASH)'),
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_response, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://haystack.vc/portfolio"
PRIMARY = "Haystack"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # the server omits a charset header, so decode the UTF-8 bytes explicitly
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for a in s.select("a[href^='http']"):
        ps = [txt(p) for p in a.select("[data-framer-name='Company'] p") if txt(p)]
        if len(ps) < 2:
            continue
        m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", ps[0])
        nm, note = (clean(m.group(1)), clean(m.group(2))) if m else (ps[0], None)
        low = (note or "").lower()
        out.append(rec(nm, ps[1] if ps[1] != "Site" else None, site(a), PRIMARY, SOURCE_URL, scraped_at, exit_note=note,
                       status="public" if "ipo" in low else ("acquired" if "acq" in low else None)))
    finish(out, "haystack", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
