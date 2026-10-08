#!/usr/bin/env python3
"""East Ventures portfolio scraper -> eastventures_companies.json
Source: https://east.vc/portfolio/ — WordPress; the portfolio grid is the
`portfolio` custom post type, read from the public WP REST API
(/wp-json/wp/v2/portfolio) with its taxonomies resolved by id:
portfolio-country (HQ country), portfolio-stages (Seed / Growth — the East
Ventures program the company sits in; only "Seed" is a funding round),
portfolio-status (Active / Exit / Inactive / Past ...) and portfolio-vertical.
Description = the post content as published on east.vc. The site publishes
no company website links, so company_url stays blank (never guessed).
Status: Active -> active; Exit -> acquired (raw kept in site_status).
"""
import html, json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, html_text, tags_for, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://east.vc/portfolio/"
API = "https://east.vc/wp-json/wp/v2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "eastventures_companies.json")
PRIMARY = "East Ventures"
SECTOR_TAG_MAP = {
    "agritech": ["CPG", "Climate / Sustainability"], "blockchain": ["Web3 / Crypto"],
    "climate tech": ["Climate / Sustainability"], "commerce": ["Consumer"], "d2c": ["Consumer", "CPG"],
    "edtech": ["Future of Work"], "f&b": ["CPG"], "fintech": ["FinTech / Insurance"],
    "healthtech": ["Health"], "logistics": ["Logistics / Supply Chain"], "saas": ["Future of Work"],
}
STATUS = {"active": "active", "exit": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "3Minute": ["Gaming / Media / Entertainment"],
    "Adskom": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "alu": ["Gaming / Media / Entertainment"],
    "Anydoor": ["Future of Work"],
    "Anyplace": ["PropTech", "Consumer"],
    "AnyRoad": ["Data & Analytics"],
    "Artawana": ["FinTech / Insurance", "Consumer"],
    "Artloft": ["Consumer"],
    "Asian Surf Cooperative": ["Gaming / Media / Entertainment"],
    "Avium": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "BerryKitchen": ["Consumer", "CPG"],
    "Bioma": ["Consumer"],
    "Bizreach": ["Future of Work"],
    "Bridestory": ["Consumer"],
    "Campfire": ["FinTech / Insurance", "Consumer"],
    "Chatbook (previously Hecto Inc)": ["Future of Work"],
    "Copra": ["Web3 / Crypto", "FinTech / Insurance"],
    "Cumi": ["Consumer"],
    "DIRIGIO": ["Consumer"],
    "Eatsy": ["Consumer", "FinTech / Insurance"],
    "Elephantech Inc.": ["Deeptech / Robotics / AR/VR"],
    "Emostyle": ["Health"],
    "Fivot": ["FinTech / Insurance"],
    "Flier": ["Gaming / Media / Entertainment"],
    "Flock": ["Gaming / Media / Entertainment"],
    "Fresh Factory": ["Logistics / Supply Chain", "Consumer"],
    "Fukurou Labo": ["Gaming / Media / Entertainment"],
    "Fuse": ["FinTech / Insurance"],
    "GarageBank": ["FinTech / Insurance", "Consumer"],
    "Global Way Lab (previously Lelele)": ["Consumer"],
    "GREENS": ["CPG", "Climate / Sustainability"],
    "Hoodline": ["Gaming / Media / Entertainment"],
    "IDN": ["Gaming / Media / Entertainment"],
    "iGrow": ["FinTech / Insurance", "Climate / Sustainability"],
    "Japan Info (previously Grood)": ["Dev Tools / Cloud"],
    "Jurnal": ["FinTech / Insurance"],
    "Justika": ["RegTech/Gov/Legal", "Consumer"],
    "Kanmu": ["FinTech / Insurance"],
    "Kaumo": ["Gaming / Media / Entertainment", "Consumer"],
    "Kyberlife": ["Logistics / Supply Chain", "Health"],
    "Laugh Tech": ["Gaming / Media / Entertainment"],
    "Libz Career": ["Future of Work"],
    "LimaKilo": ["Logistics / Supply Chain", "Consumer"],
    "LUUP 株式会社": ["Transportation / Mobility", "Consumer"],
    "MAKA Motors": ["Transportation / Mobility", "Climate / Sustainability"],
    "Market Drive": ["Consumer"],
    "Medigo": ["Health"],
    "Meeting.ai": ["Future of Work"],
    "Mesh Bio": ["Health", "Data & Analytics"],
    "Mighty Jaxx": ["Consumer", "CPG"],
    "Monstarlab": ["Dev Tools / Cloud"],
    "MOOIMOM": ["Consumer", "CPG"],
    "Ohdio": ["Consumer"],
    "Orori": ["Consumer", "CPG"],
    "Pocket": ["FinTech / Insurance", "Consumer"],
    "Prinzio": ["Consumer"],
    "Promoote": ["Consumer"],
    "Quan": ["Gaming / Media / Entertainment"],
    "ROXX": ["Future of Work"],
    "Saleshub": ["Future of Work"],
    "Siiibo": ["FinTech / Insurance"],
    "Sorajima": ["Gaming / Media / Entertainment"],
    "Sweet Escape": ["Consumer"],
    "Sxored": ["FinTech / Insurance", "Data & Analytics"],
    "Timers": ["Consumer"],
    "Traveloka": ["Consumer", "Transportation / Mobility", "FinTech / Insurance"],
    "Waygo": ["Consumer"],
    "Wizleap": ["FinTech / Insurance"],
    "Xendit": ["FinTech / Insurance", "Dev Tools / Cloud"],
}


def terms(tax):
    out, page = {}, 1
    while True:
        d = fetch(f"{API}/{tax}?per_page=100&page={page}", as_json=True)
        for t in d:
            out[t["id"]] = clean(html.unescape(t["name"]))
        if len(d) < 100:
            return out
        page += 1


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    tx = {t: terms(t) for t in ("portfolio-country", "portfolio-stages", "portfolio-status", "portfolio-vertical")}
    posts, page = [], 1
    while True:
        d = fetch(f"{API}/portfolio?per_page=100&page={page}&_fields=id,slug,link,title,content,portfolio-country,portfolio-stages,portfolio-status,portfolio-vertical", as_json=True)
        posts += d
        if len(d) < 100:
            break
        page += 1
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in sorted(posts, key=lambda x: html.unescape(x["title"]["rendered"]).lower()):
        name = clean(html.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = html_text(p["content"]["rendered"])
        names = lambda tax: [tx[tax][i] for i in p.get(tax) or [] if i in tx[tax]]
        countries, stages, statuses, verticals = (names(t) for t in ("portfolio-country", "portfolio-stages", "portfolio-status", "portfolio-vertical"))
        status = next((STATUS[s.lower()] for s in statuses if s.lower() in STATUS), None)
        if "Exit" in statuses:
            status = "acquired"
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "company_profile_url": p.get("link"),
            "status": status,
            "site_status": ", ".join(statuses) or None,
            "portfolio_stage": ", ".join(stages) or None,
            "stage": "Seed" if stages == ["Seed"] else None,
            "location": ", ".join(countries) or None,
            "sectors": [v for v in verticals if v != "Others"],
            "everywhere_tags": tags_for(name, desc, verticals, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
