#!/usr/bin/env python3
"""Ridge Ventures portfolio scraper -> ridge_companies.json
Source: https://ridge.vc/ridge-portfolio/ — Uncode portfolio overlays.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://ridge.vc/ridge-portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ridge_companies.json")
PRIMARY = "Ridge Ventures"

SKIP = {"the ridge familia", "we are proud of the companies we have backed.", "select | all", "privacy preferences"}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    # Each company sits in a t-entry block with h3 title and optional IPO/status text + link
    for entry in soup.select("div.t-entry, div.t-inside, article"):
        h = entry.select_one("h3.t-entry-title, h3")
        if not h:
            continue
        name = clean(h.get_text())
        if not name or name.lower() in SKIP or name.lower() in seen:
            continue
        if len(name) > 60:
            continue
        seen.add(name.lower())
        raw = clean(entry.get_text(" ", strip=True)) or ""
        status = "active"
        if re.search(r"\bIPO\b", raw):
            status = "active"  # public/IPO — keep active, note in description if useful
        if re.search(r"(?i)\bacquired\b|\bexit", raw):
            status = "acquired"
        website = None
        for a in entry.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["ridge.vc", "linkedin", "twitter", "facebook", "medium.com/ridge"]):
                continue
            website = clean(href)
            break
        # Also walk up for link wrapping the card
        if not website:
            parent = entry
            for _ in range(5):
                parent = parent.parent
                if not parent:
                    break
                for a in parent.select("a[href^='http']"):
                    href = a["href"]
                    if any(x in href for x in ["ridge.vc", "linkedin", "twitter", "medium.com/ridge"]):
                        continue
                    website = clean(href)
                    break
                if website:
                    break
        desc = None
        if "IPO" in raw and name in raw:
            desc = "IPO"  # site literally shows IPO — not inventing valuation

        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "everywhere_tags": classify(name, desc)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    # Fallback: h3 titles with nearest external link if t-entry miss
    if len(out) < 10:
        for h in soup.select("h3"):
            name = clean(h.get_text())
            if not name or name.lower() in SKIP or name.lower() in seen:
                continue
            if len(name) > 60:
                continue
            seen.add(name.lower())
            website = None
            parent = h
            for _ in range(6):
                parent = parent.parent
                if not parent:
                    break
                for a in parent.select("a[href^='http']"):
                    href = a["href"]
                    if any(x in href for x in ["ridge.vc", "linkedin", "twitter", "medium.com/ridge"]):
                        continue
                    website = clean(href)
                    break
                if website:
                    break
            rec = {
                "company_name": name,
                "description": None,
                "company_url": website,
                "status": "active",
                "stage": None,
                "everywhere_tags": classify(name, None)[:4],
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            }
            out.append(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
