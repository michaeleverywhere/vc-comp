#!/usr/bin/env python3
"""Titanium Ventures (formerly Telstra Ventures) portfolio scraper -> titaniumventures_companies.json
Source: https://ti.vc/portfolio/ — WP portfolio-item grid with logo alts + external links.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://ti.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "titaniumventures_companies.json")
PRIMARY = "Titanium Ventures"

# class tokens that are layout, not sectors
SKIP_CLASS = {
    "portfolio-item", "col-6", "col-md-4", "col-lg-3", "col-lg-2", "col",
    "row", "active", "show", "hide", "d-none",
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".portfolio-item"):
        img = it.select_one("img")
        name = clean(img.get("alt")) if img else None
        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if "ti.vc" not in href and "telstra" not in href:
                website = clean(href)
                break
        if not name:
            # fallback: search-terms last tokens / domain
            st = clean((it.select_one(".search-terms") or it).get_text())
            if website:
                from urllib.parse import urlparse
                host = urlparse(website).netloc.lower().removeprefix("www.")
                name = host.split(".")[0].replace("-", " ").title()
            elif st:
                name = st.split()[-1].title() if st.split() else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = []
        for cls in it.get("class") or []:
            if cls in SKIP_CLASS or cls.startswith("col"):
                continue
            # multi-word sectors encoded as hyphenated classes
            label = cls.replace("-", " ").strip()
            if label and label not in sectors and len(label) > 2:
                sectors.append(label.title() if label.islower() else label)
        # Prefer human search-terms sector phrases when present
        st_el = it.select_one(".search-terms")
        if st_el:
            # search-terms often duplicates class tokens as words
            pass
        rec = {
            "company_name": name,
            "description": None,
            "company_url": website,
            "logo_url": img.get("src") if img else None,
            "status": "Active",
            "stage": None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, None, sectors)[:4],
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
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
