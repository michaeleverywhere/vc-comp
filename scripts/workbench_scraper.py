#!/usr/bin/env python3
"""Work-Bench portfolio scraper -> workbench_companies.json
Source: https://www.work-bench.com/portfolio — Webflow + Finsweet list, one
page. Each card links to the company's own site and carries name, a one-line
description, Work-Bench's category and a status (Active / Exit). "Exit" is
kept as site_status only (an exit is not necessarily an acquisition).
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://www.work-bench.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "workbench_companies.json")
PRIMARY = "Work-Bench"
SECTOR_TAG_MAP = {
    "cybersecurity": ["Cybersecurity"],
    "ai infrastructure & developer tools": ["Dev Tools / Cloud"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for card in soup.select("a.portfolio_card"):
        nm = card.select_one("[fs-list-field=name]")
        name = clean(nm.get_text()) if nm else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = card.select_one(".portfolio_card-description")
        desc = clean(d.get_text(" ")) if d else None
        cat = card.select_one("[fs-list-field=category]")
        cat = clean(cat.get_text()) if cat else None
        st = card.select_one("[fs-list-field=status]")
        st = clean(st.get_text()) if st else None
        href = (card.get("href") or "").strip()
        sectors = [cat] if cat else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": href if href.startswith("http") else None,
            "status": "active" if (st or "").lower() == "active" else None,
            "site_status": st,
            "sectors": sectors,
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
    for k in ("description", "company_url", "status", "site_status", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
