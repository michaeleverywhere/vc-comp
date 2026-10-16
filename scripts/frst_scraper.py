#!/usr/bin/env python3
"""Frst portfolio scraper -> frst_companies.json
Source: https://www.frst.vc/ — Webflow/Finsweet portfolio list: logo alt
(name), one-line description overlay, stage, website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://www.frst.vc/"
PRIMARY = "Frst"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".portfolio_item.w-dyn-item"):
        img = it.select_one("img.portfolio-logo[alt]")
        name = clean(img.get("alt")) if img else None
        if not name:
            continue
        a = it.select_one("a[href^=http]")
        d = it.select_one(".overlay-text")
        st = it.select_one('[fs-cmsfilter-field="stage"]')
        stage = clean(st.get_text()) if st else None
        out.append(rec(name, d.get_text(" ", strip=True) if d else None, a["href"] if a else None, PRIMARY, SOURCE_URL,
                       scraped_at, stage=stage_label(stage), stage_raw=stage))
    finish(out, "frst", ("description", "company_url", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
