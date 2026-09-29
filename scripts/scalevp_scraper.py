#!/usr/bin/env python3
"""
Scale Venture Partners portfolio scraper -> scalevp_companies.json

Source: Webflow + Finsweet CMS list at https://www.scalevp.com/portfolio
paginated server-side via ?0b3cbfb7_page=N (~25/page). Listing carries name,
sectors, status, Scale partners, and investment date. Per-company detail pages
(/portfolio/<slug>) add description + external company_url.

usage:
    python3 scripts/scalevp_scraper.py [--limit N] [--skip-details]
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

LIST_URL = "https://www.scalevp.com/portfolio"
PAGE_PARAM = "0b3cbfb7_page"
SOURCE_URL = LIST_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "scalevp_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

SECTOR_TAG_MAP = {
    "Applications": [],
    "Infrastructure": ["Dev Tools / Cloud"],
    "Fintech": ["FinTech / Insurance"],
    "Healthcare": ["Health"],
    "Security": ["Cybersecurity"],
    "AI": [],
    "Featured": [],  # curation flag, not a sector
}

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify as _classify  # noqa: E402


def fetch(url, params=None):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
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
    for t in _classify(name, description, [s for s in (sectors or []) if s != "Featured"]):
        if t not in tags:
            tags.append(t)
    return tags[:4]


def parse_list_page(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".portfolio_list > .w-dyn-item")
    rows = []
    for it in items:
        name_el = it.select_one('[fs-list-field="name"]')
        name = clean(name_el.get_text()) if name_el else None
        if not name:
            continue
        sectors = []
        for s in it.select('[fs-list-field="Sector"]'):
            t = clean(s.get_text())
            if t and t not in sectors:
                sectors.append(t)
        status_el = it.select_one('[fs-list-field="Status"]')
        status = clean(status_el.get_text()) if status_el else None
        partners = []
        team = it.select_one('[fs-list-field="team"]')
        if team:
            for p in team.find_all("p"):
                pn = clean(p.get_text())
                if pn and pn not in partners:
                    partners.append(pn)
        # also Team Member chips
        for tm in it.select('[fs-list-field="Team Member"]'):
            pn = clean(tm.get_text())
            if pn and pn not in partners:
                partners.append(pn)
        date_el = it.select_one('[fs-list-field="date"]')
        inv_date = clean(date_el.get_text()) if date_el else None
        link = it.select_one('a[href*="/portfolio/"]')
        # The row itself may be wrapped in a link, or arrow link
        profile = None
        for a in it.find_all("a", href=True):
            if "/portfolio/" in a["href"] and a["href"].count("/") >= 2:
                profile = a["href"]
                break
        if profile and profile.startswith("/"):
            profile = "https://www.scalevp.com" + profile
        rows.append({
            "company_name": name,
            "sectors": sectors,
            "status": status,
            "partners": partners,
            "first_investment_date": inv_date,
            "company_profile_url": profile,
        })
    has_next = soup.select_one("a.w-pagination-next") is not None
    return rows, has_next


def parse_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    description = None
    # Common Webflow rich-text / body patterns on ScaleVP detail
    for sel in [".portfolio-detail_description", ".rich-text-block", ".portfolio_content p",
                "[class*=description]", "p"]:
        for el in soup.select(sel):
            t = clean(el.get_text(" ", strip=True))
            if t and len(t) >= 40 and "ScaleVP" not in t[:20]:
                description = t
                break
        if description:
            break
    company_url = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("http"):
            continue
        if any(x in href for x in ("scalevp.com", "scaleventure", "website-files", "linkedin.com/company/scale",
                                    "twitter.com", "x.com", "box.com")):
            continue
        company_url = clean(href)
        break
    return description, company_url


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    skip_details = "--skip-details" in sys.argv
    scraped_at = datetime.now(timezone.utc).isoformat()

    all_rows, page = [], 1
    while True:
        html = fetch(LIST_URL, params={PAGE_PARAM: page} if page > 1 else None)
        rows, has_next = parse_list_page(html)
        if not rows:
            break
        all_rows.extend(rows)
        print(f"  list page {page}: {len(rows)} companies (total {len(all_rows)})")
        if not has_next:
            break
        page += 1
        if page > 20:
            break
        time.sleep(0.4)
        if limit and len(all_rows) >= limit:
            break

    # Dedupe by name (featured may repeat)
    seen, unique = set(), []
    for r in all_rows:
        if r["company_name"] in seen:
            continue
        seen.add(r["company_name"])
        unique.append(r)
    if limit:
        unique = unique[:limit]

    out = []
    for i, r in enumerate(unique):
        description = None
        company_url = None
        if not skip_details and r.get("company_profile_url"):
            try:
                dhtml = fetch(r["company_profile_url"])
                description, company_url = parse_detail(dhtml)
                time.sleep(0.25)
            except SystemExit:
                raise
            except Exception as e:
                print(f"  ! detail failed for {r['company_name']}: {e}", file=sys.stderr)
            if (i + 1) % 25 == 0:
                print(f"  details {i + 1}/{len(unique)}")
        sectors = [s for s in r["sectors"] if s != "Featured"]
        out.append({
            "company_name": r["company_name"],
            "description": description,
            "company_url": company_url,
            "company_profile_url": r.get("company_profile_url"),
            "sectors": sectors,
            "status": r.get("status"),
            "partners": r.get("partners") or [],
            "first_investment_date": r.get("first_investment_date"),
            "everywhere_tags": everywhere_tags(r["company_name"], description, sectors),
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "company_profile_url", "status", "first_investment_date"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n}")
    print(f"  partners: {sum(1 for r in out if r['partners'])}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
