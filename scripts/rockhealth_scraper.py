#!/usr/bin/env python3
"""Rock Health Capital portfolio scraper -> rockhealth_companies.json
Source: https://rockhealthcapital.com/portfolio/ — Rock Health Capital, the seed and early-stage digital-health
venture fund; the Divi filter grid lists every portfolio company with its WordPress company categories (sector,
US region, "exited"); each company's rockhealth.com/companies/<slug>/ page supplies the firm's one-line description."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from _scraper_common import clean
from _d50_common import rec, finish

SOURCE_URL = "https://rockhealthcapital.com/portfolio/"
# The site's WAF answers 403 to the shared macOS Chrome UA string but serves this ordinary desktop UA normally.
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}


def get(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=30)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            time.sleep(0.2)
            return r.text
        except requests.RequestException:
            time.sleep(1.5 * (attempt + 1))
    return None
PRIMARY = "Rock Health Capital"
REGIONS = {"west-coast": "US West Coast", "east-coast": "US East Coast", "central": "US Central"}
SKIP = {"exited", "location", "product"}
SECTOR_MAP = {"telemedicine": ["Healthcare / Biotech"], "digital-medicine": ["Healthcare / Biotech"],
              "health-information": ["Healthcare / Biotech"], "wellness": ["Healthcare / Biotech", "Consumer"],
              "wearableshardware": ["Healthcare / Biotech", "Deeptech / Robotics / AR/VR"],
              "analytics": ["Healthcare / Biotech", "AI / ML / Data"], "infrastructure": ["Healthcare / Biotech"],
              "productivity-tools": ["Healthcare / Biotech", "Enterprise SaaS"], "services": ["Healthcare / Biotech"],
              "marketplace": ["Healthcare / Biotech", "Marketplace"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = get(SOURCE_URL)
    if not html:
        raise SystemExit("FATAL: portfolio page unreachable")
    soup = BeautifulSoup(html, "html.parser")
    cards = []
    for art in soup.select("article.dp-dfg-item"):
        name = clean(art.select_one(".entry-title") and art.select_one(".entry-title").get_text(" ", strip=True))
        if not name:
            continue
        cats = [c[len("company-category-"):] for c in art.get("class", []) if c.startswith("company-category-")]
        ajax = art.get("data-ajax-url") or ""
        detail = ajax.split("?")[0] or None
        cards.append((name, cats, detail))
    urls = [d for _, _, d in cards if d]
    with ThreadPoolExecutor(max_workers=4) as ex:
        pages = dict(zip(urls, ex.map(get, urls)))
    out = []
    for name, cats, detail in cards:
        desc = None
        if pages.get(detail):
            m = BeautifulSoup(pages[detail], "html.parser").find("meta", attrs={"name": "description"})
            desc = clean(m.get("content")) if m else None
        sectors = [c for c in cats if c not in SKIP and c not in REGIONS]
        region = next((REGIONS[c] for c in cats if c in REGIONS), None)
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       location=region, status="exited" if "exited" in cats else None,
                       profile_url=detail))
    if len(out) < 55:
        raise SystemExit(f"FATAL: only {len(out)} Rock Health companies")
    finish(out, "rockhealth", ("description", "sectors", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
