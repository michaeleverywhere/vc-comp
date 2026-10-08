#!/usr/bin/env python3
"""Kapor Capital portfolio scraper -> kaporcapital_companies.json
Source: https://www.kaporcapital.com/portfolio/ — WordPress; the filterable
grid lazy-loads 12 companies at a time, but ?current_page=N server-renders
the first N pages, so one request with a high current_page returns the full
list. Each card: name, year invested, sector and status tag (Acquired / IPO).
Each /portfolio/<slug>/ page adds the description, Founded / Invested years,
founders and the company website.
Status: Acquired -> acquired; IPO kept in site_status (status blank);
untagged companies are not labelled live by the site, so status stays blank.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, first_external_link, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.kaporcapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kaporcapital_companies.json")
PRIMARY = "Kapor Capital"
OWN = ("kaporcapital.com", "kaporfoundation.org", "kaporcenter.org", "smash.org", "rippling.com")
SECTOR_TAG_MAP = {
    "climate": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"], "environment": ["Climate / Sustainability"],
    "education": ["Future of Work"], "finance": ["FinTech / Insurance"], "food": ["CPG"], "health": ["Health"],
    "justice": ["RegTech/Gov/Legal"], "media": ["Gaming / Media / Entertainment"], "future city": ["PropTech", "Transportation / Mobility"],
    "people operations tech": ["Future of Work"], "work": ["Future of Work"], "workforce": ["Future of Work"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Asana": ["Future of Work"],
    "Bitly": ["Data & Analytics"],
    "Bridge Money": ["FinTech / Insurance"],
    "Captricity": ["Data & Analytics"],
    "Curve Health": ["Health"],
    "EdCast": ["Future of Work", "Consumer"],
    "Formlabs": ["Deeptech / Robotics / AR/VR"],
    "Gengo": ["Future of Work"],
    "Get Satisfaction": ["Future of Work"],
    "High Fidelity": ["Deeptech / Robotics / AR/VR", "Gaming / Media / Entertainment"],
    "Life360": ["Consumer"],
    "Lumi": ["Gaming / Media / Entertainment", "Consumer"],
    "Optimizely": ["Data & Analytics"],
    "Pair Team, Inc.": ["Health"],
    "Peel": ["Gaming / Media / Entertainment", "Consumer"],
    "Posterous": ["Gaming / Media / Entertainment", "Consumer"],
    "Rain": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "StyleSeek": ["Consumer"],
    "Uber": ["Transportation / Mobility", "Consumer"],
    "Uncharted": ["Dev Tools / Cloud", "Climate / Sustainability"],
    "UpLift": ["Health"],
    "Visually": ["Data & Analytics"],
    "Yobongo": ["Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL + "?current_page=100"), "html.parser")
    cards, seen = [], set()
    for it in soup.select(".portfolio-company"):
        name = clean(it.get("data-company-name")) or clean(it.select_one(".company-name").get_text(" "))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        a = it.select_one("a[href]")
        g = lambda c: clean(it.select_one(c).get_text(" ")) if it.select_one(c) else None
        cards.append(dict(name=name, prof=a["href"] if a else None, year=g(".company-year"), sector=g(".company-sector"),
                          stages=g(".funding-stages"), tag=g(".company-statuses")))
        if limit and len(cards) >= limit:
            break
    details = fetch_many([c["prof"] for c in cards if c["prof"]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for c in cards:
        desc = site = founded = None
        founders = []
        h = details.get(c["prof"])
        if h:
            s = BeautifulSoup(h, "html.parser")
            for t in s(["script", "style", "svg", "nav", "footer", "header"]):
                t.decompose()
            main_el = s.select_one("main") or s.body
            st = [clean(x) for x in main_el.stripped_strings if clean(x)]
            st = [x for x in st if not x.startswith("Skip to")]
            if st and st[0] not in ("Founded", "Invested", "Founders"):
                desc = st[0]
            fy = label_after(st, "Founded")
            founded = int(fy) if fy and re.fullmatch(r"\d{4}", fy) else None
            if "Founders" in st:
                founders = [clean(x) for x in re.split(r",| and | & ", st[st.index("Founders") + 1]) if clean(x)] if st.index("Founders") + 1 < len(st) else []
            site = clean_url(first_external_link(BeautifulSoup(h, "html.parser"), OWN))
        year = c["year"]
        tag = c["tag"]
        out.append({
            "company_name": c["name"],
            "description": desc,
            "company_url": site,
            "company_profile_url": c["prof"],
            "status": "acquired" if (tag or "").lower() == "acquired" else None,
            "site_status": tag,
            "first_invested": int(year) if year and re.fullmatch(r"\d{4}", year) else None,
            "year_founded": founded,
            "founders": founders,
            "sectors": [c["sector"]] if c["sector"] else [],
            "everywhere_tags": tags_for(c["name"], desc, [c["sector"]] if c["sector"] else [], SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "first_invested", "year_founded", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
