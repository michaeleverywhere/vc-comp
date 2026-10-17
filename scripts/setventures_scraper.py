#!/usr/bin/env python3
"""SET Ventures portfolio scraper -> setventures_companies.json
Source: https://setventures.com/portfolio/ — Portfolio list: company name (site logo alt), sector
and country."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://setventures.com/portfolio/"
PRIMARY = "SET Ventures"


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
    for h in s.select("h2.post-heading"):
        img = h.select_one("img[alt]")
        nm = clean(re.sub(r"\s*-\s*portfolio thumbnail$", "", img.get("alt") or "", flags=re.I)) if img else txt(h)
        if not nm or nm.lower() in seen or nm.lower() == "set ventures":
            continue
        seen.add(nm.lower())
        box = h.find_parent(class_="content") or h.parent
        p = [clean(x) for x in box.stripped_strings if clean(x) and clean(x) != "Hear from the founder"]
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=p[:1] if len(p) > 1 else [],
                       location=p[-1] if p else None))
    finish(out, "setventures", ("everywhere_tags",))


if __name__ == "__main__":
    main()
