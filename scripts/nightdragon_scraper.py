#!/usr/bin/env python3
"""NightDragon portfolio scraper -> nightdragon_companies.json
Source: https://www.nightdragon.com/portfolio/ — portfolio grid: company name (h4), current /
exited status and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.nightdragon.com/portfolio/"
PRIMARY = "NightDragon"


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
    for h in s.select("h4.ep-item-grid-item-title"):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        card = h.parent.parent.parent
        ss = [clean(x) for x in card.stripped_strings if clean(x) and clean(x) != nm]
        st = next((x for x in ss if x.lower() in ("current", "exited", "acquired")), None)
        if not st:
            continue
        d = next((x for x in ss if len(x) > 30), None)
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, holding=st, status="exited" if st and st.lower() != "current" else None))
    finish(out, "nightdragon", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
