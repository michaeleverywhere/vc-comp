#!/usr/bin/env python3
"""83North portfolio scraper -> 83north_companies.json
Source: https://www.83north.com/companies/ — WordPress company cards.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.83north.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "83north_companies.json")
PRIMARY = "83North"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for it in soup.select("div.companies div.item"):
        h2 = it.select_one("h2")
        name = clean(h2.get_text()) if h2 else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        label = clean(it.select_one(".label").get_text()) if it.select_one(".label") else None
        status = "active"
        if label and "exit" in label.lower():
            status = "acquired"

        hover = it.select_one(".hover")
        texts = [clean(t) for t in (hover.stripped_strings if hover else []) if clean(t)]
        # Typical: Name, tagline, www..., Acquired by..., Leadership:...
        desc = None
        website = None
        for t in texts:
            if t == name:
                continue
            if t.lower().startswith("leadership:"):
                continue
            if t.lower().startswith("www.") or t.lower().startswith("http"):
                website = t if t.startswith("http") else "https://" + t
                continue
            if t.lower().startswith("acquired"):
                if not desc:
                    desc = t
                status = "acquired"
                continue
            if not desc and len(t) > 3:
                desc = t

        # Prefer real <a href>
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["83north", "linkedin", "twitter", "facebook"]):
                continue
            website = clean(href)
            break

        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "location": None,
            "everywhere_tags": classify(name, desc)[:4],
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
