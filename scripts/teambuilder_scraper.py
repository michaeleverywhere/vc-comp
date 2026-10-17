#!/usr/bin/env python3
"""Team Builder Ventures portfolio scraper -> teambuilder_companies.json
Source: https://www.teambuilderventures.com/ — homepage 'Companies' logo
wall: company name (site-authored logo alt text); the co-investor wall after it
is ignored."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.teambuilderventures.com/"
PRIMARY = "Team Builder Ventures"


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
    h = next((x for x in s.select("h3") if txt(x) == "Companies"), None)
    stop = next((x for x in s.select("h3") if txt(x) == "Co-Investors"), None)
    if h is None:
        raise SystemExit("Companies heading not found")
    for img in h.find_all_next("img"):
        if stop is not None and img in stop.find_all_next("img"):
            break
        nm = clean(img.get("alt"))
        if not nm or nm.lower() in seen or re.search(r"\.(png|jpe?g|svg)$", nm, re.I) or nm == "Team Builder Ventures":
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "teambuilder", ("everywhere_tags",))


if __name__ == "__main__":
    main()
