#!/usr/bin/env python3
"""Hanaco Ventures portfolio scraper -> hanacoventures_companies.json
Source: https://hanacovc.com/companies/ — Israel/New York venture firm; WordPress site with a public "company" post type
(/wp-json/wp/v2/company) for the full list; the companies page card adds the one-liner, stage, founded year and
status, and each company page adds location, vertical, stage/status and the firm's longer write-up (first paragraph
kept as description)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, html_text, label_after, year_of
from _d50_common import rec, finish, wp_all

SOURCE_URL = "https://hanacovc.com/companies/"
ORIGIN = "https://hanacovc.com"
PRIMARY = "Hanaco Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = {}
    for c in BeautifulSoup(fetch(SOURCE_URL), "html.parser").select("article.company-card"):
        a = c.find("a", href=True)
        if not a:
            continue
        strs = [clean(x) for x in c.stripped_strings if clean(x)]
        d = c.select_one(".company-card__desc")
        cards[a["href"].rstrip("/")] = dict(one=clean(d.get_text(" ", strip=True)) if d else None,
                                            stage=label_after(strs, "Stage"), founded=year_of(label_after(strs, "Founded Y.")),
                                            status=label_after(strs, "Status"))
    posts = wp_all(ORIGIN, "company")
    pages = fetch_many([p["link"] for p in posts], workers=3, pause=0.3)
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        card = cards.get(p["link"].rstrip("/"), {})
        first = None
        for para in BeautifulSoup(p.get("content", {}).get("rendered") or "", "html.parser").find_all("p"):
            first = clean(para.get_text(" ", strip=True))
            if first:
                break
        loc = vertical = stage = status = None
        h = pages.get(p["link"])
        if h:
            m = BeautifulSoup(h, "html.parser").find("main")
            strs = [clean(x) for x in m.stripped_strings if clean(x)] if m else []
            loc, vertical = label_after(strs, "Location"), label_after(strs, "Vertical")
            stage, status = label_after(strs, "Stage"), label_after(strs, "Status")
        stage = stage or card.get("stage")
        status = (status or card.get("status") or "").lower() or None
        out.append(rec(name, card.get("one") or first, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[vertical] if vertical else [], long_description=first if card.get("one") else None,
                       location=loc, investment_stage_label=stage, founded_year=card.get("founded"),
                       status=status, profile_url=p["link"]))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Hanaco companies")
    finish(out, "hanacoventures", ("description", "location", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
