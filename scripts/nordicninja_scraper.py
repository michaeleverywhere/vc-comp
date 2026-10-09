#!/usr/bin/env python3
"""NordicNinja portfolio scraper -> nordicninja_companies.json
Source: https://nordicninja.com/portfolio/ — server-rendered WordPress list
(27 `article.portfolio` cards). Each card has the name, a one-line summary and
keyword links: portfolio_industry (sector) and portfolio_series (the round,
Seed / Series A / Series B). Detail pages /portfolio/<slug>/ add a short
tagline, the company website and a longer "About" text.
portfolio_series -> stage (a published funding round). No dates, locations
or exit flags are published.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://nordicninja.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "nordicninja_companies.json")
PRIMARY = "NordicNinja"
SECTOR_TAG_MAP = {
    "climatetech": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"], "batteryrecycling": ["Climate / Sustainability"],
    "digital health": ["Health"], "mobility": ["Transportation / Mobility"], "autonomous": ["Deeptech / Robotics / AR/VR"],
    "web3": ["Web3 / Crypto"], "fintech": ["FinTech / Insurance"], "logistics": ["Logistics / Supply Chain"],
    "supply chain": ["Logistics / Supply Chain"], "foodtech": ["CPG"], "metaverse": ["Deeptech / Robotics / AR/VR"],
    "quantum computing": ["Deeptech / Robotics / AR/VR"], "deeptech": ["Deeptech / Robotics / AR/VR"],
    "manufacturing": ["Deeptech / Robotics / AR/VR"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Arbonics": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Bolt": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Einride": [
        "Transportation / Mobility",
        "Logistics / Supply Chain",
        "Deeptech / Robotics / AR/VR"
    ],
    "Kognic": [
        "Deeptech / Robotics / AR/VR",
        "Transportation / Mobility"
    ],
    "LiveEO": [
        "Data & Analytics",
        "Climate / Sustainability"
    ],
    "Mavenoid": [
        "Future of Work"
    ],
    "Onego": [
        "CPG",
        "BioTech"
    ],
    "Pactum": [
        "Future of Work",
        "Logistics / Supply Chain"
    ],
    "Photoncycle": [
        "Climate / Sustainability"
    ],
    "Ready Player Me": [
        "Gaming / Media / Entertainment",
        "Deeptech / Robotics / AR/VR"
    ],
    "Realeyes": [
        "Data & Analytics",
        "Gaming / Media / Entertainment"
    ],
    "Redpine": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "SEEQC": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Starship": [
        "Deeptech / Robotics / AR/VR",
        "Logistics / Supply Chain"
    ],
    "Veriff": [
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "VSParticle": [
        "Deeptech / Robotics / AR/VR"
    ],
}


def parse_detail(html):
    s = BeautifulSoup(html, "html.parser")
    m = s.find("main") or s.body or s
    site = None
    for a in m.find_all("a", href=True):
        h = a["href"]
        if h.startswith("http") and "nordicninja.com" not in urlsplit(h).netloc and re.match(r"(?i)^(www\.|https?://)?[\w-]+\.[\w.]+/?$", clean(a.get_text(" ")) or ""):
            site = h
            break
    about = None
    tab = m.select_one("#tab-1") or m.select_one("[id^=tab-1]")
    if tab:
        ps = [clean(p.get_text(" ")) for p in tab.find_all("p") if clean(p.get_text(" "))]
        about = " ".join(ps) if ps else None
    return site, about


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = soup.select("article.portfolio")
    if limit:
        cards = cards[:limit]
    hrefs = [c.select_one("a.portfolio__heading")["href"] for c in cards if c.select_one("a.portfolio__heading")]
    pages = fetch_many(hrefs)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in cards:
        h = c.select_one("a.portfolio__heading")
        if not h:
            continue
        name = clean(h.get_text(" "))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = [clean(a.get_text(" ")).rstrip(",") for a in c.select('ul.portfolio__keywords a[href*="portfolio_industry"]') if clean(a.get_text(" "))]
        series = next((clean(a.get_text(" ")) for a in c.select('ul.portfolio__keywords a[href*="portfolio_series"]')), None)
        tt = c.select_one(".portfolio__text")
        summary = clean(tt.get_text(" ")) if tt else None
        site, about = parse_detail(pages[h["href"]]) if pages.get(h["href"]) else (None, None)
        out.append({
            "company_name": name,
            "description": summary or about,
            "long_description": about,
            "company_url": clean_url(site) if site else None,
            "company_profile_url": h["href"],
            "stage": stage_label(series),
            "sectors": sectors,
            "everywhere_tags": tags_for(name, " ".join(x for x in (summary, about) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "long_description", "company_url", "stage", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
