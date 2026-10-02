#!/usr/bin/env python3
"""Unusual Ventures portfolio scraper -> unusual_companies.json
Source: https://www.unusual.vc/portfolio/ — "Name is …" title cards with sector chips.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.unusual.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "unusual_companies.json")
PRIMARY = "Unusual Ventures"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for h in soup.select(".title_area h4, h4"):
        text = clean(h.get_text())
        if not text:
            continue
        m = re.match(r"^(.+?)\s+is\s+(.+)$", text, re.I)
        if not m:
            continue
        name = clean(m.group(1))
        desc = clean(text)
        if not name or name.lower() in seen:
            continue
        if len(name) > 60:
            continue
        seen.add(name.lower())
        # sector chip nearby
        sector = None
        parent = h.find_parent(class_=re.compile("portfolio|company|card|item|col")) or h.parent
        if parent:
            for span in parent.select("span"):
                t = clean(span.get_text())
                if t and 2 < len(t) < 40 and t.lower() not in ("portfolio", "companies") and "is " not in t.lower():
                    # likely sector chip
                    if t[0].isupper() and t not in (name,):
                        sector = t
                        break
            # also look at previous sibling area
            prev = parent.find_previous(class_=re.compile("sector|tag|categor|label"))
        sectors = [sector] if sector else []
        website = None
        if parent:
            for a in parent.select("a[href^='http']"):
                href = a["href"]
                if "unusual.vc" in href or "wp-" in href:
                    continue
                website = clean(href)
                break
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "sectors": sectors,
            "everywhere_tags": classify(name, desc, sectors)[:4],
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
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
