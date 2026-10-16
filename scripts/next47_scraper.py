#!/usr/bin/env python3
"""Next47 (N47) portfolio scraper -> next47_companies.json
Source: https://www.n47.com/portfolio — Webflow, one server-rendered grid. Each
card carries the company name, "builders" (founders), founded year, "partnered"
(year + round, e.g. "2021, Series A"), sector, location filter and a one-line
description. Each card links to /portfolio/<slug>, whose page adds the N47
lead partner, the company's website link, and the description/builders when
the grid card leaves them out.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, year_of, stage_label, first_external_link, apply_tag_overrides

SOURCE_URL = "https://www.n47.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "next47_companies.json")
PRIMARY = "Next47"
SECTOR_TAG_MAP = {
    "security": ["Cybersecurity"], "infrastructure": ["Dev Tools / Cloud"],
    "industrial": ["Deeptech / Robotics / AR/VR"], "healthcare": ["Health"], "health": ["Health"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Alaiko": ["Logistics / Supply Chain", "Consumer"],
    "Sysdig": ["Dev Tools / Cloud", "Cybersecurity", "Transportation / Mobility"],
    "Vitally": ["Future of Work"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards, seen = [], set()
    for it in soup.select(".pf-grid-list__item a.pf-grid-item"):
        h = it.select_one("h2")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cards.append((name, it))
        if limit and len(cards) >= limit:
            break
    details = fetch_many([urljoin(SOURCE_URL, a["href"]) for _, a in cards if a.get("href")])
    out = []
    for name, it in cards:
        strings = list(it.stripped_strings)
        b = it.select_one(".pf-grid-item__builders")
        founders = [clean(x) for x in re.split(r",|&| and ", b.get_text(" ")) if clean(x)] if b else []
        founded = year_of(label_after(strings, "founded"))
        partnered = label_after(strings, "partnered")
        sector = label_after(strings, "sector")
        d = it.select_one(".pf-grid-item__description")
        desc = clean(d.get_text(" ")) if d else None
        loc = clean(it.get("data-filter-location"))
        prof = urljoin(SOURCE_URL, it["href"]) if it.get("href") else None
        website, lead = None, None
        html = details.get(prof) if prof else None
        if html:
            ds = BeautifulSoup(html, "html.parser")
            website = first_external_link(ds, ("n47.com", "next47", "website-files.com"))
            dstr = list(ds.stripped_strings)
            lead = label_after(dstr, "lead")
            rt = ds.select_one(".w-richtext")
            if not desc and rt:
                desc = clean(rt.get_text(" "))
            if not founders:
                fb = label_after(dstr, "builders")
                founders = [clean(x) for x in re.split(r",|&| and ", fb or "") if clean(x)]
            founded = founded or year_of(label_after(dstr, "founded"))
            partnered = partnered or label_after(dstr, "partnered")
            sector = sector or label_after(dstr, "sector")
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "company_profile_url": prof,
            "founders": founders,
            "founded_year": founded,
            "partnered": partnered,
            "first_invested": year_of(partnered),
            "stage": stage_label(re.sub(r"^\s*(19|20)\d{2}\s*,?\s*", "", partnered or "")),
            "sectors": sectors,
            "location": loc,
            "n47_lead": lead,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "founders", "first_invested", "stage", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
