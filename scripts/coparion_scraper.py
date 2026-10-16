#!/usr/bin/env python3
"""coparion portfolio scraper -> coparion_companies.json
Source: https://www.coparion.vc — home page portfolio modals
(`.portfolio-item-modal`): company name (h4) and "Website besuchen" link.
The modal quote text is a founder testimonial, not a company description,
so it is not used.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.coparion.vc"
PRIMARY = "coparion"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for m in soup.select(".portfolio-item-modal"):
        h = m.select_one("h4")
        if not h or not clean(h.get_text()):
            continue
        a = m.select_one("a.link-website[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        out.append(rec(h.get_text(" ", strip=True), None, href, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "coparion", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
