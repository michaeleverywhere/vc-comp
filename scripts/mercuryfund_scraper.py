#!/usr/bin/env python3
"""Mercury Fund portfolio scraper -> mercuryfund_companies.json
Source: https://www.mercuryfund.com/portfolio — Webflow, one page with four CMS
lists: all companies (with a data-filter sector), "Recent funding rounds",
"Current investments" and "Exits". Each item embeds its modal: description,
"Visit Website" link, Headquarters, Founders / Leadership (name, title) and
the Mercury Team. The company name is the card's `logo` attribute.
Status: listed under Current investments -> active; under Exits -> acquired
(raw "Exit" kept in site_status; the site does not split M&A vs IPO).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, label_after, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.mercuryfund.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "mercuryfund_companies.json")
PRIMARY = "Mercury Fund"
SECTOR_TAG_MAP = {
    "retail & supplychain": ["Logistics / Supply Chain"], "energy & industrial": ["Climate / Sustainability"],
    "fintech": ["FinTech / Insurance"], "healthcare": ["Health"], "security & devops": ["Cybersecurity", "Dev Tools / Cloud"],
    "defense": ["RegTech/Gov/Legal", "Deeptech / Robotics / AR/VR"],
}


def parse_item(it):
    card = it.select_one(".portfolio-card[logo]")
    name = clean(card.get("logo")) if card else None
    if not name:
        return None
    m = it.select_one(".portfolio-current-modal-wrapper")
    d = m.select_one(".text-block-12") if m else None
    a = m.select_one("a[href^=http]") if m else None
    st = list(m.stripped_strings) if m else []
    lead = []
    for blk in (m.select(".div-block-25") if m else []):
        head = blk.select_one(".text-block-13")
        if head and clean(head.get_text()).lower().startswith("founders"):
            lead = [clean(p.get_text(" ")) for p in blk.select(".w-richtext p") if clean(p.get_text(" "))]
    team = [clean(x.get_text()) for x in (m.select(".mercury-team .text-block-15") if m else []) if clean(x.get_text())]
    return {"name": name, "desc": clean(d.get_text(" ")) if d else None, "url": clean_url(a["href"]) if a else None,
            "hq": label_after(st, "Headquarters"), "leadership": lead, "team": team,
            "sector": clean(it.get("data-filter"))}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "BitGo": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Koupon": ["Consumer", "Data & Analytics"],
    "Satsuma": ["Logistics / Supply Chain", "Dev Tools / Cloud", "Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    recs, order, current, exits = {}, [], set(), set()
    for w in soup.select(".collection-list-wrapper-3"):
        sib = w.find_previous_sibling()
        label = clean(sib.get_text(" ")).lower() if sib else "all"
        for it in w.select(":scope > .w-dyn-items > .w-dyn-item"):
            r = parse_item(it)
            if not r:
                continue
            key = r["name"].lower()
            if key not in recs:
                recs[key] = r
                order.append(key)
            elif r["sector"] and not recs[key]["sector"]:
                recs[key]["sector"] = r["sector"]
            if label.startswith("current"):
                current.add(key)
            elif label.startswith("exit"):
                exits.add(key)
    out = []
    for key in order:
        r = recs[key]
        sectors = [r["sector"]] if r["sector"] and r["sector"] != "Others" else []
        out.append({
            "company_name": r["name"],
            "description": r["desc"],
            "company_url": r["url"],
            "status": "acquired" if key in exits else ("active" if key in current else None),
            "site_status": "Exit" if key in exits else ("Current" if key in current else None),
            "location": r["hq"],
            "founders_leadership": r["leadership"],
            "mercury_team": r["team"],
            "sectors": sectors,
            "everywhere_tags": tags_for(r["name"], r["desc"], sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "founders_leadership", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
