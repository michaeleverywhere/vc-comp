#!/usr/bin/env python3
"""QED Investors portfolio scraper -> qed_companies.json
Source: https://qedinvestors.com/companies — Webflow CMS items linking to
/companies/<slug> with hidden fields for status, sector, location, country.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://qedinvestors.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "qed_companies.json")
PRIMARY = "QED Investors"
SECTOR_MAP = {
    "consumer finance": ["FinTech / Insurance"], "banking": ["FinTech / Insurance"],
    "payments": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"],
    "lending": ["FinTech / Insurance"], "vertical saas": [],
    "wealth": ["FinTech / Insurance"], "crypto": ["Web3 / Crypto"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".w-dyn-item"):
        a = it.select_one("a[href*='/companies/']")
        if not a:
            continue
        # name from img alt or slug
        img = a.select_one("img[alt]")
        name = clean(img["alt"]) if img and img.get("alt") else None
        if not name:
            slug = a["href"].rstrip("/").split("/")[-1]
            name = clean(slug.replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        hide = it.select_one(".hide")
        fields = []
        if hide:
            fields = [clean(t) for t in hide.stripped_strings if clean(t)]
        status = sector = location = country = None
        # typical order: status, sector, fund, location, country
        for f in fields:
            fl = f.lower()
            if fl in ("active", "exited", "ipo", "acquired") and not status:
                status = "active" if fl == "active" else ("public" if fl == "ipo" else "acquired")
            elif fl.startswith("fund"):
                continue
            elif not sector and fl not in ("united states", "united kingdom", "brazil", "mexico", "india", "canada") and "," not in f and len(f) < 40:
                # could be sector
                if fl not in ("active", "exited"):
                    sector = f
            elif "," in f and not location:
                location = f
            elif not country and f[0].isupper() and len(f) < 30:
                country = f
        # refine: known pattern from probe — Active, Vertical SaaS, Funds..., Washington DC, United States
        if fields:
            status = "active" if fields[0].lower() == "active" else ("acquired" if fields[0].lower() in ("exited", "acquired") else status)
            if len(fields) >= 2:
                sector = fields[1]
            # location often second-to-last before country
            if len(fields) >= 4:
                location = fields[-2]
                country = fields[-1]
        loc = ", ".join(x for x in (location, country) if x) or location or country
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "sectors": sectors,
            "location": loc,
            "status": status,
            "everywhere_tags": tags_for(name, None, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("sectors", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
