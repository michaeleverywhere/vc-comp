#!/usr/bin/env python3
"""Volition Capital portfolio scraper -> volitioncapital_companies.json
Source: https://www.volitioncapital.com/portfolio/ — WordPress, one
server-rendered gallery (current + exited). Each card carries the company
name, theme categories, a short description, the Volition investment team and
an "EXITED" flag for realized investments. Each company's own
/portfolio/<slug>/ page adds the "visit ... website" link.
Exited -> status "acquired" (raw flag kept in site_status), per repo convention.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, is_social, apply_tag_overrides

SOURCE_URL = "https://www.volitioncapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "volitioncapital_companies.json")
PRIMARY = "Volition Capital"
SECTOR_TAG_MAP = {
    "adtech": ["Gaming / Media / Entertainment"], "gtm technology": ["Future of Work"],
    "cybersecurity": ["Cybersecurity"], "digital health": ["Health"], "ecommerce": ["Consumer"],
    "gaming": ["Gaming / Media / Entertainment"], "hr tech": ["Future of Work"],
    "it infrastructure": ["Dev Tools / Cloud"], "movement of physical things": ["Logistics / Supply Chain"],
    "supply chain": ["Logistics / Supply Chain"], "proptech": ["PropTech"], "fintech": ["FinTech / Insurance"],
    "sustainability": ["Climate / Sustainability"], "physical ai": ["Deeptech / Robotics / AR/VR"],
    "data, analytics & automation": ["Data & Analytics"],
}


def website_of(html):
    ds = BeautifulSoup(html, "html.parser")
    for a in ds.select("a[href^=http]"):
        if "website" in a.get_text(" ").lower() and "volitioncapital" not in a["href"]:
            return a["href"].strip()
    for a in ds.select("main a[href^=http], article a[href^=http], .entry-content a[href^=http]"):
        h = a["href"]
        if "volitioncapital" not in h and "glassdoor" not in h and not is_social(h):
            return h.strip()
    return None


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "PetScreening": ["PropTech"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for it in soup.select(".pfgai-list-item"):
        t = it.select_one(".pfgai-list-item-title a")
        name = clean(t.get_text(" ")) if t else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = it.select_one(".pfgai-list-item-sub-title")
        desc = clean(d.get_text(" ")) if d else None
        cats = [clean(c.get_text()) for c in it.select(".pfgai-list-item-categories .pfgai-list-item-category") if clean(c.get_text())]
        det = it.select_one(".pfgai-list-item-detail")
        dstr = list(det.stripped_strings) if det else []
        team = [clean(a.get_text()) for a in (det.select("a[href*='/team/']") if det else []) if clean(a.get_text())]
        exited = any(s.strip().upper() == "EXITED" for s in dstr)
        rows.append({
            "company_name": name,
            "description": desc,
            "company_profile_url": t["href"].strip() if t and t.get("href") else None,
            "sectors": cats,
            "investment_team": team,
            "site_status": "Exited" if exited else "Current",
            "status": "acquired" if exited else "active",
        })
        if limit and len(rows) >= limit:
            break
    details = fetch_many([r["company_profile_url"] for r in rows if r["company_profile_url"]])
    out = []
    for r in rows:
        html = details.get(r["company_profile_url"])
        url = website_of(html) if html else None
        out.append({
            "company_name": r["company_name"],
            "description": r["description"],
            "company_url": url,
            "company_profile_url": r["company_profile_url"],
            "status": r["status"],
            "site_status": r["site_status"],
            "sectors": r["sectors"],
            "investment_team": r["investment_team"],
            "everywhere_tags": tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "sectors", "investment_team", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
