#!/usr/bin/env python3
"""Accel-KKR portfolio scraper -> accelkkr_companies.json
Source: https://www.accel-kkr.com/portfolio — server-rendered WordPress grid of
<article class="company">: name, one-line excerpt, location, investment status
(current/past) and strategy (equity/credit) data attributes, detail link.
(The site rejects the shared fetch() client, so a browser UA is sent directly.)
"""
import os, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.accel-kkr.com/portfolio"
PRIMARY = "Accel-KKR"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def attr(art, k):
    v = (art.get(k) or "").strip(".").replace("-", " ").strip()
    return v or None


REGION = {"emea": "EMEA", "north america": "North America", "asia pacific": "Asia Pacific", "latin america": "Latin America"}


def fmt_region(v):
    parts = [p.replace("-", " ").strip() for p in (v or "").split(".") if p.strip()]
    return ", ".join(REGION.get(p, p.title()) for p in parts) or None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for art in soup.select("article.company"):
        h = art.find("h3")
        a = art.find("a", href=True)
        ex = art.select_one(".excerpt")
        name = clean(h.get_text(" ", strip=True)) if h else (a.get("title") if a else None)
        status = attr(art, "data-status")
        out.append(rec(name, clean(ex.get_text(" ", strip=True)) if ex else None, None, PRIMARY, SOURCE_URL, scraped_at,
                       region=fmt_region(art.get("data-location")),
                       portfolio_status=status,
                       status={"current investment": "active", "past investment": "realized"}.get(status, status),
                       strategy=(attr(art, "data-strategy") or "").title() or None,
                       detail_url=a["href"] if a else None))
    finish(out, "accelkkr", ("description", "status", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
