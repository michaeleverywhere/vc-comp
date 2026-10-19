#!/usr/bin/env python3
"""XYZ Venture Capital portfolio scraper -> xyzvc_companies.json
Source: https://www.xyz.vc/portfolio — Squarespace portfolio gallery (company logo layer is
added by JS, so read via headless Chrome): company name (company-logo alt), XYZ's
one-line description (gallery image alt text, when it is a sentence rather than a file
name) and website (gallery click-through link)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.xyz.vc/portfolio"
PRIMARY = "XYZ Venture Capital"
FILE_RX = re.compile(r"\.(jpe?g|png|gif|webp|svg)$", re.I)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 20000, min_len=100000), "html.parser")
    out = []
    for fig in s.select("figure.gallery-grid-item"):
        logo = fig.select_one("img.company-logo[alt]")
        name = clean(logo.get("alt")) if logo else None
        if not name or FILE_RX.search(name):
            continue
        a = fig.select_one("a.gallery-grid-image-link[href]")
        gimg = a.find("img", alt=True) if a else None
        desc = clean(gimg.get("alt")) if gimg else None
        if desc and (FILE_RX.search(desc) or len(desc.split()) < 4):
            desc = None
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        out.append(rec(name, desc, href, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} XYZ companies")
    finish(out, "xyzvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
