#!/usr/bin/env python3
"""Active Capital portfolio scraper -> activecapital_companies.json
Source: https://active.vc/ — portfolio grid on the home page (client-rendered Next.js,
read via headless Chrome): company name (logo alt "<Name> Logo"), website link, and the
site's own "Acquired by <acquirer>" caption for exited companies."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://active.vc/"
PRIMARY = "Active Capital"
NEWS = re.compile(r"(?i)/(news|newsroom|press|blog)/|acquire")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=20000), "html.parser")
    out = []
    for img in s.select('a[href^=http] > img[alt$=" Logo"]'):
        name = clean(re.sub(r"\s+Logo$", "", img.get("alt") or ""))
        if not name or name.lower().startswith("active capital"):
            continue
        a = img.parent
        href = a["href"].strip()
        cap = a.find_next_sibling("div")
        cap = clean(cap.get_text(" ", strip=True)) if cap else None
        acq = None
        if cap and cap.lower().startswith("acquired by"):
            acq = clean(cap[len("acquired by"):])
        url, exit_url = (None, href) if NEWS.search(href) else (href, None)
        if url and is_social(url):
            url = None
        out.append(rec(name, None, url, PRIMARY, SOURCE_URL, scraped_at,
                       status="acquired" if acq else "active", acquirer=acq, exit_news_url=exit_url))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Active Capital companies")
    finish(out, "activecapital", ("company_url", "status", "acquirer", "everywhere_tags"))


if __name__ == "__main__":
    main()
