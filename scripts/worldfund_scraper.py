#!/usr/bin/env python3
"""World Fund portfolio scraper -> worldfund_companies.json
Source: https://www.worldfund.vc/portfolio — Webflow list (name, detail link)
plus each company page: description, Website, Founded, Location, Segment,
World Fund investment stage, management.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, year_of
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.worldfund.vc/portfolio"
PRIMARY = "World Fund"
LABELS = {"website", "website:", "founded", "management", "location", "segment", "world fund investment stage",
          "co-investors", "partners/customers"}
SECTOR_MAP = {"energy": ["Climate / Sustainability"], "food": ["Climate / Sustainability", "CPG"],
              "industrials": ["Climate / Sustainability"], "industry": ["Climate / Sustainability"],
              "transport / industry": ["Climate / Sustainability", "Transportation / Mobility"],
              "buildings": ["Climate / Sustainability", "PropTech"], "transport": ["Transportation / Mobility"]}


def block_after(st, label):
    if label not in [x.lower() for x in st]:
        return []
    i = [x.lower() for x in st].index(label) + 1
    out = []
    while i < len(st) and st[i].lower() not in LABELS and st[i] != "Subscribe to our Newsletter":
        out.append(st[i]); i += 1
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items, seen = [], set()
    for a in soup.select("a[href^='/portfolio/']"):
        if a["href"] in seen:
            continue
        p = a.find_parent(class_="w-dyn-item")
        strs = [x for x in (p.stripped_strings if p else []) if x not in ("See more", "to be announced")]
        if strs:
            seen.add(a["href"])
            items.append((clean(strs[0]), urljoin(SOURCE_URL, a["href"])))
    pages = fetch_many([u for _, u in items], workers=4, pause=0.2)
    out = []
    for name, link in items:
        st, _ = page_strings(pages.get(link) or "")
        st = [x for x in st if x.strip("\u200d ")]
        desc = None
        if "Portfolio Companies" in st:
            i = st.index("Portfolio Companies") + 1
            paras = []
            while i < len(st) and st[i] not in ("Why we invested in:",) and not st[i].startswith(("Seed", "Series", "Pre-Seed")):
                paras.append(st[i]); i += 1
            desc = " ".join(paras) or None
        web = label_after(st, "Website")
        seg = label_after(st, "Segment")
        stage = " ".join(block_after(st, "world fund investment stage")) or None
        rounds = [x.lstrip("— ").strip() for x in st if x.lstrip("— ").startswith("World Fund ") and " round" in x]
        out.append(rec(name, desc, ("https://" + web) if web and not web.startswith("http") else web, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[seg] if seg else [], sector_map=SECTOR_MAP,
                       year_founded=year_of(label_after(st, "Founded")), location=label_after(st, "Location"),
                       stage=stage, funding_rounds=rounds, management=block_after(st, "management"), detail_url=link))
    finish(out, "worldfund", ("description", "company_url", "location", "year_founded", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
