#!/usr/bin/env python3
"""
Emergence Capital portfolio scraper -> emergence_companies.json

Source: Webflow list at https://www.emcap.com/portfolio (logo grid of
~87 /portfolio/<slug> links). Each detail page carries name, description,
CEO, founded/partnered years, status, and external website / socials.

usage:
    python3 scripts/emergence_scraper.py [--limit N]
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

LIST_URL = "https://www.emcap.com/portfolio"
SOURCE_URL = LIST_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "emergence_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

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


def list_slugs(html):
    soup = BeautifulSoup(html, "html.parser")
    slugs = []
    seen = set()
    for a in soup.select('a[href*="/portfolio/"]'):
        href = a["href"]
        if href.startswith("http") and "emcap.com" not in href:
            continue
        path = href.split("?")[0].rstrip("/")
        slug = path.split("/")[-1]
        if not slug or slug == "portfolio" or slug in seen:
            continue
        seen.add(slug)
        profile = href if href.startswith("http") else "https://www.emcap.com" + href
        slugs.append((slug, profile))
    return slugs


def parse_detail(html, profile_url):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    # Name: often first substantial heading, or og:title, or from URL slug fallback
    name = None
    for sel in ["h1", "h2.heading", ".company-name", "[class*=company-name]"]:
        el = soup.select_one(sel)
        if el:
            t = clean(el.get_text())
            if t and t.lower() not in {"emergence", "portfolio", "building something iconic?"}:
                name = t
                break
    if not name:
        og = soup.select_one('meta[property="og:title"]')
        if og and og.get("content"):
            name = clean(og["content"].replace(" | Emergence", "").replace("- Emergence", ""))
    if not name:
        # From body text: after Menu, before CEO line
        m = re.search(r"Menu\s+([A-Z][^\n]{1,60})\s+(?:[A-Z][a-z]+ [A-Z]|Founded|Investor)", text)
        if m:
            name = clean(m.group(1))

    description = None
    # Long paragraph describing the company
    for p in soup.find_all("p"):
        t = clean(p.get_text(" ", strip=True))
        if t and len(t) >= 80 and "Emergence" not in t[:30] and "Privacy Policy" not in t:
            description = t
            break
    if not description:
        # From assembled-style body sample: after Status Private comes the blurb
        m = re.search(r"Status\s+\w+\s+(.+?)(?:On average|Building something|$)", text, re.S)
        if m:
            description = clean(m.group(1))

    year_founded = None
    m = re.search(r"Founded\s+(\d{4})", text)
    if m:
        year_founded = m.group(1)
    partnered = None
    m = re.search(r"Partnered\s+(\d{4})", text)
    if m:
        partnered = m.group(1)
    status = None
    m = re.search(r"Status\s+(Private|Public|Acquired|IPO)", text)
    if m:
        status = m.group(1)

    founders = []
    # "Ryan Wang, CEO" pattern
    m = re.search(r"([A-Z][a-zA-Z.\-]+(?:\s+[A-Z][a-zA-Z.\-]+)+),\s*CEO", text)
    if m:
        founders.append(clean(m.group(1)))

    partners = []
    m = re.search(r"Investor\s+([A-Z][a-zA-Z.\-]+(?:\s+[A-Z][a-zA-Z.\-]+)+)", text)
    if m:
        partners.append(clean(m.group(1)))

    company_url = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("http"):
            continue
        if any(x in href for x in ("emcap.com", "emergence", "webflow", "linkedin.com/company/emergence",
                                    "twitter.com/emergence", "x.com/emergence", "google.com/maps")):
            continue
        # Prefer non-social company site
        if any(x in href for x in ("linkedin.com", "twitter.com", "x.com")):
            continue
        company_url = clean(href)
        break

    logo = None
    img = soup.select_one("img.img-cover, img[src*='website-files']")
    if img and img.get("src"):
        logo = clean(img["src"])

    if not name:
        return None
    return {
        "company_name": name,
        "description": description,
        "company_url": company_url,
        "company_profile_url": profile_url,
        "logo_url": logo,
        "year_founded": year_founded,
        "first_investment_year": partnered,
        "status": status,
        "founders": founders,
        "partners": partners,
        "everywhere_tags": _classify(name, description)[:4],
        "source_url": SOURCE_URL,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(LIST_URL)
    slugs = list_slugs(html)
    if limit:
        slugs = slugs[:limit]
    print(f"found {len(slugs)} portfolio slugs")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for i, (slug, profile) in enumerate(slugs):
        try:
            dhtml = fetch(profile)
            rec = parse_detail(dhtml, profile)
        except Exception as e:
            print(f"  ! failed {slug}: {e}", file=sys.stderr)
            continue
        if not rec or rec["company_name"] in seen:
            continue
        seen.add(rec["company_name"])
        rec["scraped_at"] = scraped_at
        out.append(rec)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(slugs)}")
        time.sleep(0.3)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "year_founded", "status"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
