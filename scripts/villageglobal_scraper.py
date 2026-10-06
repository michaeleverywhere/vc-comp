#!/usr/bin/env python3
"""Village Global portfolio scraper -> villageglobal_companies.json
Source: https://www.villageglobal.com/portfolio — Webflow, one page. Each card
gives the company name + one-line description (linked to the company's own
site), Village Global's category labels and the founders. The site publishes a
curated selection, not the full fund history.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://www.villageglobal.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "villageglobal_companies.json")
PRIMARY = "Village Global"
SECTOR_TAG_MAP = {
    "health": ["Health"], "fintech": ["FinTech / Insurance"], "consumer": ["Consumer"],
    "logistics": ["Logistics / Supply Chain"], "aerospace/defense": ["Deeptech / Robotics / AR/VR"],
    "climate": ["Climate / Sustainability"], "crypto": ["Web3 / Crypto"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for card in soup.select(".portfolio-card"):
        link = card.select_one("a.portfolio-card-link")
        nm = link.select_one(".heading-small") if link else None
        name = clean(nm.get_text()) if nm else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = link.select_one(".text-large")
        desc = clean(d.get_text(" ")) if d else None
        cats = []
        for c in card.select(".portfolio-info .label"):
            t = clean(c.get_text())
            if t and t not in cats:
                cats.append(t)
        founders = [clean(f.get_text()) for f in card.select(".portfolio-meta .font-weight-semibold") if clean(f.get_text())]
        href = (link.get("href") or "").strip()
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": href if href.startswith("http") else None,
            "status": None,
            "sectors": cats,
            "founders": founders,
            "everywhere_tags": tags_for(name, desc, cats, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "sectors", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
