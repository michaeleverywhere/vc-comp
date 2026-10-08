#!/usr/bin/env python3
"""BEENEXT portfolio scraper -> beenext_companies.json
Source: https://www.beenext.com/portfolio/ — WordPress + Search & Filter Pro;
the result list is server-rendered and paged with ?sf_paged=N (6 per page,
followed until empty). Each item: company name linked to its website, a
country flag (ISO code -> country), description, "Area of focus" and
"Funding" (the year BEENEXT partnered -> first_invested). No stage or status
is published, so those stay blank.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.beenext.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "beenext_companies.json")
PRIMARY = "BEENEXT"
COUNTRY = {"IN": "India", "ID": "Indonesia", "SG": "Singapore", "VN": "Vietnam", "PH": "Philippines",
           "US": "USA", "JP": "Japan", "PK": "Pakistan", "BD": "Bangladesh", "MM": "Myanmar", "NG": "Nigeria",
           "UG": "Uganda", "CA": "Canada", "TH": "Thailand", "MY": "Malaysia", "AU": "Australia", "GB": "UK",
           "KE": "Kenya", "ZA": "South Africa", "AE": "UAE", "TW": "Taiwan", "HK": "Hong Kong", "CN": "China", "KR": "South Korea"}
SECTOR_TAG_MAP = {
    "agritech": ["CPG", "Climate / Sustainability"], "climatetech": ["Climate / Sustainability"],
    "sustainability": ["Climate / Sustainability"], "cloud infra": ["Dev Tools / Cloud"], "cloud kitchen": ["CPG"],
    "d2c": ["Consumer"], "e-commerce": ["Consumer"], "edtech": ["Future of Work"], "enterprise saas": ["Future of Work"],
    "fintech": ["FinTech / Insurance"], "food tech": ["CPG"], "gaming": ["Gaming / Media / Entertainment"],
    "health tech": ["Health"], "healthtech": ["Health"], "hr tech": ["Future of Work"], "insuretech": ["FinTech / Insurance"],
    "iot": ["Deeptech / Robotics / AR/VR"], "logistics": ["Logistics / Supply Chain"], "media": ["Gaming / Media / Entertainment"],
    "mobility": ["Transportation / Mobility"], "proptech": ["PropTech"], "real estate": ["PropTech"],
    "satellite": ["Deeptech / Robotics / AR/VR"], "web3": ["Web3 / Crypto"], "analytics": ["Data & Analytics"],
    "lifestyle": ["Consumer"], "social media": ["Consumer"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Converj": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Cube": ["FinTech / Insurance"],
    "Ipaymy": ["FinTech / Insurance"],
    "Makmur": ["FinTech / Insurance"],
    "Memechat": ["Gaming / Media / Entertainment", "Consumer"],
    "Niramai": ["Health"],
    "Pasarpolis": ["FinTech / Insurance"],
    "Phi Commerce Pvt Ltd": ["FinTech / Insurance"],
    "Revv": ["Transportation / Mobility", "Consumer"],
    "Ritase.com": ["Logistics / Supply Chain", "Transportation / Mobility"],
    "SafeGold": ["FinTech / Insurance", "Consumer"],
    "Sendo": ["Consumer"],
    "Stably": ["Web3 / Crypto", "FinTech / Insurance"],
    "Trusting Social": ["FinTech / Insurance", "Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen, page = [], set(), 1
    while page < 80:
        soup = BeautifulSoup(fetch(SOURCE_URL + (f"?sf_paged={page}" if page > 1 else "")), "html.parser")
        items = soup.select(".search-filter-result-item")
        if not items:
            break
        for it in items:
            a = it.select_one("h4 a")
            name = clean(a.get_text(" ")) if a else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            href = clean(a.get("href"))
            if href and not href.lower().startswith("http") and "." in href:
                href = "https://" + href
            flag = it.select_one("em.fflag")
            code = next((c[6:] for c in (flag.get("class") or []) if c.startswith("fflag-") and len(c) == 8), None) if flag else None
            p = it.select_one(".ourportfolio_cnt > div > p")
            desc = clean(p.get_text(" ")) if p else None
            area = year = None
            for q in it.select(".ourportfolio_txt p"):
                lab = q.select_one("span")
                k = clean(lab.get_text()) if lab else None
                if lab:
                    lab.decompose()
                if k == "Area of focus":
                    area = clean(q.get_text(" "))
                elif k == "Funding":
                    year = clean(q.get_text(" "))
            areas = [clean(x) for x in re.split(r",|/", area or "") if clean(x)]
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(href),
                "location": COUNTRY.get(code, code) if code else None,
                "first_invested": int(year) if year and re.fullmatch(r"\d{4}", year) else None,
                "sectors": areas,
                "everywhere_tags": tags_for(name, desc, areas, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
        if limit and len(out) >= limit:
            break
        page += 1
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "location", "first_invested", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
