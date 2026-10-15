#!/usr/bin/env python3
"""Peak XV Partners portfolio scraper -> peakxv_companies.json
Source: https://www.peakxv.com/our-companies — Webflow CMS cards with logo alt
name + one-line description. Detail pages optionally enrich website.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://www.peakxv.com/our-companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "peakxv_companies.json")
PRIMARY = "Peak XV Partners"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    seen = set()
    for it in soup.select(".w-dyn-item"):
        a = it.select_one("a[href*='/companies/']")
        if not a:
            continue
        img = a.select_one("img[alt]")
        name = clean(img["alt"]) if img and img.get("alt") else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc_el = it.select_one(".com-header_block-paragraph .text-size-regular, .text-size-regular")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        # strip trailing "Read more"
        if desc and desc.lower().endswith("read more"):
            desc = clean(desc[: -len("read more")])
        href = urljoin(SOURCE_URL, a["href"])
        cards.append((name, href, desc))
    # sample detail pages lightly for websites (first 40 to stay polite/time-bound)
    sample = cards  # all — fetch_many is parallel
    pages = fetch_many([h for _, h, _ in sample], workers=8, pause=0.1)
    out = []
    for name, href, desc in cards:
        html = pages.get(href) or ""
        website = None
        if html:
            dsoup = BeautifulSoup(html, "html.parser")
            for a in dsoup.find_all("a", href=True):
                h = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if h.startswith("http") and "peakxv.com" not in h and label in ("website", "visit website", "company website", "visit site", "visit"):
                    website = clean_url(h)
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
