#!/usr/bin/env python3
"""Backstage Capital portfolio scraper -> backstage_companies.json
Source: https://backstagecapital.com/headliners/ — WordPress page of
"headliner" bio modals (`.modal-bio`): company name (h2), tagline info
lines, website icon link, description paragraph and founders line.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://backstagecapital.com/headliners/"
PRIMARY = "Backstage Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".modal-bio"):
        h = it.find("h2")
        if not h or not clean(h.get_text()):
            continue
        a = it.select_one("a.social-icon.web[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        body = it.select_one("div.purple-links")
        desc = founders = None
        if body:
            p = body.find("p")
            if p and not p.find("a"):
                desc = clean(p.get_text(" ", strip=True))
            fs = body.select_one("span.purple-links")
            founders = clean(fs.get_text(" ", strip=True)) if fs else None
        if not desc:
            info = [clean(i.get_text(" ", strip=True)) for i in it.select(".info")]
            desc = next((i for i in info if i), None)
        out.append(rec(h.get_text(" ", strip=True), desc, href, PRIMARY, SOURCE_URL, scraped_at, founders=founders))
    finish(out, "backstage", ("description", "company_url", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
