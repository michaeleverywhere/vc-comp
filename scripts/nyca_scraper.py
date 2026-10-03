#!/usr/bin/env python3
"""Nyca Partners portfolio scraper -> nyca_companies.json
Source: https://www.nyca.com/companies — logo alts "{Name} portfolio logo".
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.nyca.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "nyca_companies.json")
PRIMARY = "Nyca Partners"

ALT_RE = re.compile(r"^(.+?)\s+portfolio\s+logo$", re.I)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for img in soup.select("img[alt]"):
        alt = clean(img.get("alt"))
        if not alt:
            continue
        m = ALT_RE.match(alt)
        if not m:
            continue
        name = clean(m.group(1))
        if not name or name.lower() in seen:
            continue
        if name.lower() in ("nyca partners", "nyca"):
            continue
        seen.add(name.lower())
        # Try parent link for company URL
        website = None
        a = img.find_parent("a")
        if a and a.get("href") and a["href"].startswith("http"):
            href = a["href"]
            if "nyca.com" not in href:
                website = clean(href)
        rec = {
            "company_name": name,
            "description": None,  # not published on listing
            "company_url": website,
            "status": "Active",
            "stage": None,
            "everywhere_tags": classify(name, None)[:4],
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
