#!/usr/bin/env python3
"""Neotribe Ventures portfolio scraper -> neotribe_companies.json
Source: https://www.neotribe.vc/portfolio — portfolio cards (JS-rendered, read via headless
Chrome): company name (logo alt), one-line description, Neotribe sector(s), entry round
(-> stage) and year (-> first_invested), website link and the "Exited" badge (-> status)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social, stage_label
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.neotribe.vc/portfolio"
PRIMARY = "Neotribe Ventures"
SECTOR_MAP = {"security networking & infrastructure": ["Cybersecurity", "Dev Tools / Cloud"],
              "data - ai - analytics": ["Data & Analytics"], "climate & energytech": ["Climate / Sustainability"],
              "robotics & hardware": ["Deeptech / Robotics / AR/VR"], "computational bio & health": ["BioTech", "Health"],
              "computational biology": ["BioTech"], "enterprise software": [], "fintech": ["FinTech / Insurance"],
              "quantum": ["Deeptech / Robotics / AR/VR"], "developer tools": ["Dev Tools / Cloud"],
              "medical diagnostics": ["Health"], "fintech & web3": ["FinTech / Insurance", "Web3 / Crypto"], "drug discovery": ["BioTech"], "other": []}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 20000, min_len=50000), "html.parser")
    out = []
    for strong in s.find_all("strong", string=re.compile(r"^\s*Sector:\s*$")):
        p = strong.parent
        card = p
        while card is not None and not card.find("img", alt=True):
            card = card.parent
        if card is None:
            continue
        img = card.find("img", alt=True)
        name = clean(img.get("alt"))
        if not name:
            continue
        sectors = [clean(x) for x in re.split(r",\s*(?=[A-Z])", clean(p.get_text(" ", strip=True).replace("Sector:", "", 1)) or "") if clean(x)]
        info = p.parent
        desc_el = info.find_previous_sibling("div")
        desc = clean(desc_el.get_text(" ", strip=True)) if desc_el and not desc_el.find("img") else None
        stage = year = None
        for sp in info.find_all("p"):
            st = sp.find("strong")
            if st and st is not strong:
                stage = stage_label(st.get_text(" ", strip=True))
                y = re.search(r"\b(19|20)\d{2}\b", sp.get_text(" ", strip=True))
                year = int(y.group(0)) if y else None
        a = info.find("a", href=re.compile(r"^https?://"))
        href = a["href"] if a and not is_social(a["href"]) else None
        exited = any(clean(x.get_text()) == "Exited" for x in card.find_all("span"))
        out.append(rec(name, desc, href, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       stage=stage, first_invested=year, status="exited" if exited else "active"))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Neotribe companies")
    finish(out, "neotribe", ("description", "company_url", "sectors", "stage", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
