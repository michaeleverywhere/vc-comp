#!/usr/bin/env python3
"""Golden Gate Ventures portfolio scraper -> goldengate_companies.json
Source: https://www.goldengate.vc/portfolio — Webflow, every card server-rendered
(no pagination): name, IPO / Exit / Closed badges (a badge is set when it lacks
`w-condition-invisible`), countries list and industry string. Each
/portfolio/<slug> detail page adds the headline, website, founders (name — role),
Golden Gate investment team and long description. No stage or invest year.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for

BASE = "https://www.goldengate.vc"
SOURCE_URL = BASE + "/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "goldengate_companies.json")
PRIMARY = "Golden Gate Ventures"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
    "healthtech": ["Health"], "healthcare": ["Health"], "edtech": ["Consumer"],
    "e-commerce": ["Consumer"], "ecommerce": ["Consumer"], "consumer": ["Consumer"],
    "logistics": ["Logistics / Supply Chain"], "supply chain": ["Logistics / Supply Chain"],
    "mobility": ["Transportation / Mobility"], "proptech": ["PropTech"], "real estate": ["PropTech"],
    "gaming": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
    "entertainment": ["Gaming / Media / Entertainment"], "blockchain": ["Web3 / Crypto"],
    "web3": ["Web3 / Crypto"], "crypto": ["Web3 / Crypto"], "climate": ["Climate / Sustainability"],
    "sustainability": ["Climate / Sustainability"], "agritech": ["Climate / Sustainability"],
    "hr tech": ["Future of Work"], "hrtech": ["Future of Work"], "saas": ["Dev Tools / Cloud"],
    "b2b saas": ["Dev Tools / Cloud"], "enterprise": ["Dev Tools / Cloud"], "cybersecurity": ["Cybersecurity"],
    "deeptech": ["Deeptech / Robotics / AR/VR"], "robotics": ["Deeptech / Robotics / AR/VR"],
    "fmcg": ["CPG"], "f&b": ["CPG"], "food": ["CPG"], "legaltech": ["RegTech/Gov/Legal"],
}


def badge(card, cls):
    el = card.select_one("." + cls)
    return bool(el) and "w-condition-invisible" not in (el.get("class") or [])


def box(d, title):
    for t in d.select(".box-title"):
        if clean(t.get_text()) == title:
            vals = [clean(s) for s in t.parent.stripped_strings]
            vals = [v for v in vals if v and v != title]
            return vals
    return []

# Hand-assigned tags (reviewer judgment from the firm-site description; no LLM)
# for companies the keyword classifier leaves untagged. Applied only when empty.
TAG_OVERRIDES = {
    "Tarjama": [
        "Future of Work"
    ],
    "Nybl": [
        "Dev Tools / Cloud"
    ],
    "Bucketplace": [
        "Consumer",
        "PropTech"
    ],
    "Bootloader": [
        "Deeptech / Robotics / AR/VR",
        "Gaming / Media / Entertainment"
    ],
    "Find Ai": [
        "Data & Analytics"
    ],
    "Locofy": [
        "Dev Tools / Cloud"
    ],
    "Cinnamon": [
        "Future of Work"
    ],
    "Skelterlabs": [
        "Dev Tools / Cloud"
    ],
    "Popapp": [
        "Dev Tools / Cloud"
    ],
    "PowerCore": [
        "Data & Analytics"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for c in soup.select("div.portfolio-card"):
        a = c.select_one("a.portfolio-card-link[href]")
        h = c.select_one("h3")
        name = clean(h.get_text()) if h else None
        if not name or not a or name.lower() in seen:
            continue
        seen.add(name.lower())
        ind = c.select_one(".industry")
        rows.append({
            "name": name, "profile": urljoin(BASE, a["href"]),
            "ipo": badge(c, "portfolio-card-ipo"), "exit": badge(c, "portfolio-card-exit"),
            "closed": badge(c, "portfolio-card-closed"),
            "countries": [clean(x.get_text()) for x in c.select(".countries .w-dyn-item") if clean(x.get_text())],
            "industry": [s.strip() for s in (clean(ind.get_text()) or "").split(",") if s.strip()] if ind else [],
        })
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        h1 = d.select_one("h1.big-title")
        headline = clean(h1.get_text()) if h1 else None
        w = d.select_one(".social-media-holder-1 a[href]")
        website = clean(w["href"]) if w else None
        rt = d.select_one(".rich-text")
        desc = clean(rt.get_text(" ")) if rt else None
        founders_raw = box(d, "Founders")
        founders, i = [], 0
        while i < len(founders_raw):
            nm = founders_raw[i]
            role = None
            if i + 1 < len(founders_raw) and founders_raw[i + 1].startswith("—"):
                role = clean(founders_raw[i + 1].lstrip("— "))
                i += 1
            founders.append({"name": nm, "role": role})
            i += 1
        team = box(d, "Investment Team")
        if r["exit"]:
            status, site_status = "acquired", "Exit"
        elif r["ipo"]:
            status, site_status = "active", "IPO"
        elif r["closed"]:
            status, site_status = None, "Closed"
        else:
            status, site_status = "active", None
        countries = [x for x in r["countries"] if x.lower() != "rest of the world"]
        out.append({
            "company_name": r["name"],
            "description": desc or headline,
            "headline": headline,
            "company_url": website,
            "company_profile_url": r["profile"],
            "status": status,
            "site_status": site_status,
            "stage": None,
            "location": ", ".join(countries) or None,
            "countries": r["countries"],
            "sectors": r["industry"],
            "founders": founders,
            "ggv_team": team,
            "everywhere_tags": tags_for(r["name"], " ".join(x for x in (headline, desc) if x), r["industry"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for rec in out:
        if not rec["everywhere_tags"] and rec["company_name"] in TAG_OVERRIDES:
            rec["everywhere_tags"] = TAG_OVERRIDES[rec["company_name"]]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "location", "sectors", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
