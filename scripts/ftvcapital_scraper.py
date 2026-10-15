#!/usr/bin/env python3
"""FTV Capital portfolio scraper -> ftvcapital_companies.json
Source: WP REST /wp-json/wp/v2/portfolio_item (paginated). Titles only on the
list endpoint (ACF empty); detail page HTML scraped for description/website when present.
"""
import os, re, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://ftvcapital.com/portfolio/"
REST = "https://ftvcapital.com/wp-json/wp/v2/portfolio_item?per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ftvcapital_companies.json")
PRIMARY = "FTV Capital"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts, page = [], 1
    while True:
        batch = fetch(REST.format(page), as_json=True)
        if not batch:
            break
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    # detail pages for desc/website
    urls = [p.get("link") for p in posts if p.get("link")]
    pages = fetch_many(urls, workers=6, pause=0.15)
    out, seen = [], set()
    for p in posts:
        name = clean(htmlmod.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        html = pages.get(p.get("link")) or ""
        soup = BeautifulSoup(html, "html.parser") if html else None
        desc = None
        website = None
        if soup:
            # try common content blocks
            for sel in [".entry-content p", ".portfolio-content p", "article p", ".et_pb_text_inner p"]:
                for el in soup.select(sel):
                    t = clean(el.get_text(" "))
                    if t and len(t) > 40 and "FTV" not in t[:20]:
                        desc = t
                        break
                if desc:
                    break
            for a in soup.find_all("a", href=True):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if href.startswith("http") and "ftvcapital.com" not in href and label in ("website", "visit website", "company website", "visit"):
                    website = clean_url(href)
                    break
            if not website:
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http") and "ftvcapital.com" not in href and not any(x in href for x in ("linkedin", "twitter", "facebook", "youtube", "instagram")):
                        # first external non-social
                        if label := clean(a.get_text(" ")):
                            if "investor" not in label.lower() and "portal" not in label.lower():
                                website = clean_url(href)
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
