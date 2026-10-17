#!/usr/bin/env python3
"""Xontogeny portfolio scraper -> xontogeny_companies.json
Source: https://xontogeny.com/portfolio/ — portfolio logo grid: company name (site-authored
logo alt) and website ('Visit Site')."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://xontogeny.com/portfolio/"
PRIMARY = "Xontogeny"


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
    SKIP = {"xontogeny", "desktop shape", "mobile shape", "perceptive advisors"}
    for img in s.find_all("img", alt=True):
        nm = clean(re.sub(r"(?i)\s*logo\s*$", "", img["alt"]))
        if not nm or nm.lower() in SKIP or nm.lower() in seen or len(nm.split()) > 5:
            continue
        seen.add(nm.lower())
        box = img.parent
        a = None
        for _ in range(5):
            if box is None:
                break
            a = box.find("a", href=re.compile(r"^https?://(?!(www\.)?xontogeny)"))
            if a:
                break
            box = box.parent
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "xontogeny", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
