#!/usr/bin/env python3
"""Canary (Brazil) portfolio scraper -> canary_companies.json
Source: https://canary.com.br/portfolio/ — every company profile page Canary lists in its
own sitemap (canary.com.br/sitemap.xml, /portfolio/<slug>/ entries; the portfolio list
itself is a JS "load more"). Each profile gives company name, location (country), Canary
sector, one-line description, longer description and the company website ("Know more"
homepage link)."""
import os, re, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://canary.com.br/portfolio/"
SITEMAP = "https://canary.com.br/sitemap.xml"
PRIMARY = "Canary"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "climate": ["Climate / Sustainability"], "healthcare": ["Health"],
              "consumer": ["Consumer"], "b2b/enterprise": []}


def profile(url):
    try:
        s = BeautifulSoup(fetch(url), "html.parser")
    except Exception as e:
        print(f"  profile failed {url}: {e}", file=sys.stderr)
        return None
    t = clean(s.title.get_text()) if s.title else ""
    name = clean(re.sub(r"\s*\|\s*Canary\s*$", "", re.sub(r"^\s*Canary\s*\|\s*", "", t or "")))
    if not name or name.lower() in ("canary", "portfolio"):
        return None
    loc = sector = site = long_desc = None
    p = s.select_one("p.text-xs.uppercase")
    if p:
        parts = [clean(x) for x in p.get_text().split("|")]
        if len(parts) >= 2:
            loc, sector = parts[0] or None, parts[1] or None
        elif parts:
            sector = parts[0] or None
    h1 = s.find("h1")
    desc = clean(h1.get_text(" ", strip=True)) if h1 else None
    for a in s.select("a.cms-link[href^=http]"):
        u = urlparse(a["href"])
        if u.path in ("", "/") and not u.query and "canary.com.br" not in u.netloc and not is_social(a["href"]):
            site = a["href"]
            break
    rt = s.select_one("section.portfolio-block-rich-text .cms-rich-text")
    if rt:
        long_desc = clean(rt.get_text(" ", strip=True))
    return dict(name=name, loc=loc, sector=sector, desc=desc or long_desc, site=site, long_desc=long_desc, url=url)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    sm = fetch(SITEMAP)
    urls = sorted(set(u.replace("://www.", "://") for u in re.findall(r"<loc>(https?://[^<]*/portfolio/[^<]+/)</loc>", sm)))
    with ThreadPoolExecutor(6) as ex:
        profs = [p for p in ex.map(profile, urls) if p]
    out = []
    for p in profs:
        out.append(rec(p["name"], p["desc"], p["site"], PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[p["sector"]] if p["sector"] else [], sector_map=SECTOR_MAP,
                       location=p["loc"], long_description=p["long_desc"] if p["long_desc"] != p["desc"] else None,
                       profile_url=p["url"]))
    print(f"sitemap profiles: {len(urls)}, parsed: {len(profs)}")
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Canary companies")
    finish(out, "canary", ("description", "company_url", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
