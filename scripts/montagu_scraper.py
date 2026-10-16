#!/usr/bin/env python3
"""Montagu Private Equity portfolio scraper -> montagu_companies.json
Source: https://montagu.com/portfolio/ — WP REST `portfolio` post type; name =
title, description = the content paragraphs before the first heading (the
"A Montagu Business" / "Opportunity" bullet sections are skipped). Montagu
does not publish company websites or realized status in the feed.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, clean
from _d50_common import rec, finish, wp_all

ORIGIN = "https://montagu.com"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "Montagu Private Equity"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        soup = BeautifulSoup(p.get("content", {}).get("rendered") or "", "html.parser")
        paras = []
        for el in soup.find_all(["p", "h2", "h3", "h4"]):
            if el.name != "p":
                break
            t = clean(el.get_text(" ", strip=True))
            if t:
                paras.append(t)
        out.append(rec(html_text(p["title"]["rendered"]), " ".join(paras) or None, None, PRIMARY, SOURCE_URL,
                       scraped_at, detail_url=p.get("link")))
    finish(out, "montagu", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
