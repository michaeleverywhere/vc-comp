#!/usr/bin/env python3
"""M Ventures (Merck KGaA) portfolio scraper -> mventures_companies.json
Source: https://www.m-ventures.com/portfolio — card grid (name, exit badge) plus
each company page: sector line, tagline, description, website, investment lead.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.m-ventures.com/portfolio"
PRIMARY = "M Ventures"
SECTOR_MAP = {"biotechnology": ["BioTech", "Health"], "healthcare": ["Health"], "electronics": ["Deeptech / Robotics / AR/VR"],
              "life science": ["BioTech", "Health"], "sustainability": ["Climate / Sustainability"],
              "digital health": ["Health"], "medtech": ["Health"], "semiconductor": ["Deeptech / Robotics / AR/VR"],
              "quantum": ["Deeptech / Robotics / AR/VR"]}


def is_sector_line(s):
    parts = [x.strip().lower() for x in s.replace("–", "-").split(" - ") if x.strip()]
    return bool(parts) and len(s) < 80 and all(p in SECTOR_MAP or p in EXTRA_SECTORS for p in parts)


EXTRA_SECTORS = {"electronics", "life science", "life sciences", "healthcare", "biotechnology", "sustainability",
                 "digital", "materials", "new businesses", "fund investment"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for c in soup.select("figure.card--company"):
        t = c.select_one(".card__title"); a = c.select_one("a[href]")
        if t and a:
            ex = c.select_one(".card__exit")
            cards.append((clean(t.get_text(" ", strip=True)), a["href"], clean(ex.get_text(" ", strip=True)) if ex else None))
    pages = fetch_many([c[1] for c in cards], workers=6, pause=0.1)
    out = []
    for name, link, exit_ in cards:
        st, s = page_strings(pages.get(link) or "")
        sector = tagline = desc = site = lead = None
        vis = [k for k, x in enumerate(st) if x.lower().startswith("visit ")]
        if name in st:
            i = st.index(name, 1) if name in st[1:] else st.index(name)
            block = st[i + 1:i + 12]
            if block and is_sector_line(block[0]):
                sector = block.pop(0)
            if block and len(block[0]) < 160:
                tagline = block.pop(0)
            paras = []
            for x in block:
                if len(x) < 60 or x.lower().startswith("visit "):
                    break
                paras.append(x)
            desc = " ".join(paras) or None
        TITLE = ("director", "partner", "principal", "associate", "head", "analyst", "managing")
        for k in range(len(st) - 1):
            if 1 < len(st[k]) < 40 and any(w in st[k + 1].lower() for w in TITLE) and len(st[k + 1]) < 40 \
                    and k > (st.index(name) if name in st else 0):
                lead = st[k]; break
        for a in s.select("a[href^=http]") if pages.get(link) else []:
            if a.get_text(" ", strip=True).lower().startswith("visit") and "m-ventures" not in a["href"] and not is_social(a["href"]):
                site = a["href"]; break
        secs = [x.strip() for x in (sector or "").replace("–", "-").split(" - ") if x.strip()]
        e = (exit_ or "").lower()
        out.append(rec(name, desc or tagline, site, PRIMARY, SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP,
                       tagline=tagline, lead_partner=lead, exit_type=exit_,
                       status=("ipo" if "ipo" in e else "acquired" if ("acqui" in e or "trade" in e or "m&a" in e) else ("exited" if e else "active"))))
    finish(out, "mventures", ("description", "company_url", "lead_partner", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
