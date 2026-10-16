#!/usr/bin/env python3
"""Alpha Partners portfolio scraper -> alphapartners_companies.json
Source: https://alphapartners.com/ — WP REST `portfolio-item` posts (name,
industry taxonomy) plus each company page: status, Founded, Partnered, Fund,
description, Industries, management team, website.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, html_text, clean, year_of
from _d50_common import rec, finish, wp_all, wp_terms, page_strings

ORIGIN = "https://alphapartners.com"
SOURCE_URL = "https://alphapartners.com/portfolio/"
PRIMARY = "Alpha Partners"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "healthcare": ["Health"], "security": ["Cybersecurity"],
              "cybersecurity": ["Cybersecurity"], "defense": ["Deeptech / Robotics / AR/VR"], "robotics": ["Deeptech / Robotics / AR/VR"],
              "consumer": ["Consumer"], "climate": ["Climate / Sustainability"], "crypto": ["Web3 / Crypto"],
              "infrastructure": ["Dev Tools / Cloud"], "data": ["Data & Analytics"], "space": ["Deeptech / Robotics / AR/VR"]}


def after_prefix(strings, prefix):
    for s in strings:
        if s.startswith(prefix):
            return clean(s[len(prefix):])
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "portfolio-item")
    inds = wp_terms(ORIGIN, "industry")
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        strings, soup = page_strings(pages.get(p["link"]) or "")
        desc = None
        if "Industries:" in strings:
            i = strings.index("Industries:")
            if i > 0 and len(strings[i - 1]) > 40:
                desc = strings[i - 1]
        raw = BeautifulSoup(pages.get(p["link"]) or "", "html.parser")
        status = None
        for hd in raw.select("header"):
            if "site-header" in (hd.get("class") or []):
                continue
            for s in hd.stripped_strings:
                if s in ("Active", "Acquired", "IPO", "Public", "Exited", "Closed"):
                    status = s.lower()
        site = None
        for a in raw.select("a[href^=http]"):
            h = a["href"]
            txt = clean(a.get_text(" ", strip=True)) or ""
            if "alphapartners.com" in h or any(x in h for x in ("linkedin", "twitter", "x.com/")):
                continue
            if txt.lower().startswith("www.") or txt.lower() == urlparse(h).netloc.lower():
                site = h
                break
        mgmt = []
        if "Management team:" in strings:
            i = strings.index("Management team:") + 1
            while i < len(strings) and strings[i] != "Meet more of our portfolio.":
                mgmt.append(strings[i]); i += 1
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[inds[i] for i in p.get("industry") or [] if i in inds], sector_map=SECTOR_MAP,
                       status=status, year_founded=year_of(after_prefix(strings, "Founded:")),
                       first_invested_year=year_of(after_prefix(strings, "Partnered:")),
                       fund=after_prefix(strings, "Fund:"), management_team=mgmt))
    finish(out, "alphapartners", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
