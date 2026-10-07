#!/usr/bin/env python3
"""Golden Ventures portfolio scraper -> goldenventures_companies.json
Source: https://www.golden.ventures/portfolio — Webflow CMS list, paginated
via ?<hash>_page=N. Each card: description, category, location, Active/Exited
label and visible Acquired / IPO badges. Each /portfolio/<slug> page adds the
leaders (founders), Year Invested, location and a "Visit Site" link.
Not to be confused with Golden Gate Ventures (goldengate_companies.json) — a
separate Singapore firm.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, tags_for, label_after, year_of, carry_forward_descriptions, apply_tag_overrides

SOURCE_URL = "https://www.golden.ventures/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "goldenventures_companies.json")
PRIMARY = "Golden Ventures"
SECTOR_TAG_MAP = {
    "consumer": ["Consumer"], "life sciences": ["BioTech", "Health"], "frontier": ["Deeptech / Robotics / AR/VR"],
    "crypto": ["Web3 / Crypto"], "fintech": ["FinTech / Insurance"], "media": ["Gaming / Media / Entertainment"],
    "food": ["CPG"], "esports & gaming": ["Gaming / Media / Entertainment"],
    "manufacturing": ["Deeptech / Robotics / AR/VR"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Barley": ["Future of Work"],
    "BenchSci": ["BioTech", "Health"],
    "Brightwheel": ["Consumer"],
    "Carbonated": ["Gaming / Media / Entertainment"],
    "Channel 1": ["Gaming / Media / Entertainment"],
    "Deck": ["Cybersecurity", "Dev Tools / Cloud", "Climate / Sustainability"],
    "Mangrove": ["FinTech / Insurance", "Climate / Sustainability"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".portfolio-company"):
            a = it.select_one("a[href]")
            t = it.select_one(".portfolio__title")
            name = clean(t.get_text(" ")) if t else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            g = lambda sel: clean(it.select_one(sel).get_text(" ")) if it.select_one(sel) else None
            badges = [clean(b.get_text()) for b in it.select(".acquired:not(.w-condition-invisible)")]
            rows.append({"name": name, "href": urljoin(SOURCE_URL, a["href"]) if a else None,
                         "desc": g(".port__description"), "cat": g(".port__category"),
                         "loc": g(".port__location"), "label": g(".port__stage"), "badges": [b for b in badges if b]})
    if limit:
        rows = rows[:limit]
    details = fetch_many([r["href"] for r in rows if r["href"]])
    out = []
    for r in rows:
        founders, year, url, loc = [], None, None, r["loc"]
        html = details.get(r["href"])
        if html:
            ds = BeautifulSoup(html, "html.parser")
            st = list(ds.stripped_strings)
            founders = [clean(x) for x in re.split(r",| & | and ", label_after(st, "LEADERS") or "") if clean(x)]
            year = year_of(label_after(st, "Year Invested"))
            loc = loc or label_after(st, "Location")
            for x in ds.select("a[href^=http]"):
                if clean(x.get_text()) and "visit site" in x.get_text().lower():
                    url = x["href"].strip()
                    break
        badges = r["badges"]
        if "Acquired" in badges:
            status = "acquired"
        elif r["label"] == "Active" or "IPO" in badges:
            status = "active"
        elif r["label"] == "Exited":
            status = "acquired"
        else:
            status = None
        sectors = [r["cat"]] if r["cat"] else []
        out.append({
            "company_name": r["name"],
            "description": r["desc"],
            "company_url": url,
            "company_profile_url": r["href"],
            "status": status,
            "site_status": r["label"],
            "exit_badges": badges,
            "first_invested": year,
            "location": loc,
            "founders": founders,
            "sectors": sectors,
            "everywhere_tags": tags_for(r["name"], r["desc"], sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "first_invested", "location", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
