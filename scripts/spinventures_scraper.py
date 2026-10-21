#!/usr/bin/env python3
"""Spin Ventures portfolio scraper -> spinventures_companies.json
Source: https://spin.vc/ventures/ — WordPress "Ventures" page, one card per portfolio company: company
name, Spin's "How does it make it better?" description, Industry label, founder name(s) and the
company website link."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://spin.vc/ventures/"
PRIMARY = "Spin Ventures"


def section(det, label):
    for h in det.select("h5"):
        if clean(h.get_text(" ", strip=True)) == label:
            p = h.find_next_sibling("p")
            if p:
                for a in p.select("a"):
                    a.decompose()
                return clean(p.get_text(" ", strip=True))
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for card in s.select("div.card.row"):
        det = card.select_one("div.details")
        h = det.select_one("h4") if det else None
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        web = None
        for a in card.select("div.links a[href]"):
            if clean(a.get_text(" ", strip=True)) == "Website" and not is_social(a["href"]):
                web = a["href"].strip()
        ind = section(det, "Industry")
        founder = section(det, "Founder") or section(det, "Founders")
        out.append(rec(name, section(det, "How does it make it better?"), web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[ind] if ind else [], founders=founder))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Spin Ventures companies")
    finish(out, "spinventures", ("description", "company_url", "sectors", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
