#!/usr/bin/env python3
"""SignalFire portfolio scraper -> signalfire_companies.json
Source: https://www.signalfire.com/portfolio — Webflow portfolio-item cards.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.signalfire.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "signalfire_companies.json")
PRIMARY = "SignalFire"

SKIP = {"featured case studies", "all companies", "privacy settings"}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for h2 in soup.select("h2.heading-style-h3"):
        name = clean(h2.get_text())
        if not name or name.lower() in SKIP or name.lower() in seen:
            continue
        seen.add(name.lower())
        box = h2.find_parent(class_="portfolio-item_description-box") or h2.find_parent(class_="portfolio-item_desc-col")
        scope = box.parent if box and box.parent else (box or h2.parent)
        website = None
        for a in scope.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ("signalfire.com", "webflow.io", "cookie")):
                continue
            website = clean(href)
            break
        texts = [clean(t) for t in scope.stripped_strings if clean(t)]
        founders = None
        sectors = []
        for i, t in enumerate(texts):
            if t == "Founder(s)" and i + 1 < len(texts):
                founders = texts[i + 1]
            if t == "Sector":
                for j in range(i + 1, min(i + 8, len(texts))):
                    if texts[j] in ("Founder(s)", "Sector", "Stage", "Status", name) or (texts[j] or "").startswith("http"):
                        break
                    if texts[j] and texts[j] not in sectors:
                        sectors.append(texts[j])
        desc = None  # list cards are name+sector+founders; sector drives tags
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "founders": founders,
            "sectors": sectors,
            "everywhere_tags": classify(name, " ".join(sectors) if sectors else None, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r.get('sectors'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print("  caveat: name+sector+url cards; descriptions sparse on list page")


if __name__ == "__main__":
    main()
