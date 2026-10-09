#!/usr/bin/env python3
"""lool ventures portfolio scraper -> lool_companies.json
Source: https://www.lool.vc/portfolio/ — WordPress theme page, fully
server-rendered. A logo grid (company name + acquired="true|false" flag)
plus one hidden detail row per company (id "<company-id>_companyRow") with
title, description, Founders, Founded in, Invested in, Acquired by /
Acquired in, website and LinkedIn.
Invested in (year) -> first_invested. Founded in -> year_founded.
Status: acquired="true" or an "Acquired by" value -> acquired; otherwise blank
(the site has no active label).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, tags_for, clean_url, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.lool.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "lool_companies.json")
PRIMARY = "lool ventures"

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Overcut": [
        "Dev Tools / Cloud"
    ],
    "Avon AI": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Zeroport": [
        "Cybersecurity",
        "Deeptech / Robotics / AR/VR"
    ],
    "LiZo.ai": [
        "PropTech",
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "ai.work": [
        "Future of Work"
    ],
    "Dono": [
        "PropTech",
        "Data & Analytics"
    ],
    "NewMoo": [
        "CPG",
        "BioTech",
        "Climate / Sustainability"
    ],
    "Unlimited Robotics": [
        "Deeptech / Robotics / AR/VR"
    ],
    "IKIDO": [
        "Logistics / Supply Chain",
        "Data & Analytics"
    ],
    "BioRaptor": [
        "BioTech",
        "Data & Analytics"
    ],
    "Beewise": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Eleos Health": [
        "Health"
    ],
    "Flip": [
        "Consumer"
    ],
    "GraphiteRx": [
        "Health",
        "Logistics / Supply Chain"
    ],
    "Inner Cosmos": [
        "Health",
        "BioTech"
    ],
    "Kidoz": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Superlegal": [
        "RegTech/Gov/Legal"
    ],
    "Lightico": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Mabaya": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "MarketMan": [
        "Logistics / Supply Chain",
        "FinTech / Insurance"
    ],
    "Medisafe": [
        "Health"
    ],
    "NeoLogic": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Sensibo": [
        "Climate / Sustainability",
        "PropTech"
    ],
    "Shopial": [
        "Consumer"
    ],
    "SiteAware": [
        "PropTech",
        "Deeptech / Robotics / AR/VR"
    ],
    "Talenya": [
        "Future of Work"
    ],
    "Voca.ai": [
        "Future of Work"
    ],
    "XTEND": [
        "Deeptech / Robotics / AR/VR"
    ],
    "ZooZ": [
        "FinTech / Insurance"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch_response(SOURCE_URL).content.decode("utf-8", "replace")
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for tile in soup.select("div.logowrapper[company-id]"):
        cid = tile["company-id"]
        nm = tile.select_one(".companyname")
        name = clean(nm.get_text(" ")) if nm else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        row = soup.find(id=f"{cid}_companyRow")
        info, desc, site = {}, None, None
        if row:
            d = row.select_one(".company-single-description")
            desc = clean(d.get_text(" ")) if d else None
            if desc and desc.lower() == "stealth":  # placeholder, not a description
                desc = None
            for t in row.select(".single-company-details-title"):
                v = t.find_next_sibling("p")
                info[clean(t.get_text(" ")).lower()] = clean(v.get_text(" ")) if v else None
            a = row.select_one("a.btn[href^=http]")
            site = a["href"] if a else None
        acq = info.get("acquired by")
        acquired = tile.get("acquired") == "true" or bool(acq)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(site),
            "company_profile_url": tile.get("company-url"),
            "status": "acquired" if acquired else None,
            "acquirer": acq,
            "exit_year": year_of(info.get("acquired in")),
            "first_invested": year_of(info.get("invested in")),
            "year_founded": year_of(info.get("founded in")),
            "founders": [clean(x) for x in re.split(r",| & ", info.get("founders") or "") if clean(x)],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "acquirer", "first_invested", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
