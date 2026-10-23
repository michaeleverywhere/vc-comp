#!/usr/bin/env python3
"""Swanlaab Venture Factory portfolio scraper -> swanlaab_companies.json
Source: https://swanlaab.com/portfolio — Swanlaab, Spanish-Israeli venture capital firm (deep tech, B2B software,
agri-food tech). Each portfolio entry's off-canvas profile (div.portfolio-item-off-canvas) gives the company name,
website, Swanlaab's description and labelled fields Date of Investment / Sector / Status / Fund / Country.
Companies held by the Scipio Swanlaab search-fund vehicles (acquisitions of established SMEs, not venture
investments) are skipped (VC-only rule). The page repeats entries per filter tab; duplicates collapse by name."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://swanlaab.com/portfolio"
PRIMARY = "Swanlaab"
FIELDS = ("Date of Investment", "Sector", "Status", "Fund", "Country")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for box in soup.select("div.portfolio-item-off-canvas"):
        h = box.select_one(".elementor-heading-title")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        parts = [clean(t) for t in box.stripped_strings]
        parts = [t for t in parts if t]
        f = {}
        for i, t in enumerate(parts):
            k = t.rstrip(":").strip()
            if t.endswith(":") and k in FIELDS and i + 1 < len(parts):
                f[k] = parts[i + 1]
        fund = f.get("Fund")
        if fund and "scipio" in fund.lower():
            continue
        site = next((a["href"] for a in box.select("a[href]") if a.get_text(strip=True) == "Website"), None)
        desc = None
        if "Company Profile" in parts:
            j = parts.index("Company Profile") + 1
            if j < len(parts) and not parts[j].endswith(":"):
                desc = parts[j]
        st = f.get("Status")
        status = ("exited" if st and st.lower().startswith("acquired") else
                  "closed" if st and st.lower() == "we tried" else "active" if st else None)
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[f["Sector"]] if f.get("Sector") else None,
                       investment_date=f.get("Date of Investment"), fund=fund, location=f.get("Country"),
                       status=status, status_detail=st))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Swanlaab companies")
    finish(out, "swanlaab", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
