#!/usr/bin/env python3
"""Cake Ventures portfolio scraper -> cakeventures_companies.json
Source: https://cake.vc/companies — Webflow CMS list: name, one-line description,
status (Active / ...), website, long description, Cake Ventures category labels,
location; founders come from each /companies/<slug> page (nested CMS list)."""
import os, re, sys, time
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://cake.vc/companies"
PRIMARY = "Cake Ventures"
SECTOR_MAP = {"aging": ["Health"], "care": ["Health"], "consumer": ["Consumer"], "women": [],
              "services": [], "b2b": [], "fintech": ["FinTech / Insurance"], "e-commerce": ["Consumer"],
              "health": ["Health"], "healthcare": ["Health"], "digital health": ["Health"], "insurtech": ["FinTech / Insurance"],
              "hardware": ["Deeptech / Robotics / AR/VR"], "ai": [], "future of work": ["Future of Work"]}
PLACEHOLDER = "This is some text inside of a div block."


def founders(url):
    try:
        b = BeautifulSoup(fetch(url), "html.parser")
    except Exception as e:
        print("  detail failed", url, e)
        return []
    for t in b(["script", "style", "svg", "nav", "header", "footer"]):
        t.decompose()
    strs = [clean(x) for x in b.stripped_strings]
    out = []
    for i, x in enumerate(strs[:-1]):
        if strs[i + 1] == PLACEHOLDER and x and x != PLACEHOLDER and x not in out:
            out.append(x)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in s.select(".companies-list_overlay-item.w-dyn-item"):
        n = it.select_one(".companies-list_item-name")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        one = it.select_one(".companies-list_item-description")
        long = it.select_one(".companies-list_overlay-description")
        st = it.select_one(".companies-list_overlay-status")
        a = it.select_one("a.companies-list_overlay-link[href^=http]")
        cats = list(dict.fromkeys(clean(c.get_text(" ", strip=True)) for c in it.select('[fs-cmsfilter-field="category"]')))
        cats = [c for c in cats if c]
        loc = None
        for d in it.select(".companies-list_overlay-detail"):
            lab = d.select_one(".text-style-subheading")
            if lab and clean(lab.get_text(" ", strip=True)).lower() == "location":
                lab.extract(); loc = clean(d.get_text(" ", strip=True))
                break  # later overlay blocks are unfilled Webflow template copies
        prof = it.select_one('a[href^="/companies/"]')
        fl = founders(urljoin(SOURCE_URL, prof["href"])) if prof else []
        time.sleep(0.2)
        status = (clean(st.get_text(" ", strip=True)) or "").lower() if st else None
        out.append(rec(name, clean(one.get_text(" ", strip=True)) if one else None,
                       a["href"].strip() if a and not is_social(a["href"]) else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=cats, sector_map=SECTOR_MAP,
                       long_description=clean(long.get_text(" ", strip=True)) if long else None,
                       location=loc, founders=fl, status=status or None,
                       profile_url=urljoin(SOURCE_URL, prof["href"]) if prof else None))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Cake Ventures companies")
    finish(out, "cakeventures", ("description", "company_url", "location", "founders", "status", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
