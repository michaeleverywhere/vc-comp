#!/usr/bin/env python3
"""Colle Capital portfolio scraper -> collecapital_companies.json
Source: https://collecapital.com/portfolio/ — logo gallery with company alts + links.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://collecapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "collecapital_companies.json")
PRIMARY = "Colle Capital"

SKIP_ALTS = {
    "colle-capital-logo-w (1)", "colle capital", "logo", "image",
}


def clean_name(alt: str) -> str | None:
    alt = clean(alt)
    if not alt:
        return None
    low = alt.lower()
    if low in SKIP_ALTS or "colle" in low and "capital" in low:
        return None
    # strip common logo suffixes
    alt = re.sub(r"(?i)[\s_-]*logo.*$", "", alt).strip()
    alt = re.sub(r"(?i)^2024\s+", "", alt).strip()
    alt = alt.replace("-", " ").replace("_", " ")
    alt = re.sub(r"\s+", " ", alt).strip()
    # title-case if all lower/upper
    if alt.islower() or alt.isupper():
        alt = alt.title()
    if len(alt) < 2 or len(alt) > 60:
        return None
    return alt


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for img in soup.select("img[alt]"):
        name = clean_name(img.get("alt") or "")
        if not name or name.lower() in seen:
            continue
        website = None
        parent = img
        for _ in range(8):
            parent = parent.parent
            if not parent:
                break
            for a in parent.select("a[href^='http']"):
                href = a["href"]
                if any(x in href for x in ["collecapital", "colle.vc", "linkedin", "twitter", "facebook", "instagram", "ataki"]):
                    continue
                website = clean(href)
                break
            if website:
                break
        if not website:
            continue  # require a company link to avoid nav logos
        seen.add(name.lower())
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
