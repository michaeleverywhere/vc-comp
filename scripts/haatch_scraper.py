#!/usr/bin/env python3
"""Haatch portfolio scraper -> haatch_companies.json
Source: https://haatch.com/portfolio — Portfolio cards: company name, year founded, year
invested and note (exits flagged)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://haatch.com/portfolio"
PRIMARY = "Haatch"


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
    for card in s.select("div.card-body"):
        h = card.select_one("h3")
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in card.stripped_strings if clean(x) and clean(x) != "Learn more:"]
        fy = p[p.index("Founded") + 1] if "Founded" in p[:-1] else None
        iy = p[p.index("Invested") + 1] if "Invested" in p[:-1] else None
        d = [x for x in p if x not in (nm, "Founded", "Invested", fy, iy)]
        note = d[0] if d else None
        out.append(rec(nm, note, None, PRIMARY, SOURCE_URL, scraped_at, founded=fy, year=iy,
                       status="exited" if note and re.search(r"\bexit", note, re.I) else None))
    finish(out, "haatch", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
