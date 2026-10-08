#!/usr/bin/env python3
"""Wavemaker Ventures portfolio scraper -> wavemaker_companies.json
Source: https://wavemaker.vc/portfolio/ — WordPress; companies are the
`wavemaker-portfolio` custom post type, listed from the public WP REST API
with taxonomies resolved by id (operational HQ, sector, capital-raised
bucket, focus area, status Current / Exited / Past). Each
/portfolio/<slug>/ page adds the description, company website, founders and
"partnered" year (-> first_invested).
Capital Raised (US$) is published as a bucket (e.g. "1M to 5M") and kept
verbatim in total_raised. No funding round is published, so stage is blank.
Status: Current -> active; Exited -> acquired; Past (written off / no longer
held) is kept only in site_status.
"""
import html, json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, first_external_link, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://wavemaker.vc/portfolio/"
API = "https://wavemaker.vc/wp-json/wp/v2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "wavemaker_companies.json")
PRIMARY = "Wavemaker Ventures"
OWN = ("wavemaker.vc",)
TAX = ("wavemaker-portfolio-headquarter", "wavemaker-portfolio-platform-po", "portfolio_capital_raised",
       "portfolio_focus_area", "wavemaker-portfolio-status-pods", "wavemaker-portfolio-type-pods")
SECTOR_TAG_MAP = {
    "finance & insurance": ["FinTech / Insurance"], "bfsi": ["FinTech / Insurance"], "health care": ["Health"],
    "healthcare": ["Health"], "construction & real estate": ["PropTech"], "real estate & property management": ["PropTech"],
    "transportation & warehousing": ["Logistics / Supply Chain"], "supply chain": ["Logistics / Supply Chain"],
    "trade logistics & shipping": ["Logistics / Supply Chain"], "food & beverages": ["CPG"], "food & beverage": ["CPG"],
    "agriculture & forestry": ["Climate / Sustainability"], "electric power": ["Climate / Sustainability"],
    "energy & utilities": ["Climate / Sustainability"], "aerospace": ["Deeptech / Robotics / AR/VR"],
    "cybersecurity": ["Cybersecurity"], "e-commerce & retail": ["Consumer"], "media & content": ["Gaming / Media / Entertainment"],
    "mobility & transportation": ["Transportation / Mobility"], "automotive": ["Transportation / Mobility"],
    "hr & recruitment": ["Future of Work"], "education": ["Future of Work"], "military & defense": ["RegTech/Gov/Legal"],
    "pharmaceutical": ["BioTech"], "travel & tourism": ["Consumer"], "accommodation & tourism services": ["Consumer"],
}
STATUS = {"current": "active", "exited": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Advano": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Advent Integra": ["Dev Tools / Cloud", "Gaming / Media / Entertainment"],
    "Arcstone": ["Data & Analytics"],
    "Ardent Capital": ["FinTech / Insurance"],
    "Art of Click": ["Gaming / Media / Entertainment"],
    "AssetFindr": ["Data & Analytics"],
    "Beams": ["Transportation / Mobility", "Data & Analytics"],
    "Bind": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Bondle": ["Future of Work"],
    "Borneo": ["Cybersecurity", "RegTech/Gov/Legal"],
    "Canal Circle": ["FinTech / Insurance"],
    "Eazy": ["FinTech / Insurance"],
    "Gimmie": ["Consumer"],
    "Hum Capital": ["FinTech / Insurance"],
    "Lhoopa": ["PropTech", "Consumer"],
    "Media Loyal": ["Consumer"],
    "MFast": ["FinTech / Insurance"],
    "Noneaway": ["PropTech"],
    "Nugit": ["Data & Analytics"],
    "Ohai.ai": ["Consumer"],
    "Panalyt": ["Future of Work", "Data & Analytics"],
    "Pencil": ["Gaming / Media / Entertainment"],
    "Pixel Canvas": ["Deeptech / Robotics / AR/VR"],
    "Poseidon Fund": [],
    "Relativity Space": ["Deeptech / Robotics / AR/VR"],
    "SalesCandy": ["Future of Work"],
    "Saleswhale": ["Future of Work"],
    "Smartkarma": ["FinTech / Insurance", "Data & Analytics"],
    "Smove": ["Transportation / Mobility", "Consumer"],
    "Snapcart": ["Data & Analytics", "Consumer"],
    "Stylist in Pocket": ["Consumer"],
    "Transcelestial": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Vama": ["Consumer"],
    "Verihubs": ["Cybersecurity", "Dev Tools / Cloud"],
    "Wiz": ["Future of Work"],
    "Zumata": ["Consumer", "Dev Tools / Cloud"],
    "ZUZU Hospitality": ["Consumer", "Data & Analytics"],
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
    tx = {t: terms(t) for t in TAX}
    posts, page = [], 1
    while True:
        d = fetch(f"{API}/wavemaker-portfolio?per_page=100&page={page}&_fields=id,slug,link,title," + ",".join(TAX), as_json=True)
        posts += d
        if len(d) < 100:
            break
        page += 1
    posts.sort(key=lambda p: html.unescape(p["title"]["rendered"]).lower())
    if limit:
        posts = posts[:limit]
    details = fetch_many([p["link"] for p in posts], workers=6)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in posts:
        name = clean(html.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        names = lambda t: [tx[t][i] for i in p.get(t) or [] if i in tx[t]]
        hq, sector, raised, focus, status_l, types = (names(t) for t in TAX)
        desc = site = partnered = None
        founders = []
        h = details.get(p["link"])
        if h:
            s = BeautifulSoup(h, "html.parser")
            for t in s(["script", "style", "svg", "nav", "footer", "header"]):
                t.decompose()
            st = [clean(x) for x in s.body.stripped_strings if clean(x)]
            if name in st:
                i = st.index(name)
                if i + 1 < len(st) and st[i + 1] not in ("Type", "Focus Area"):
                    desc = st[i + 1]
            if "founders" in st:
                i = st.index("founders") + 1
                while i < len(st) and st[i] not in ("partnered", "exited", "You may be interested in..."):
                    founders.append(st[i])
                    i += 1
            py = label_after(st, "partnered")
            partnered = int(py) if py and re.fullmatch(r"\d{4}", py) else None
            site = clean_url(first_external_link(s, OWN))
        raw_status = ", ".join(status_l) or None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "company_profile_url": p["link"],
            "status": next((STATUS[x.lower()] for x in status_l if x.lower() in STATUS), None),
            "site_status": raw_status,
            "first_invested": partnered,
            "location": ", ".join(hq) or None,
            "total_raised": f"US${raised[0]}" if raised else None,
            "founders": [clean(x) for f in founders for x in f.split(", ") if clean(x)],
            "sectors": [x for x in sector + types if x != "Other"],
            "focus_areas": focus,
            "everywhere_tags": tags_for(name, desc, types + sector, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "first_invested", "location", "total_raised", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
