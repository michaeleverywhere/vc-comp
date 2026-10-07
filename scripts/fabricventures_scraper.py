#!/usr/bin/env python3
"""Fabric Ventures portfolio scraper -> fabricventures_companies.json
Source: https://www.fabric.vc/portfolio — Webflow (Finsweet list fields),
paginated with ?7365779c_page=N. Cards carry name, open-web sector, status,
investment stage, description, country, year and region; each
/portfolios/<slug> detail page adds the company website and Key People.
Status mapping (raw kept in site_status): Private / Liquid -> active,
M&A -> acquired, Closed -> null. "M&A" in the stage field is not a round.
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, tags_for, stage_label, clean_url, carry_forward_descriptions, apply_tag_overrides

SOURCE_URL = "https://www.fabric.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fabricventures_companies.json")
PRIMARY = "Fabric Ventures"
STATUS = {"private": "active", "liquid": "active", "m&a": "acquired"}
SECTOR_TAG_MAP = {  # Fabric is a Web3-only investor; sector labels are Web3 categories
    "finance": ["Web3 / Crypto", "FinTech / Insurance"], "payments": ["Web3 / Crypto", "FinTech / Insurance"],
    "infrastructure": ["Web3 / Crypto", "Dev Tools / Cloud"], "gaming": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "culture": ["Web3 / Crypto", "Gaming / Media / Entertainment"], "work": ["Web3 / Crypto", "Future of Work"],
    "commerce": ["Web3 / Crypto", "Consumer"], "ecosystem": ["Web3 / Crypto"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Crunch DAO": ["Web3 / Crypto", "Data & Analytics"],
    "Decentraland": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "Flashbots": ["Web3 / Crypto", "Dev Tools / Cloud"],
    "Loop Crypto": ["Web3 / Crypto", "FinTech / Insurance", "Consumer"],
    "Magicave": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "Messari": ["Web3 / Crypto", "Future of Work"],
    "Nazare": ["Web3 / Crypto", "Dev Tools / Cloud"],
    "Northstake": ["Web3 / Crypto", "FinTech / Insurance", "Cybersecurity"],
    "Quantoz Payments": ["Web3 / Crypto", "FinTech / Insurance"],
    "Storygrounds": ["Web3 / Crypto", "Gaming / Media / Entertainment", "Consumer"],
    "Urban": ["Consumer", "Health"],
    "Yellowcard": ["Web3 / Crypto", "FinTech / Insurance"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    cards, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".collection-item-4"):
            f = {x.get("fs-list-field"): clean(x.get_text(" ")) for x in it.select("[fs-list-field]")}
            name = f.get("name")
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            a = it.select_one("a.portfolio_card-link")
            d = it.select_one(".portfolio_card-description")
            cards.append((name, f, clean(d.get_text(" ")) if d else None, urljoin(SOURCE_URL, a["href"]) if a else None))
            if limit and len(cards) >= limit:
                break
    details = fetch_many([c[3] for c in cards if c[3]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for name, f, desc, prof in cards:
        site, people, tagline = None, [], None
        h = details.get(prof)
        if h:
            s = BeautifulSoup(h, "html.parser")
            a = s.select_one("a.portfoliopage_card-link[href^=http]")
            site = clean_url(a["href"]) if a else None
            for p in s.select(".portfoliopage_keypeople .portfoliopage_people-content"):
                pn = p.select_one(".portfoliopage_person")
                pr = p.select_one(".portfoliopage_person-role")
                if pn and clean(pn.get_text()):
                    people.append({"name": clean(pn.get_text()), "role": clean(pr.get_text()) if pr else None})
        raw_status, raw_stage, sector = f.get("status"), f.get("investment-stage"), f.get("open-web-sector")
        sectors = [sector] if sector else []
        year = f.get("year")
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "company_profile_url": prof,
            "status": STATUS.get((raw_status or "").lower()),
            "site_status": raw_status,
            "stage": stage_label(raw_stage) if raw_stage and raw_stage.lower() != "m&a" else None,
            "first_invested": year if year and year.isdigit() else None,
            "location": f.get("country"),
            "region": f.get("region"),
            "key_people": people,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in carry_forward_descriptions(out, OUT):
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r.get("sectors"), SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "location", "key_people", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
