#!/usr/bin/env python3
"""Target Global portfolio scraper -> targetglobal_companies.json
Source: https://www.targetglobal.vc/portfolio — /portfolio/<slug> links + detail pages.
"""
import json, os, sys, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

PORTFOLIO_URL = "https://www.targetglobal.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "targetglobal_companies.json")
PRIMARY = "Target Global"


def list_slugs(html):
    soup = BeautifulSoup(html, "html.parser")
    slugs, seen = [], set()
    for a in soup.select('a[href*="/portfolio/"]'):
        href = a["href"].split("?")[0].rstrip("/")
        slug = href.split("/")[-1]
        if not slug or slug == "portfolio" or slug in seen:
            continue
        seen.add(slug)
        profile = href if href.startswith("http") else urljoin(PORTFOLIO_URL, href)
        slugs.append((slug, profile))
    return slugs


def parse_detail(html, profile):
    soup = BeautifulSoup(html, "html.parser")
    name = None
    for h in soup.select("h1"):
        t = clean(h.get_text())
        if t and t.lower() not in ("portfolio", "target global"):
            name = t
            break
    if not name:
        og = soup.select_one('meta[property="og:title"]')
        if og and og.get("content"):
            name = clean(og["content"].split("|")[0])
    desc = None
    md = soup.select_one('meta[name="description"], meta[property="og:description"]')
    if md and md.get("content"):
        desc = clean(md["content"])
    if not desc:
        for p in soup.find_all("p"):
            t = clean(p.get_text())
            if t and len(t) >= 60 and "target global" not in t.lower()[:30]:
                desc = t
                break
    company_url = None
    for a in soup.select("a[href^='http']"):
        href = a["href"]
        if any(x in href for x in ("targetglobal", "linkedin", "twitter", "x.com", "facebook", "instagram", "youtube")):
            continue
        company_url = clean(href)
        break
    return {
        "company_name": name,
        "description": desc,
        "company_url": company_url,
        "status": "Active",
        "stage": None,
        "everywhere_tags": classify(name, desc)[:4] if name else [],
        "primary_investor": PRIMARY,
        "source_url": profile,
    }


def fetch_one(profile):
    for attempt in range(1, 4):
        try:
            r = requests.get(profile, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            time.sleep(1.2 * attempt)
    return None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    slugs = list_slugs(html)
    if limit:
        slugs = slugs[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_one, profile): (slug, profile) for slug, profile in slugs}
        for fut in as_completed(futs):
            slug, profile = futs[fut]
            dhtml = fut.result()
            if not dhtml:
                name = slug.replace("-", " ").title()
                rec = {
                    "company_name": name,
                    "description": None,
                    "company_url": None,
                    "status": "Active",
                    "stage": None,
                    "everywhere_tags": classify(name, None)[:4],
                    "primary_investor": PRIMARY,
                    "source_url": profile,
                    "scraped_at": scraped_at,
                }
            else:
                rec = parse_detail(dhtml, profile)
                if not rec.get("company_name"):
                    rec["company_name"] = slug.replace("-", " ").title()
                    rec["everywhere_tags"] = classify(rec["company_name"], rec.get("description"))[:4]
                rec["scraped_at"] = scraped_at
            key = rec["company_name"].lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(rec)
    out.sort(key=lambda r: r["company_name"].lower())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged")


if __name__ == "__main__":
    main()
