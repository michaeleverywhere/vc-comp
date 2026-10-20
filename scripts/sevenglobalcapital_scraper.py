#!/usr/bin/env python3
"""7GC (7 Global Capital, 7gc&co) portfolio scraper -> sevenglobalcapital_companies.json
Source: https://www.7gc.co/portfolio — every company page in 7GC's Squarespace portfolio: company
name, the month/year shown on the page (first invested), 7GC's one-line description and website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.7gc.co/portfolio"
BASE = "https://www.7gc.co"
PRIMARY = "7GC"
MONTH = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})$", re.I)


def parse(url, h):
    s = BeautifulSoup(h, "html.parser")
    t = s.title.get_text(strip=True) if s.title else ""
    name = clean(t.split("—")[0]) if "—" in t else None
    main = s.select_one("main") or s
    texts = []
    for blk in main.select(".sqs-html-content"):
        x = clean(blk.get_text(" ", strip=True))
        if x and x not in ("Previous", "Next"):
            texts.append(x)
    date, desc = None, None
    for x in texts:
        if MONTH.match(x):
            date = x[:1].upper() + x[1:].lower()
        elif name and x != name and not desc and x.lower() not in ("previous", "next"):
            desc = f"{name} {x}" if x.lower().startswith("is ") else x
    web = None
    for a in main.select("a[href^=http]"):
        if "7gc.co" not in a["href"] and not is_social(a["href"]):
            web = a["href"]
            break
    return name, desc, web, date


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    lst = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    urls = list(dict.fromkeys(BASE + a["href"] for a in lst.select('a[href^="/portfolio/"]')))
    pages = fetch_many(urls)
    out = []
    for u in urls:
        if not pages.get(u):
            continue
        name, desc, web, date = parse(u, pages[u])
        if not name:
            continue
        m = MONTH.match(date or "")
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, profile_url=u,
                       first_invested=m.group(2) if m else None, invested_label=date))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} 7GC companies")
    finish(out, "sevenglobalcapital", ("description", "company_url", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
