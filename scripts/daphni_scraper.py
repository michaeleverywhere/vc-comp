#!/usr/bin/env python3
"""Daphni portfolio scraper -> daphni_companies.json
Source: https://www.daphni.com/portfolio — Webflow + Finsweet list, server-side
pagination ?5858938c_page=N (24/page). Each card carries state (active/exited),
"invested in <year>", name, sector(s), Daphni fund vehicle, founders and the
company website. Daphni publishes no per-company description, stage or
location, so tagging runs on name + Daphni sector labels.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://www.daphni.com/portfolio"
PAGE_PARAM = "5858938c_page"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "daphni_companies.json")
PRIMARY = "Daphni"
SECTOR_TAG_MAP = {
    "energy": ["Climate / Sustainability"], "climate": ["Climate / Sustainability"],
    "sustainability": ["Climate / Sustainability"], "food": ["CPG", "Climate / Sustainability"],
    "health": ["Health"], "healthcare": ["Health"], "biotech": ["BioTech"], "medtech": ["Health"],
    "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
    "saas": ["Dev Tools / Cloud"], "software": ["Dev Tools / Cloud"], "infrastructure": ["Dev Tools / Cloud"],
    "devtools": ["Dev Tools / Cloud"], "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"],
    "data": ["Data & Analytics"], "deeptech": ["Deeptech / Robotics / AR/VR"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "robotics": ["Deeptech / Robotics / AR/VR"], "space": ["Deeptech / Robotics / AR/VR"], "industry": ["Deeptech / Robotics / AR/VR"],
    "mobility": ["Transportation / Mobility"], "logistics": ["Logistics / Supply Chain"],
    "consumer": ["Consumer"], "retail": ["Consumer"], "e-commerce": ["Consumer"], "marketplace": ["Consumer"],
    "education": ["Consumer"], "edtech": ["Consumer"], "media": ["Gaming / Media / Entertainment"],
    "gaming": ["Gaming / Media / Entertainment"], "entertainment": ["Gaming / Media / Entertainment"],
    "real estate": ["PropTech"], "proptech": ["PropTech"], "construction": ["PropTech"],
    "future of work": ["Future of Work"], "hr": ["Future of Work"], "web3": ["Web3 / Crypto"],
    "crypto": ["Web3 / Crypto"], "legal": ["RegTech/Gov/Legal"], "govtech": ["RegTech/Gov/Legal"],
    "mobile app": ["Consumer"], "travel": ["Consumer"], "cyber": ["Cybersecurity"],
}


def fix_mojibake(t):
    if t and "Ã" in t:
        try:
            return t.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return t
    return t


def previous_descriptions():
    """Daphni cards carry no description; blurbs are back-filled from each
    company's own website by scripts/fill_descriptions_web.py. Carry them
    forward by name so a re-scrape doesn't wipe them."""
    try:
        with open(OUT, encoding="utf-8") as fh:
            return {(r.get("company_name") or "").lower(): r.get("description")
                    for r in json.load(fh) if r.get("description")}
    except (OSError, ValueError):
        return {}

# Hand-assigned tags (reviewer judgment from the firm-site description; no LLM)
# for companies the keyword classifier leaves untagged. Applied only when empty.
TAG_OVERRIDES = {
    "Reduck AI": [
        "Future of Work"
    ]
}


def main():
    prev = previous_descriptions()
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen, page = [], set(), 1
    while page < 50:
        url = SOURCE_URL if page == 1 else f"{SOURCE_URL}?{PAGE_PARAM}={page}"
        soup = BeautifulSoup(fetch(url), "html.parser")
        cards = soup.select(".portfolio-list_item")
        if not cards:
            break
        for c in cards:
            nm = c.select_one('[fs-list-field="name"]')
            name = clean(nm.get_text()) if nm else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            state = c.select_one('[fs-list-field="state"]')
            state = clean(state.get_text()) if state else None
            yr = c.select_one('[fs-list-field="date"]')
            yr = clean(yr.get_text()) if yr else None
            sectors = [clean(x.get_text()) for x in c.select('[fs-list-field="sector"]') if clean(x.get_text())]
            funds = [clean(x.get_text()) for x in c.select('[fs-list-field="fund"]') if clean(x.get_text())]
            fo = c.select_one('[fs-list-field="founders"]')
            founders = [clean(x) for x in (clean(fo.get_text()) or "").split(",") if clean(x)] if fo else []
            a = c.select_one("a.portfolio-card_link-site[href]")
            site = clean(a["href"]) if a and a["href"].startswith("http") else None
            st = (state or "").lower()
            status = "active" if st == "active" else ("acquired" if st in ("exited", "exit", "acquired") else None)
            desc = fix_mojibake(prev.get(name.lower()))
            out.append({
                "company_name": name,
                "description": desc,
                "description_source": "company website (fill_descriptions_web.py)" if desc else None,
                "company_url": site,
                "status": status,
                "site_status": state,
                "stage": None,
                "first_invested": int(yr) if yr and yr.isdigit() else None,
                "location": None,
                "sectors": sectors,
                "daphni_fund": funds,
                "founders": founders,
                "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": url,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
        if limit and len(out) >= limit:
            break
        page += 1
    for rec in out:
        if not rec["everywhere_tags"] and rec["company_name"] in TAG_OVERRIDES:
            rec["everywhere_tags"] = TAG_OVERRIDES[rec["company_name"]]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "sectors", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
