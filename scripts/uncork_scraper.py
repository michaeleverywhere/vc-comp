#!/usr/bin/env python3
"""
Uncork Capital (formerly SoftTech) portfolio scraper -> uncork_companies.json

Source: Framer site https://uncorkcapital.com/companies
- Full roster (~175) lives in `[data-framer-name="company cms item II"]` nodes
  (name only on the all-companies section).
- Featured companies (~21) have detail pages at /companies/<slug> with sector,
  founded year, website, partners-since, lead partner(s), stage, and a short blurb.

usage:
    python3 scripts/uncork_scraper.py [--limit N] [--skip-details]
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://uncorkcapital.com/companies"
SOURCE_URL = PORTFOLIO_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "uncork_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

SECTOR_TAG_MAP = {
    "Developer Tooling Infrastructure": ["Dev Tools / Cloud"],
    "Developer Tools & Infrastructure": ["Dev Tools / Cloud"],
    "Developer Tooling, Infrastructure & Security": ["Dev Tools / Cloud"],
    "B2B Applications": ["Future of Work"],
    "Consumer": ["Consumer"],
    "Fintech": ["FinTech / Insurance"],
    "Healthcare": ["Health"],
    "Crypto": ["Web3 / Crypto"],
    "Climate": ["Climate / Sustainability"],
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
        for mapped in SECTOR_TAG_MAP.get(sec, SECTOR_TAG_MAP.get(sec.replace(",", ""), [])):
            if mapped not in tags:
                tags.append(mapped)
        # partial match for long sector labels
        sl = sec.lower()
        if "developer" in sl or "infrastructure" in sl:
            if "Dev Tools / Cloud" not in tags:
                tags.append("Dev Tools / Cloud")
        if "fintech" in sl or "financ" in sl:
            if "FinTech / Insurance" not in tags:
                tags.append("FinTech / Insurance")
        if "health" in sl:
            if "Health" not in tags:
                tags.append("Health")
        if "consumer" in sl:
            if "Consumer" not in tags:
                tags.append("Consumer")
        if "crypto" in sl or "web3" in sl:
            if "Web3 / Crypto" not in tags:
                tags.append("Web3 / Crypto")
    for t in _classify(name, description, sectors):
        if t not in tags:
            tags.append(t)
    return tags[:4]


def slug_from_href(href):
    if not href:
        return None
    href = href.split("#")[0]
    m = re.search(r"/companies/([^/]+)/?$", href)
    return m.group(1) if m else None


def parse_listing(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select('[data-framer-name="company cms item II"]')
    companies = {}  # name -> {slug, profile_url}
    for it in items:
        txt = it.get_text("\n", strip=True)
        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        if not lines:
            continue
        name = clean(lines[0])
        if not name:
            continue
        a = it.find("a", href=True)
        href = a["href"] if a else None
        slug = slug_from_href(href) if href else None
        profile = None
        if slug:
            profile = f"https://uncorkcapital.com/companies/{slug}"
        # Prefer entry that has a detail slug
        if name not in companies or (slug and not companies[name].get("slug")):
            companies[name] = {"slug": slug, "company_profile_url": profile}
    return companies


def parse_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    info = {
        "description": None,
        "sectors": [],
        "year_founded": None,
        "company_url": None,
        "partners_since": None,
        "partners": [],
        "stage": None,
    }
    # Sector: ...
    m = re.search(r"Sector:\s*([^\n]+)", text)
    if m:
        info["sectors"] = [clean(m.group(1))]
    m = re.search(r"Founded In:\s*(\d{4})", text)
    if m:
        info["year_founded"] = m.group(1)
    m = re.search(r"Website:\s*([^\n]+)", text)
    if m:
        site = clean(m.group(1))
        if site and not site.startswith("http"):
            site = "https://" + site
        info["company_url"] = site
    m = re.search(r"Partners Since:\s*(\d{4})", text)
    if m:
        info["partners_since"] = m.group(1)
    m = re.search(r"Lead Partner\(s\):\s*([^\n]+)", text)
    if m:
        raw = clean(m.group(1))
        if raw:
            info["partners"] = [p.strip() for p in re.split(r",| & | and ", raw) if p.strip()]
    m = re.search(r"Stage:\s*([^\n]+)", text)
    if m:
        # Stop before STAGE filter UI repeating
        stage = clean(m.group(1))
        if stage:
            stage = re.split(r"\s+STAGE\s+", stage)[0].strip()
            info["stage"] = stage or None
    # Blurb: often a short sentence near the top after the name
    # Look for framer text blocks that look like descriptions
    for el in soup.select('[data-framer-name]'):
        nm = el.get("data-framer-name") or ""
        t = clean(el.get_text(" ", strip=True))
        if not t or len(t) < 40 or len(t) > 400:
            continue
        if any(x in t for x in ("Sector:", "Founded In:", "Website:", "Partners Since:", "Lead Partner", "Back to companies", "STAGE All")):
            continue
        if t.endswith(".") or "," in t:
            info["description"] = t
            break
    return info


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    skip_details = "--skip-details" in sys.argv
    html = fetch(PORTFOLIO_URL)
    companies = parse_listing(html)
    names = sorted(companies.keys())
    if limit:
        # Prefer ones with detail pages first
        names = sorted(names, key=lambda n: (0 if companies[n].get("slug") else 1, n))[:limit]

    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for i, name in enumerate(names):
        meta = companies[name]
        description = None
        sectors = []
        year_founded = None
        company_url = None
        partners_since = None
        partners = []
        stage = None
        if not skip_details and meta.get("company_profile_url"):
            try:
                dhtml = fetch(meta["company_profile_url"])
                info = parse_detail(dhtml)
                description = info["description"]
                sectors = info["sectors"]
                year_founded = info["year_founded"]
                company_url = info["company_url"]
                partners_since = info["partners_since"]
                partners = info["partners"]
                stage = info["stage"]
                time.sleep(0.3)
            except Exception as e:
                print(f"  ! detail failed {name}: {e}", file=sys.stderr)
            if (i + 1) % 10 == 0:
                print(f"  details {i + 1}/{len(names)}")
        out.append({
            "company_name": name,
            "description": description,
            "company_url": company_url,
            "company_profile_url": meta.get("company_profile_url"),
            "sectors": sectors,
            "stage": stage,
            "year_founded": year_founded,
            "partners_since": partners_since,
            "partners": partners,
            "everywhere_tags": everywhere_tags(name, description, sectors),
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "company_profile_url", "year_founded", "stage"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:25]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
