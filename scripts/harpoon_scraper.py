#!/usr/bin/env python3
"""Harpoon Ventures portfolio scraper -> harpoon_companies.json
Source: https://www.harpoon.vc/portfolio — Webflow CMS cards
(`.portfolio-item .portco-card`, the visible variant): company name, one-line description, detail
link, and visible status pills (Acq. by ..., IPO). Stealth placeholder cards
("Coming soon..." / "STEALTH CO") are skipped.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.harpoon.vc/portfolio"
PRIMARY = "Harpoon Ventures"


def vis(el):
    return "w-condition-invisible" not in (el.get("class") or [])


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".portfolio-item.w-dyn-item"):
            card = next((c for c in it.select(".portco-card") if vis(c)), None)
            if not card:
                continue
            nm = card.select_one(".portco-card-name")
            name = clean(nm.get_text(" ", strip=True)) if nm else None
            if not name or name.lower().startswith(("coming soon", "stealth")):
                continue
            lab = card.select_one(".portco-card-label")
            pills = [clean(" ".join(c.get_text(" ", strip=True) for c in p.find_all(recursive=False) if vis(c)))
                     for p in card.select(".acquired-pill") if vis(p) and "black-flag" not in (p.get("class") or [])]
            pills = [p for p in pills if p]
            pl = " ".join(pills).lower()
            out.append(rec(name, lab.get_text(" ", strip=True) if lab else None, None, PRIMARY, SOURCE_URL, scraped_at,
                           exit_note="; ".join(pills) or None,
                           status="acquired" if "acq" in pl else "ipo" if "ipo" in pl else None,
                           detail_url=urljoin(SOURCE_URL, card["href"]) if card.get("href") else None))
    finish(out, "harpoon", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
