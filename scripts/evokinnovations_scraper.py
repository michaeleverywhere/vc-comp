#!/usr/bin/env python3
"""Evok Innovations portfolio scraper -> evokinnovations_companies.json
Source: https://www.evokinnovations.com/portfolio — Evok Innovations (Vancouver), early-stage venture firm backing
industrial / climate technology for heavy industry. Each portfolio company has its own Wix item page with the company
name, city, description and website; the item pages are listed in the site's portfolio sitemap (falling back to the
rendered portfolio grid)."""
import os, sys, re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, HEADERS
from _d50_common import rec, finish

SOURCE_URL = "https://www.evokinnovations.com/portfolio"
SITEMAP = "https://www.evokinnovations.com/dynamic-portfolio-1_p_5fadb1fa_8075_4e6d_b1ce_bd32e41d4761_0_5000-sitemap.xml"
PRIMARY = "Evok Innovations"


def item_urls():
    try:
        r = requests.get(SITEMAP, headers=HEADERS, timeout=120)
        r.raise_for_status()
        u = re.findall(r"<loc>(https://www\.evokinnovations\.com/portfolio-1/[^<]+)</loc>", r.text)
        if len(u) >= 10:
            return u
    except requests.RequestException:
        pass
    from _chrome_dom import dom
    html = dom(SOURCE_URL, 20000, tries=2, min_len=2000)
    s = BeautifulSoup(html, "html.parser")
    out = []
    for a in s.select("a[href*='/portfolio-1/']"):
        if a["href"] not in out:
            out.append(a["href"])
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    urls = item_urls()
    pages = fetch_many(urls)
    out, seen = [], set()
    for u in urls:
        html = pages.get(u)
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        t = d.title.get_text() if d.title else ""
        name = clean(t.split(" | ")[0]) if " | " in t else None
        if not name or name.lower() in seen:
            continue
        m = d.find("main") or d
        parts = [clean(x) for x in m.stripped_strings]
        parts = [x for x in parts if x]
        loc = None
        if len(parts) > 1 and parts[0] == name and parts[1] != "BACK TO PORTFOLIO" and len(parts[1]) < 50:
            loc = parts[1]
        body = [clean(x.get_text(" ", strip=True)) for x in m.find_all("p")]
        body = [x for x in body if x and len(x) > 40]
        desc = " ".join(body) if body else None
        acq = re.search(r"(?i)\bacquired by ([^)(.,]+)", desc or "")
        web = None
        for a in m.find_all("a", href=True):
            h = a["href"]
            if h.startswith("http") and "evokinnovations" not in h and "wix" not in h and not is_social(h):
                web = h
                break
        seen.add(name.lower())
        out.append(rec(name, desc, web, PRIMARY, u, scraped_at, location=loc,
                       status="acquired" if acq else None, acquirer=clean(acq.group(1)) if acq else None))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Evok companies")
    finish(out, "evokinnovations", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
