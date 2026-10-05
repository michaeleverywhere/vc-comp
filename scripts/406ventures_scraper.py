#!/usr/bin/env python3
""".406 Ventures portfolio scraper -> 406ventures_companies.json
Source: https://www.406ventures.com/companies/ — WordPress, every company card
server-rendered: name, status (data-company-status active|exited), sectors
(Healthcare / Data + AI / Cybersecurity), description, website and an optional
case-study / "In the Zone" link. No stage, location or invest year published.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://www.406ventures.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "406ventures_companies.json")
PRIMARY = ".406 Ventures"
SECTOR_TAG_MAP = {
    "healthcare": ["Health"],
    "cybersecurity": ["Cybersecurity"],
    "data + ai": ["Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in soup.select("div.company-card"):
        h = c.select_one(".company-name")
        name = clean(h.get_text()) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        site_status = clean(c.get("data-company-status"))
        sectors = [clean(li.get_text()) for li in c.select(".sectors-list li") if clean(li.get_text())]
        d = c.select_one(".company-description")
        desc = clean(d.get_text(" ")) if d else None
        w = c.select_one("a.company-website[href]")
        more = [a["href"] for a in c.select("a[href]") if a is not w and "406ventures.com" in a["href"]]
        status = {"active": "active", "exited": "acquired"}.get((site_status or "").lower())
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean(w["href"]) if w else None,
            "status": status,
            "site_status": site_status,
            "stage": None,
            "location": None,
            "sectors": sectors,
            "case_study_url": more[0] if more else None,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for r in out if r.get(k))}/{n}")


if __name__ == "__main__":
    main()
