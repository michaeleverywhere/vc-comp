#!/usr/bin/env python3
"""DBL Partners portfolio scraper -> dbl_companies.json
Source: https://www.dbl.vc/portfolio/ — WP REST `portfolio` (title, content =
description, portfolio-sector taxonomy) plus each company page for its website.
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, fetch_many, is_social
from _d50_common import rec, finish, wp_all, wp_terms, page_strings

ORIGIN = "https://www.dbl.vc"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "DBL Partners"
SECTOR_MAP = {"clean energy": ["Climate / Sustainability"], "health care": ["Health"],
              "sustainable products & services": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    terms = wp_terms(ORIGIN, "portfolio-sector")
    posts = wp_all(ORIGIN, "portfolio")
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        _, soup = page_strings(pages.get(p["link"]) or "")
        site = next((a["href"] for a in soup.select("a[href^=http]")
                     if "dbl.vc" not in a["href"] and not is_social(a["href"])), None)
        secs = [terms[i] for i in p.get("portfolio-sector") or [] if i in terms and terms[i] != "Featured"]
        desc = html_text(p["content"]["rendered"]) or html_text(p["excerpt"]["rendered"])
        out.append(rec(html_text(p["title"]["rendered"]), desc or None, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=secs, sector_map=SECTOR_MAP, detail_url=p["link"]))
    finish(out, "dbl", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
