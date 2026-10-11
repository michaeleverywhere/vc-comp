#!/usr/bin/env python3
"""Qiming Venture Partners portfolio scraper -> qiming_companies.json
Source: https://www.qimingvc.com/en/portfolio — server-rendered list; each
.portfolio-box has the name (.portfolio-name), Qiming's sector label (.p-type:
Healthcare / Technology / Consumer ...), a one-line description and the company
website (a.outlink). No location, round, year or status published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.qimingvc.com/en/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "qiming_companies.json")
PRIMARY = "Qiming Venture Partners"
SECTOR_TAG_MAP = {"consumer": ["Consumer"]}  # "Healthcare"/"Technology" too broad: keyword tagger decides
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "2Dunet": ["Transportation / Mobility", "Consumer"],
    "ABUP": ["Transportation / Mobility"],
    "Afu": ["CPG"],
    "AirQuality": ["Climate / Sustainability"],
    "Apus Group": ["Consumer"],
    "BiLin": ["Consumer"],
    "Bingo Box": ["Consumer"],
    "Bomming Vision Technology": ["Deeptech / Robotics / AR/VR"],
    "BTR China": ["Climate / Sustainability"],
    "Cencorp Automation": ["Deeptech / Robotics / AR/VR"],
    "CETA": ["Climate / Sustainability"],
    "Chaodian Culture": ["Gaming / Media / Entertainment"],
    "ChinaCache": ["Dev Tools / Cloud"],
    "Chuhang": ["Transportation / Mobility", "Deeptech / Robotics / AR/VR"],
    "Chuman": ["Gaming / Media / Entertainment"],
    "CIX Technology": ["Deeptech / Robotics / AR/VR"],
    "Convenient Power": ["Deeptech / Robotics / AR/VR"],
    "Coohua": ["Consumer"],
    "Cool College": ["Future of Work"],
    "Cootek": ["Consumer"],
    "Dining Secretary": ["Consumer"],
    "eHi": ["Transportation / Mobility"],
    "FangTek": ["Deeptech / Robotics / AR/VR"],
    "FindPlastics": ["Logistics / Supply Chain"],
    "FINERN": ["Deeptech / Robotics / AR/VR"],
    "Fortune": ["FinTech / Insurance"],
    "Gaiya": ["Climate / Sustainability"],
    "Genius": ["Future of Work"],
    "Hanqi Environment": ["Climate / Sustainability"],
    "HashQuark": ["Web3 / Crypto"],
    "Hexing": ["Climate / Sustainability"],
    "Honess": ["Climate / Sustainability"],
    "Insta360": ["Consumer"],
    "International Water": ["Climate / Sustainability"],
    "Jiayuan": ["Consumer"],
    "Kaola Reading": ["Consumer"],
    "KeySino": ["Climate / Sustainability"],
    "Kintep": ["Climate / Sustainability"],
    "Lanmi": ["Consumer"],
    "LP Amina": ["Climate / Sustainability"],
    "Luotianyi": ["Gaming / Media / Entertainment"],
    "LuPu": ["FinTech / Insurance"],
    "MainOne": ["Dev Tools / Cloud"],
    "Mandian": ["Gaming / Media / Entertainment"],
    "Marvel-Tech": ["Climate / Sustainability"],
    "Meituan": ["Consumer"],
    "Micromedia": ["Dev Tools / Cloud"],
    "Mksemi": ["Deeptech / Robotics / AR/VR"],
    "moodytiger": ["Consumer"],
    "More Tickets (Motianlun)": ["Gaming / Media / Entertainment"],
    "Mutto": ["Deeptech / Robotics / AR/VR"],
    "NEIWAI": ["Consumer"],
    "OneAPM": ["Dev Tools / Cloud"],
    "PELLIOT": ["Consumer"],
    "PRM": ["Deeptech / Robotics / AR/VR"],
    "Reddoorz": ["Consumer"],
    "SGEET": ["Climate / Sustainability"],
    "SinoDynamics": ["Deeptech / Robotics / AR/VR"],
    "Spēs": ["CPG"],
    "StepFun": ["Deeptech / Robotics / AR/VR"],
    "SUPERMAG": ["Deeptech / Robotics / AR/VR"],
    "Tasogare Coffee": ["CPG"],
    "Transwarp": ["Deeptech / Robotics / AR/VR"],
    "Tuhu Car": ["Transportation / Mobility", "Consumer"],
    "V Light": ["Consumer"],
    "Viewtrix": ["Deeptech / Robotics / AR/VR"],
    "Webuy (dba Jingling)": ["Consumer"],
    "Woxiaoya": ["CPG"],
    "Xiaoe Tech": ["Future of Work"],
    "OKKI": ["Data & Analytics"],
    "Xiaomi": ["Consumer"],
    "Yilong Hengye": ["Climate / Sustainability"],
    "Zhihu Technology": ["Consumer"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-box"):
        n = it.select_one(".portfolio-name")
        name = clean(n.get_text(" ")) if n else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        t = it.select_one(".p-type")
        sectors = [clean(t.get_text(" "))] if t and clean(t.get_text(" ")) else []
        p = it.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        a = it.select_one("a.outlink[href]")
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
