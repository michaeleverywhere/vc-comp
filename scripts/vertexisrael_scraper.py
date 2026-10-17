#!/usr/bin/env python3
"""Vertex Ventures Israel portfolio scraper -> vertexisrael_companies.json
Source: https://www.vertexventures.co.il/portfolio/ — portfolio carousel cards
(`div[class*=projectWrapper]`): company name (site-authored logo alt), screen-
reader description and Exited / Recent badge. 'Stealth' entries are skipped."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.vertexventures.co.il/portfolio/"
PRIMARY = "Vertex Ventures Israel"


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
    for w in s.select("div[class*='projectWrapper']"):
        img = w.find("img", alt=True)
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen or nm.lower().startswith("stealth"):
            continue
        seen.add(nm.lower())
        badge = txt(w.select_one("div[class*='Badge']"))
        out.append(rec(nm, txt(w.select_one("p.sr-only")), None, PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if badge and badge.lower() == "exited" else None))
    finish(out, "vertexisrael", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
