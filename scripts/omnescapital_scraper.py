#!/usr/bin/env python3
"""Omnes Capital portfolio scraper -> omnescapital_companies.json
Source: https://www.omnescapital.com/investments — Omnes Capital, Paris-based investor whose Venture Capital & Growth
team backs European tech / deep-tech start-ups. Every holding has a summary tile tagged with its expertise
(isSelected([...]) list) and a full profile (div.b-investments__item--full, keyed by the same id) with name, founders,
description and labelled fields Country / City / Sector / Investment Date / Website. Only holdings tagged
"venture-capital-growth" are kept; energy-transition / digital infrastructure and co-investment holdings are
infrastructure/PE-style and skipped (VC-only rule)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.omnescapital.com/investments"
PRIMARY = "Omnes Capital"
FIELDS = ("Country", "City", "Sector", "Investment Date", "Website")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    vc_ids = set()
    for d in soup.select("div.b-investments__item--summary[id]"):
        if "'venture-capital-growth'" in (d.get("v-if") or ""):
            vc_ids.add(d["id"].replace("investment", ""))
    out = []
    for d in soup.select("div.b-investments__item--full"):
        m = re.search(r"current==(\d+)", d.get("v-if") or "")
        if not m or m.group(1) not in vc_ids:
            continue
        h = d.select_one(".b-investment__title")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        fo = d.select_one(".b-investment__founders")
        founders = None
        if fo:
            b = fo.find("b")
            if b:
                b.extract()
            founders = clean(fo.get_text(" ", strip=True))
        c = d.select_one(".b-investment__content p")
        parts = [t for t in (clean(x) for x in d.stripped_strings) if t]
        f = {}
        for i, t in enumerate(parts):
            if t in FIELDS and i + 1 < len(parts) and parts[i + 1] not in FIELDS:
                f.setdefault(t, parts[i + 1])
        loc = ", ".join(x for x in (f.get("City"), f.get("Country")) if x) or None
        site = f.get("Website") if (f.get("Website") or "").startswith("http") else None
        out.append(rec(name, clean(c.get_text(" ", strip=True)) if c else None, site, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[f["Sector"]] if f.get("Sector") else None, location=loc,
                       founders=founders, investment_date=f.get("Investment Date")))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Omnes Capital VC companies")
    finish(out, "omnescapital", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
