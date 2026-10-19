#!/usr/bin/env python3
"""Rose Street Capital portfolio scraper -> rosestreetcapital_companies.json
Source: https://www.rosestreetcapital.com/portfolio — Svelte table (client-rendered, read via
headless Chrome): company name, website, Rose Street industry label and the site's own
"Exit" note."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.rosestreetcapital.com/portfolio"
PRIMARY = "Rose Street Capital"
ZW = re.compile("[\u200b-\u200f\u2060\ufeff]")
SECTOR_MAP = {"food": ["CPG", "Consumer"], "fintech": ["FinTech / Insurance"], "personal care": ["CPG", "Consumer"],
              "health & wellness": ["Health", "Consumer"], "marketplace": ["Consumer"], "ai": [],
              "beauty": ["CPG", "Consumer"], "podcast": ["Gaming / Media / Entertainment"], "data": ["Data & Analytics"],
              "healthcare": ["Health"], "robotics": ["Deeptech / Robotics / AR/VR"], "beverage": ["CPG", "Consumer"],
              "apparel": ["Consumer"], "pet": ["Consumer"], "software": [], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(ZW.sub("", dom(SOURCE_URL, 15000, min_len=10000)), "html.parser")
    out = []
    for a in s.select("a.table-row[href]"):
        note = a.select_one(".acq-note")
        note_txt = clean(note.get_text(" ", strip=True)) if note else None
        if note:
            note.extract()
        for arr in a.select(".link-arrow"):
            arr.extract()
        spans = [clean(x.get_text(" ", strip=True)) for x in a.find_all("span", recursive=False)]
        spans = [x for x in spans if x]
        if not spans:
            continue
        name, ind = spans[0], (spans[1] if len(spans) > 1 else None)
        href = a["href"].strip()
        out.append(rec(name, None, href if href.startswith("http") and not is_social(href) else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[ind] if ind else [], sector_map=SECTOR_MAP,
                       status="exited" if note_txt and note_txt.lower() == "exit" else "active"))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Rose Street Capital companies")
    finish(out, "rosestreetcapital", ("company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
