#!/usr/bin/env python3
"""
Initialized Capital portfolio scraper -> initialized_companies.json

Source: Next.js __NEXT_DATA__ on https://initialized.com/companies
(pageProps.startups.data — Strapi-shaped CMS payload, ~184 startups).

Schema: company_name, description, company_url, logo_url, sectors (Initialized
tags), is_unicorn, everywhere_tags, source_url, scraped_at.

usage:
    python3 scripts/initialized_scraper.py [--limit N]
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://initialized.com/companies"
SOURCE_URL = PORTFOLIO_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "initialized_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

# Initialized tags -> everywhere_tags. Enterprise / Frontier Tech / Exit left to
# keyword classifier (too broad / not a market / status flag).
SECTOR_TAG_MAP = {
    "Climate": ["Climate / Sustainability"],
    "Consumer": ["Consumer"],
    "Crypto": ["Web3 / Crypto"],
    "Fintech": ["FinTech / Insurance"],
    "Hardware": ["Deeptech / Robotics / AR/VR"],
    "Healthcare": ["Health"],
    "Marketplaces": ["Consumer"],
    "Real Estate": ["PropTech"],
}

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify as _classify  # noqa: E402


def fetch(url):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def everywhere_tags(name, description, sectors):
    tags = []
    for sec in sectors or []:
        for mapped in SECTOR_TAG_MAP.get(sec, []):
            if mapped not in tags:
                tags.append(mapped)
    for t in _classify(name, description, sectors):
        if t not in tags:
            tags.append(t)
    return tags[:4]


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: no __NEXT_DATA__ on companies page")
    pp = json.loads(m.group(1))["props"]["pageProps"]
    startups = ((pp.get("startups") or {}).get("data")) or []
    if limit:
        startups = startups[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for item in startups:
        attrs = item.get("attributes") or {}
        name = clean(attrs.get("name"))
        if not name or name in seen:
            continue
        seen.add(name)
        description = clean(attrs.get("description"))
        sectors = []
        for t in (attrs.get("tags") or {}).get("data") or []:
            tn = clean((t.get("attributes") or {}).get("name"))
            if tn and tn != "Exit" and tn not in sectors:
                sectors.append(tn)
        logo = None
        logo_data = ((attrs.get("logo") or {}).get("data") or {})
        if isinstance(logo_data, dict):
            logo = clean((logo_data.get("attributes") or {}).get("url"))
        out.append({
            "company_name": name,
            "description": description,
            "company_url": clean(attrs.get("websiteUrl")),
            "logo_url": logo,
            "sectors": sectors,
            "is_unicorn": bool(attrs.get("isUnicorn")),
            "everywhere_tags": everywhere_tags(name, description, sectors),
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "logo_url"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n}")
    print(f"  is_unicorn: {sum(1 for r in out if r['is_unicorn'])}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
