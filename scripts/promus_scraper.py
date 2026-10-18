#!/usr/bin/env python3
"""Promus Ventures portfolio scraper -> promus_companies.json
Source: https://promusventures.com/portfolio/ — WordPress site whose company grid is
built client-side; the listing is read from the rendered DOM via headless Chrome
(_chrome_dom.py): name, active/exited chip, city chip, one-liner and the company's
/project/<slug>/ page. Each project page (server-rendered) adds website, long
description, founded year, location and team line."""
import os, re, sys, time
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://promusventures.com/portfolio/"
PRIMARY = "Promus Ventures"


def detail(url):
    try:
        b = BeautifulSoup(fetch(url), "html.parser")
    except SystemExit:
        return {}
    for t in b(["script", "style", "svg", "nav", "header", "footer"]):
        t.decompose()
    strs = [clean(x) for x in b.stripped_strings if clean(x)]
    d = {}
    for lab in ("Founded", "Location", "Team"):
        if lab in strs:
            i = strs.index(lab)
            if i + 1 < len(strs):
                d[lab.lower()] = strs[i + 1]
    web = None
    for a in b.select("a[href^=http]"):
        h = a["href"]
        if "promusventures.com" not in h and not is_social(h) and clean(a.get_text(" ", strip=True)):
            web = h; break
    d["website"] = web
    # long description = the paragraph right after the website line
    if web and len(strs) > 3:
        host = re.sub(r"^https?://(www\.)?", "", web).strip("/").lower()
        for i, s in enumerate(strs[:12]):
            if s.lower().strip("/") == host and i + 1 < len(strs) and len(strs[i + 1]) > 40:
                d["description"] = strs[i + 1]; break
    return d


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=100000), "html.parser")
    out, seen = [], set()
    spot = {}  # spotlight cards carry city chip + one-liner
    for card in s.select('div[id^="spotlight-project-"]'):
        a = card.select_one('a[href*="/project/"]')
        chips = [clean(c.get_text(" ", strip=True)) for c in card.select("div.capitalize")]
        blurb = card.select_one(".wysiwyg-content div div")
        if a:
            spot[a["href"]] = (next((c for c in chips if c and c.lower() not in ("active", "exited")), None),
                               blurb.get_text(" ", strip=True) if blurb else None)
    for row in s.select('div[id^="all-project-"]'):
        h = row.select_one("h2")
        a = row.select_one('a[href*="/project/"]')
        if not h or not a:
            continue
        name = clean(h.get_text(" ", strip=True))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        chip = row.select_one("span.capitalize")
        status = (clean(chip.get_text(" ", strip=True)) or "").lower() or None if chip else None
        city, blurb = spot.get(a["href"], (None, None))
        d = detail(a["href"]); time.sleep(0.2)
        fy = d.get("founded")
        out.append(rec(name, d.get("description") or blurb, d.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       location=d.get("location") or city, founded_year=int(fy) if fy and fy.isdigit() else None,
                       team=d.get("team"), status=status, profile_url=a["href"]))
    if len(out) < 50:
        raise SystemExit(f"FATAL: only {len(out)} Promus rows rendered")
    finish(out, "promus", ("description", "company_url", "location", "founded_year", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
