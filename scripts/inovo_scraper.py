#!/usr/bin/env python3
"""Inovo VC portfolio scraper -> inovo_companies.json
Source: https://inovo.vc/portfolio — public Notion database table (Startup,
Website, Category, Founders' Origin, Entry, Entry stage, Entry round [€m],
Co-investors, Lead Person). The per-company Notion pages repeat the same
properties with no description, so description stays null. A Website cell that
reads "Acquired by X" is an exit note, not a URL.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://inovo.vc/portfolio"
PRIMARY = "Inovo VC"
SECTOR_MAP = {"edtech": ["Consumer"], "fintech": ["FinTech / Insurance"], "health": ["Health"],
              "devtools": ["Dev Tools / Cloud"], "productivity": ["Future of Work"], "ai/data science": ["Data & Analytics"],
              "ecommerce": ["Consumer"], "web3": ["Web3 / Crypto"], "construction": ["PropTech"], "food": ["CPG"],
              "design": ["Dev Tools / Cloud"], "ar/vr": ["Deeptech / Robotics / AR/VR"], "spacetech": ["Deeptech / Robotics / AR/VR"],
              "data/infrastructure": ["Data & Analytics", "Dev Tools / Cloud"], "data": ["Data & Analytics"],
              "cybersecurity": ["Cybersecurity"], "energy": ["Climate / Sustainability"], "hrtech": ["Future of Work"],
              "payroll": ["Future of Work", "FinTech / Insurance"], "social": ["Consumer"], "chatbots": ["Future of Work"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    heads = [clean(th.get_text(" ", strip=True)) for th in soup.select("thead th")]
    rows = []
    for tr in soup.select("tbody tr"):
        cells = tr.find_all("td", recursive=False)
        row = {}
        for h, td in zip(heads, cells):
            pills = [clean(p.get_text()) for p in td.select(".notion-pill")]
            a = td.select_one("a[href]")
            row[h] = {"text": clean(td.get_text(" ", strip=True)), "pills": pills, "href": a["href"] if a else None}
        rows.append(row)
    out = []
    for r in rows:
        st = r.get("Startup") or {}
        g = lambda k, f="text": (r.get(k) or {}).get(f)
        site = g("Website", "href")
        wtxt = g("Website") or ""
        acquirer = None
        if re.search(r"acquired", wtxt, re.I):
            m = re.search(r"acquired by (.+)", wtxt, re.I)
            acquirer = clean(m.group(1)) if m else None
            site = None
        es = g("Entry stage")
        out.append(rec(st.get("text"), None, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=g("Category", "pills") or [], sector_map=SECTOR_MAP,
                       founders_origin=", ".join(g("Founders' Origin", "pills") or []) or g("Founders' Origin"),
                       first_invested_year=year_of(g("Entry")), entry=g("Entry"), stage=stage_label(es), stage_raw=es,
                       entry_round_eur_m=g("Entry round [€m]"), co_investors=g("Co-investors", "pills") or [],
                       lead_partner=g("Lead Person"), acquirer=acquirer,
                       status="acquired" if acquirer or re.search(r"acquired", wtxt, re.I) else None))
    finish(out, "inovo", ("company_url", "acquirer", "stage", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
