#!/usr/bin/env python3
"""Cherry Ventures portfolio scraper -> cherry_companies.json
Source: sitemap founder-companies/* detail pages (name, description, website).
"""
import os, re, sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://cherry.vc/founders"
SITEMAP = "https://cherry.vc/sitemap.xml"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "cherry_companies.json")
PRIMARY = "Cherry Ventures"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    sm = fetch(SITEMAP)
    urls = sorted(set(re.findall(r"<loc>(https://cherry\.vc/founder-companies/[^<]+)</loc>", sm)))
    pages = fetch_many(urls, workers=8, pause=0.1)
    out, seen = [], set()
    for url, html in pages.items():
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        # title / h1
        name = None
        if soup.title and soup.title.string:
            name = clean(soup.title.string.split("|")[0])
        h1s = [clean(h.get_text(" ")) for h in soup.find_all("h1")]
        # prefer short title-like name; first h1 may be long tagline
        if name and len(name) < 60:
            pass
        else:
            name = None
        # slug fallback
        slug = url.rstrip("/").split("/")[-1].replace("-", " ").title()
        if not name:
            name = slug
        # if title equals long sentence, use slug
        if name and len(name) > 50:
            name = slug
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = None
        for h in h1s:
            if h and len(h) > 40:
                desc = h
                break
        if not desc:
            for p in soup.select("p"):
                t = clean(p.get_text(" "))
                if t and len(t) > 40:
                    desc = t
                    break
        website = None
        for a in soup.select("a[href^=http]"):
            href = a["href"]
            if "cherry.vc" in href or is_social(href):
                continue
            website = clean_url(href)
            break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
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
