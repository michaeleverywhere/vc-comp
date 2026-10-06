#!/usr/bin/env python3
"""Kindred Ventures portfolio scraper -> kindredventures_companies.json
(Kindred Ventures, San Francisco — not Kindred Capital, London, which is
kindredcapital_companies.json.)
Source: https://kindredventures.com/portfolio/ — WordPress + Search & Filter
Pro, 12 companies per page (?sf_paged=N). Each company's modal carries name,
website, country tag, an exit tag where applicable (e.g. "aqd NYSE: UBER",
"Acquired by ..."), Kindred's mission theme, description and sector tag(s).
"""
import json, os, re, sys, time
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://kindredventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kindredventures_companies.json")
PRIMARY = "Kindred Ventures"
SECTOR_TAG_MAP = {
    "consumer": ["Consumer"], "crypto/web3": ["Web3 / Crypto"], "fintech": ["FinTech / Insurance"],
    "mobility & logistics": ["Transportation / Mobility", "Logistics / Supply Chain"], "health": ["Health"],
    "healthcare": ["Health"], "climate": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"],
    "security": ["Cybersecurity"], "tools & infrastructure": ["Dev Tools / Cloud"], "gaming": ["Gaming / Media / Entertainment"],
}
ACQ = re.compile(r"(?i)\b(acquired|aqd|acq|merged with)\b")
COUNTRYISH = re.compile(r"^[A-Z][A-Za-z .,'-]+$")


def parse(html):
    s = BeautifulSoup(html, "html.parser")
    rows = []
    for m in s.select(".portfolio_company_modal_wrapper"):
        h = m.select_one(".name h3")
        name = clean(h.get_text(" ")) if h else None
        if not name:
            continue
        a = m.select_one(".top_banner .url a[href]")
        tags = [clean(t.get_text(" ")) for t in m.select(".area_custom .tag") if clean(t.get_text(" "))]
        desc_el = m.select_one(".desc")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        mission = m.select_one(".mission_wrap")
        sectors = [clean(x.get_text(" ")) for x in m.select(".tags a") if clean(x.get_text(" "))]
        rows.append({"name": name, "url": a["href"].strip() if a else None, "tags": tags, "desc": desc,
                     "mission": clean(mission.get_text(" ")) if mission else None, "sectors": sectors})
    return rows


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    allrows, seen = [], set()
    for page in range(1, 60):
        rows = parse(fetch(SOURCE_URL if page == 1 else f"{SOURCE_URL}?sf_paged={page}"))
        added = 0
        for r in rows:
            if r["name"].lower() in seen:
                continue
            seen.add(r["name"].lower())
            allrows.append(r)
            added += 1
        if not added:
            break
        if limit and len(allrows) >= limit:
            break
        time.sleep(0.4)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in allrows[:limit] if limit else allrows:
        exit_tags = [t for t in r["tags"] if ACQ.search(t) or re.search(r"(?i)\b(nyse|nasdaq|otcmkts|ipo)\b|^\$", t)]
        loc_tags = [t for t in r["tags"] if t not in exit_tags]
        acquired = any(ACQ.search(t) for t in exit_tags) or bool(re.search(r"(?i)\bacquired by\b", r["desc"] or ""))
        out.append({
            "company_name": r["name"],
            "description": r["desc"],
            "company_url": r["url"],
            "status": "acquired" if acquired else None,
            "site_status": ", ".join(exit_tags) or None,
            "location": ", ".join(loc_tags) or None,
            "mission_theme": r["mission"],
            "sectors": r["sectors"],
            "everywhere_tags": tags_for(r["name"], r["desc"], r["sectors"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
