#!/usr/bin/env python3
"""Entrée Capital portfolio scraper -> entreecapital_companies.json
Source: company-sitemap.xml + per-company pages on entreecap.com.
"""
import json, os, re, sys, time
from collections import Counter
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SITEMAP = "https://entreecap.com/company-sitemap.xml"
SOURCE_URL = "https://entreecap.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "entreecapital_companies.json")
PRIMARY = "Entrée Capital"


def company_urls():
    r = requests.get(SITEMAP, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for loc in root.findall(".//sm:loc", ns):
        if loc.text and "/company/" in loc.text:
            urls.append(loc.text.strip())
    return urls


def parse_detail(url: str) -> dict | None:
    # Legacy company pages sometimes 302 to the startup domain (often dead).
    # Never follow off-site redirects — only parse HTML served by entreecap.com.
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=False)
    if r.status_code in (301, 302, 303, 307, 308):
        loc = r.headers.get("Location") or ""
        if loc.startswith("/") or "entreecap.com" in loc:
            if loc.startswith("/"):
                loc = "https://entreecap.com" + loc
            r = requests.get(loc, headers=HEADERS, timeout=TIMEOUT, allow_redirects=False)
        else:
            # Off-site redirect with no usable HTML — synthesize from slug + Location.
            if not r.text or len(r.text) < 500:
                slug = url.rstrip("/").split("/")[-1].replace("-", " ").strip()
                name = clean(slug.title()) if slug else None
                if not name:
                    return None
                website = clean(loc)
                return {
                    "company_name": name,
                    "description": None,
                    "company_url": website,
                    "status": "Active",
                    "stage": None,
                    "founders": None,
                    "sectors": None,
                    "lead_partner": None,
                    "source_url": url,
                }
    elif r.status_code >= 400:
        r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # title "monday.com - Entrée Capital"
    title = clean(soup.title.string) if soup.title else None
    name = None
    if title and " - " in title:
        name = clean(title.split(" - ")[0])
    if not name:
        h = soup.select_one("h1")
        name = clean(h.get_text()) if h else None
    if not name:
        return None
    text_body = soup.get_text("\n", strip=True)
    lines = [clean(l) for l in text_body.split("\n") if clean(l)]
    # Description: first substantial paragraph after the name
    desc = None
    for i, l in enumerate(lines):
        if l == name and i + 1 < len(lines):
            cand = lines[i + 1]
            if len(cand) > 40 and not cand.startswith("Founder") and cand not in ("Overview", "About"):
                desc = cand
                break
    if not desc:
        for l in lines:
            if name and name.lower() in l.lower() and len(l) > 60:
                desc = l
                break
    # Labeled fields
    founders = None
    sector = None
    stage = None
    website = None
    partner = None
    for i, l in enumerate(lines):
        if l == "Founder" and i + 1 < len(lines):
            founders = [clean(x) for x in re.split(r"\s*&\s*|\s*,\s*", lines[i + 1]) if clean(x)]
        elif l == "Leading Partner" and i + 1 < len(lines):
            partner = lines[i + 1]
        elif l == "Sector" and i + 1 < len(lines):
            sector = lines[i + 1]
        elif l == "Stage" and i + 1 < len(lines):
            stage = lines[i + 1]
        elif l == "Website" and i + 1 < len(lines):
            w = lines[i + 1]
            if w.startswith("http"):
                website = w
            elif "." in w and " " not in w:
                website = "https://" + w
    if not website:
        for a in soup.select("a[href^='http']"):
            href = a["href"]
            if "entreecap" in href or "linkedin.com" in href or "twitter.com" in href or "x.com" in href:
                continue
            website = clean(href)
            break
    sectors = [s.strip() for s in (sector or "").split(",") if s.strip()] if sector else []
    status = "Active"
    if stage and any(x in stage.lower() for x in ("ipo", "exit", "acquired", "public")):
        status = "Exited"
    return {
        "company_name": name,
        "description": desc,
        "company_url": website,
        "status": status,
        "stage": stage,
        "founders": founders,
        "sectors": sectors or None,
        "lead_partner": partner,
        "source_url": url,
    }



def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    urls = company_urls()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for i, url in enumerate(urls):
        if limit and len(out) >= limit:
            break
        try:
            row = parse_detail(url)
        except Exception as e:
            print(f"  skip {url}: {e}")
            continue
        if not row:
            continue
        name = row["company_name"]
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        rec = {
            **row,
            "everywhere_tags": classify(name, row.get("description"), row.get("sectors"))[:4],
            "primary_investor": PRIMARY,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if (i + 1) % 25 == 0:
            print(f"  ... {i+1}/{len(urls)}")
        time.sleep(0.25)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
