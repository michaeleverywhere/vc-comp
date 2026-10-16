#!/usr/bin/env python3
"""Hyperplane portfolio scraper -> hyperplane_companies.json
Source: https://www.hyperplane.vc/companies — Webflow cards (name, summary,
tagline, Hyperplane round tag) plus each company page: website (logo link),
category tags, description.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.hyperplane.vc/companies"
PRIMARY = "Hyperplane"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "security": ["Cybersecurity"], "cybersecurity": ["Cybersecurity"],
              "data & analytics": ["Data & Analytics"], "physical ai": ["Deeptech / Robotics / AR/VR"],
              "robotics": ["Deeptech / Robotics / AR/VR"], "autonomous driving": ["Transportation / Mobility"],
              "developer tools": ["Dev Tools / Cloud"], "infrastructure": ["Dev Tools / Cloud"],
              "healthcare": ["Health"], "defense": ["RegTech/Gov/Legal"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards, seen = [], set()
    for a in soup.select("a.card.is-company[href]"):
        link = urljoin(SOURCE_URL, a["href"])
        t = a.select_one(".card_title")
        if not t or link in seen:
            continue
        seen.add(link)
        g = lambda sel: (lambda e: clean(e.get_text(" ", strip=True)) if e else None)(a.select_one(sel))
        cards.append([clean(t.get_text(" ", strip=True)), link, g(".card_summary"), g(".overlay_title"), g(".tag_text"), None, None, []])
    by_link = {c[1]: c for c in cards}
    for row in soup.select(".table_row"):
        a = row.select_one("a[href^='/companies/']")
        if not a:
            continue
        link = urljoin(SOURCE_URL, a["href"])
        kids = [k for k in row.find_all(recursive=False) if k.name == "div"]
        txt = lambda k: clean(k.get_text(" ", strip=True))
        name = txt(kids[0]) if kids else None
        tags = [txt(x) for x in row.select(".is-tags-list .table_text")]
        plain = [txt(k) for k in kids[1:] if "table_text" in (k.get("class") or [])]
        cell = row.select_one(".table_cell")
        stage, status_txt = (plain + [None, None])[:2]
        c = by_link.get(link)
        if c is None:
            c = [name, link, txt(cell) if cell else None, None, None, None, None, []]
            cards.append(c); by_link[link] = c
        c[5], c[6], c[7] = stage, status_txt, tags
    pages = fetch_many([c[1] for c in cards], workers=6, pause=0.1)
    out = []
    for name, link, summary, tagline, round_, entry_stage, status_txt, list_tags in cards:
        site, tags, desc = None, [], None
        if pages.get(link):
            s = BeautifulSoup(pages[link], "html.parser")
            a = s.select_one("main a.company_link[href^=http]")
            site = a["href"] if a else None
            tags = [clean(x.get_text(" ", strip=True)) for x in s.select("main .tag_text")]
            bg = s.select_one("main .button-group")
            p = bg.find_previous_sibling("p") if bg else None
            if p is None:
                ps = [x for x in s.select("main section p") if len(x.get_text(strip=True)) > 60]
                p = ps[0] if ps else None
            desc = clean(p.get_text(" ", strip=True)) if p else None
        tags = list_tags or tags
        out.append(rec(name, desc or summary, site, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, sector_map=SECTOR_MAP,
                       summary=summary, tagline=tagline, hyperplane_round=round_, stage=entry_stage or round_,
                       status_detail=status_txt, acquirer=status_txt[12:].strip() if (status_txt or "").startswith("Acquired by") else None,
                       status=("acquired" if (status_txt or "").startswith("Acquired") else "active" if status_txt else None),
                       detail_url=link))
    finish(out, "hyperplane", ("description", "company_url", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
