#!/usr/bin/env python3
"""Theory Ventures portfolio scraper -> theory_companies.json
Source: https://theoryvc.com/portfolio — Webflow CMS `.portfolio-card_item`:
company name, one-line description, Finsweet stage and theme fields and a
detail page /portfolio/<slug>.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://theoryvc.com/portfolio"
PRIMARY = "Theory Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".portfolio-card_item"):
        nm = it.select_one(".portfolio-card_name")
        if not nm or not clean(nm.get_text()):
            continue
        p = it.select_one(".portfolio-hover_wrap p")
        f = {e["fs-list-field"]: clean(e.get_text(" ", strip=True)) for e in it.select("div[fs-list-field]")}
        a = it.select_one("a[href]")
        out.append(rec(nm.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[f["theory"]] if f.get("theory") else [], stage=f.get("stage"),
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "theory", ("description", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
