#!/usr/bin/env python3
"""MaC Venture Capital portfolio scraper -> mac_companies.json
Source: https://macventurecapital.com/portfolio/ — WordPress. The listing page
server-renders every company (hover card: description, CEO, MaC investors,
website; sector + region as CSS classes). Current status (Active/Acquired) is a
`stage` taxonomy only exposed through the public WP REST endpoint
/wp-json/wp/v2/portfolio_new, joined on the profile URL.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://macventurecapital.com/portfolio/"
API = "https://macventurecapital.com/wp-json/wp/v2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "mac_companies.json")
PRIMARY = "MaC Venture Capital"

SECTORS = {
    "aerospace": "Aerospace", "ai-ml": "AI/ML", "cyber-security": "Cyber Security",
    "deep-tech": "Deep Tech", "ecommerce": "eCommerce", "energy": "Energy",
    "enterprise-software": "Enterprise Software", "fintech": "Fintech",
    "healthtech": "Healthtech", "robotics": "Robotics",
    "sports-media-entertainment": "Sports, Media, & Entertainment",
    "transportation-logistics-supply-chain-and-storage": "Transportation, Logistics, Supply Chain, and Storage",
}
REGIONS = {"north-america": "North America", "africa": "Africa", "europe": "Europe",
           "asia": "Asia", "latin-america": "Latin America"}
SECTOR_TAG_MAP = {
    "aerospace": ["Deeptech / Robotics / AR/VR"],
    "cyber security": ["Cybersecurity"],
    "deep tech": ["Deeptech / Robotics / AR/VR"],
    "ecommerce": ["Consumer"],
    "energy": ["Climate / Sustainability"],
    "enterprise software": ["Dev Tools / Cloud"],
    "fintech": ["FinTech / Insurance"],
    "healthtech": ["Health"],
    "robotics": ["Deeptech / Robotics / AR/VR"],
    "sports, media, & entertainment": ["Gaming / Media / Entertainment"],
    "transportation, logistics, supply chain, and storage": ["Logistics / Supply Chain", "Transportation / Mobility"],
}
ACQ_RE = re.compile(r"(?i)\bacquired by ([^.]+?)(?: in (\d{4}))?\.")


def rest_status():
    terms = {t["id"]: t["slug"] for t in fetch(f"{API}/stage?per_page=100", as_json=True)}
    out, page = {}, 1
    while True:
        rows = fetch(f"{API}/portfolio_new?per_page=100&page={page}&_fields=link,stage", as_json=True)
        if not rows:
            break
        for r in rows:
            slugs = [terms.get(i) for i in r.get("stage") or [] if terms.get(i)]
            out[r["link"].rstrip("/")] = slugs
        if len(rows) < 100:
            break
        page += 1
    return out

# Hand-assigned tags (reviewer judgment from the firm-site description; no LLM)
# for companies the keyword classifier leaves untagged. Applied only when empty.
TAG_OVERRIDES = {
    "Bioqore": [
        "BioTech"
    ],
    "Constellation": [
        "Data & Analytics"
    ],
    "Pareto AI": [
        "Data & Analytics"
    ],
    "Seldon": [
        "Dev Tools / Cloud"
    ],
    "Taya": [
        "Consumer",
        "Deeptech / Robotics / AR/VR"
    ],
    "Yobe": [
        "Deeptech / Robotics / AR/VR"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    status_by_link = rest_status()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for li in soup.select("li.portfolio-listing__item"):
        a = li.select_one("a.portfolio-listing__title")
        name = clean(a.get_text()) if a else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        profile = a.get("href")
        cls = li.get("class") or []
        sectors = [SECTORS.get(c[4:], c[4:]) for c in cls if c.startswith("tag_")]
        region = next((REGIONS.get(c[7:], c[7:]) for c in cls if c.startswith("region_")), None)
        info = li.select_one(".portfolio-info__content")
        desc = None
        ceo, investors, website = None, [], None
        if info:
            p = info.find("p")
            desc = clean(p.get_text(" ")) if p else None
            for item in info.select(":scope > ul > li"):
                h3 = item.find("h3")
                label = clean(h3.get_text()).lower() if h3 else ""
                if label == "ceo":
                    h3.extract()
                    ceo = clean(item.get_text(" "))
                elif label == "investors":
                    investors = [clean(x.get_text()) for x in item.select("ul li") if clean(x.get_text())]
                elif label == "website":
                    w = item.select_one("a[href]")
                    website = clean(w["href"]) if w else None
        slugs = status_by_link.get((profile or "").rstrip("/"), [])
        acq = ACQ_RE.search(desc or "")
        status = "acquired" if ("acquired" in slugs or acq) else ("active" if "active" in slugs else None)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "company_profile_url": profile,
            "status": status,
            "acquirer": clean(acq.group(1)) if acq else None,
            "exit_year": int(acq.group(2)) if acq and acq.group(2) else None,
            "stage": None,
            "location": region,
            "sectors": sectors,
            "ceo": ceo,
            "mac_investors": investors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "location", "sectors", "ceo", "everywhere_tags"):
        print(f"  {k}: {sum(1 for r in out if r.get(k))}/{n}")


if __name__ == "__main__":
    main()
