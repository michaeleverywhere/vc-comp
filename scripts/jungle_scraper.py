#!/usr/bin/env python3
"""Jungle Ventures portfolio scraper -> jungle_companies.json
Source: https://www.jungle.vc/portfolio — Webflow, all cards server-rendered
(.c-portfolio_item) with an embedded modal: Unicorn / IPO / Exited badges
(set when not `w-condition-invisible`), sector (Consumer/B2B/Software), region,
stage at first investment, headline + description, website, category chips,
investment year, Jungle team and founders.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, round_label

SOURCE_URL = "https://www.jungle.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "jungle_companies.json")
PRIMARY = "Jungle Ventures"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "health": ["Health"],
    "healthtech": ["Health"], "edtech": ["Consumer"], "e-commerce": ["Consumer"], "ecommerce": ["Consumer"],
    "d2c": ["CPG", "Consumer"], "logistics": ["Logistics / Supply Chain"], "supply chain": ["Logistics / Supply Chain"],
    "mobility": ["Transportation / Mobility"], "proptech": ["PropTech"], "real estate": ["PropTech"],
    "gaming": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
    "web3": ["Web3 / Crypto"], "crypto": ["Web3 / Crypto"], "climate": ["Climate / Sustainability"],
    "agritech": ["Climate / Sustainability"], "hrtech": ["Future of Work"], "saas": ["Dev Tools / Cloud"],
    "software": ["Dev Tools / Cloud"], "cybersecurity": ["Cybersecurity"], "travel": ["Consumer"],
}


def visible(el):
    return bool(el) and "w-condition-invisible" not in (el.get("class") or [])


def modal_field(card, label):
    for lab in card.select(".c-modal_item .cc-semi-bold"):
        if clean(lab.get_text()) == label:
            box = lab.parent
            vals = []
            for v in box.find_all(["div", "a"], recursive=True):
                if v is lab or "cc-semi-bold" in (v.get("class") or []):
                    continue
                if not visible(v) or "w-dyn-bind-empty" in (v.get("class") or []):
                    continue
                if v.find(["div", "a"]):
                    continue
                t = clean(v.get_text())
                if t and t not in vals:
                    vals.append(t)
            href = None
            a = box.select_one("a[href^='http']")
            if a:
                href = a["href"]
            return vals, href
    return [], None

# Hand-assigned tags (reviewer judgment from the firm-site description; no LLM)
# for companies the keyword classifier leaves untagged. Applied only when empty.
TAG_OVERRIDES = {
    "Walko Food": [
        "CPG",
        "Consumer"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in soup.select(".c-portfolio_item"):
        nm = c.select_one("[portfolioname]")
        name = clean(nm.get_text()) if nm else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        tagwrap = c.select_one(":scope > .c-tag-wrap")
        unicorn = visible(tagwrap.select_one(".c-unicorn")) if tagwrap else False
        ipo = visible(tagwrap.select_one(".c-ipo")) if tagwrap else False
        exited = visible(tagwrap.select_one(".c-exited")) if tagwrap else False
        g = lambda sel: clean(c.select_one(sel).get_text()) if c.select_one(sel) else None
        sector, region, stage_raw = g(".c-data_sector"), g(".c-data_region"), g(".c-data_stage")
        headline = g(".c-modal_desc .c-title-4")
        desc = g(".c-modal_desc .c-text-2")
        _, website = modal_field(c, "Website")
        cats, _ = modal_field(c, "Category")
        yrs, _ = modal_field(c, "Investment Year")
        stg, _ = modal_field(c, "Investment Stage")
        team, _ = modal_field(c, "Jungle team")
        founders, _ = modal_field(c, "Founders")
        stage_raw = (stg[0] if stg else None) or stage_raw
        year = next((int(y) for y in yrs if y.isdigit()), None)
        if exited and not ipo:
            status = "acquired"
        else:
            status = "active"
        sectors = []
        for s_ in [sector] + cats:
            if s_ and s_ not in sectors:
                sectors.append(s_)
        out.append({
            "company_name": name,
            "description": desc or headline,
            "headline": headline,
            "company_url": clean(website),
            "status": status,
            "site_status": ", ".join(x for x, f in (("Unicorn", unicorn), ("IPO", ipo), ("Exited", exited)) if f) or None,
            "unicorn": unicorn,
            "ipo": ipo,
            "exited": exited,
            "stage": round_label(stage_raw),
            "investment_stage_raw": stage_raw,
            "first_invested": year,
            "location": region,
            "sectors": sectors,
            "jungle_team": team,
            "founders": founders,
            "everywhere_tags": tags_for(name, " ".join(x for x in (headline, desc) if x), [s for s in sectors if s not in ("B2B", "Consumer", "Tech")], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    for rec in out:
        if not rec["everywhere_tags"] and rec["company_name"] in TAG_OVERRIDES:
            rec["everywhere_tags"] = TAG_OVERRIDES[rec["company_name"]]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "site_status", "stage", "first_invested", "location",
              "sectors", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
