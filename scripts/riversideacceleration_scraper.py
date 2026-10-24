#!/usr/bin/env python3
"""Riverside Acceleration Capital portfolio scraper -> riversideacceleration_companies.json
Source: https://www.riverside.ac/companies — Riverside Acceleration Capital (RAC), revenue-based growth capital for
early-stage software companies. Each HubSpot company card (div.company-card) carries the company's logo alt text
(name), description, website link, executive name/position, and data-status / data-region / data-industry filters."""
import os, sys, json, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.riverside.ac/companies"
PRIMARY = "Riverside Acceleration Capital"


def _labels(raw):
    try:
        v = json.loads(raw or "[]")
    except ValueError:
        return []
    out = []
    for x in v:
        x = x.get("label") if isinstance(x, dict) else x
        if clean(x):
            out.append(clean(x))
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select("div.company-card"):
        img = c.select_one("img")
        name = clean(re.sub(r"\s*logo\s*$", "", (img.get("alt") or "") if img else "", flags=re.I))
        if not name:
            continue
        d = c.select_one(".company-description p")
        a = c.select_one(".company-description a[href]")
        ex = c.select_one(".executive-name")
        pos = c.select_one(".executive-position")
        status = _labels(c.get("data-status"))
        region = _labels(c.get("data-region"))
        industry = _labels(c.get("data-industry"))
        exe = clean(ex.get_text(" ", strip=True)) if ex else None
        if exe and pos and clean(pos.get_text(" ", strip=True)):
            exe = f"{exe} ({clean(pos.get_text(' ', strip=True))})"
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, a["href"] if a else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=industry,
                       status=status[0] if status else None, region=", ".join(region) or None,
                       founders=exe))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} RAC companies")
    finish(out, "riversideacceleration", ("description", "company_url", "status", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
