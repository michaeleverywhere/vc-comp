#!/usr/bin/env python3
"""Amplify.LA portfolio scraper -> amplifyla_companies.json
Source: https://amplify.la/portfolio/ — WordPress/Elementor "portfolio" post loop:
company name (logo alt), one-line description, website, Amplify sector tags
(portfolio-tags-*: Enterprise / Consumer / Healthcare / Fintech) and the site's own
status class (portfolio-status-active / -exited)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://amplify.la/portfolio/"
PRIMARY = "Amplify.LA"
SECTOR_MAP = {"enterprise": [], "consumer": ["Consumer"], "healthcare": ["Health"], "fintech": ["FinTech / Insurance"]}
JUNK = re.compile(r"(?i)\b(logo|header|square|icon|wordmark|white|black|acquired|color|colour|new|final|v\d)\b|\b\d+\b")


def name_of(alt):
    n = clean(JUNK.sub(" ", (alt or "").replace("-logo", " logo")))
    n = clean(re.sub(r"[-_]+$", "", n or ""))
    return n


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for art in s.select("article.ecs-post-loop.type-portfolio"):
        cls = art.get("class") or []
        img = art.select_one(".elementor-widget-theme-post-featured-image img[alt]") or art.select_one("img[alt]")
        name = name_of(img.get("alt")) if img else None
        if not name:
            continue
        a = art.select_one("a[href^=http]")
        url = a["href"] if a and not is_social(a["href"]) and "amplify.la" not in a["href"] else None
        desc = art.select_one(".elementor-widget-text-editor")
        desc = clean(desc.get_text(" ", strip=True)) if desc else None
        cats = [c.replace("portfolio-tags-", "").replace("-", " ").title() for c in cls if c.startswith("portfolio-tags-")]
        cats = [c for c in cats if c.lower() != "active"]
        st = [c.replace("portfolio-status-", "") for c in cls if c.startswith("portfolio-status-")]
        status = st[0] if st else None
        if status is None and re.search(r"(?i)acquired", img.get("alt") or ""):
            status = "acquired"
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, sector_map=SECTOR_MAP,
                       status=status))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Amplify.LA companies")
    finish(out, "amplifyla", ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
