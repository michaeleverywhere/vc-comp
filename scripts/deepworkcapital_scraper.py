#!/usr/bin/env python3
"""DeepWork Capital portfolio scraper -> deepworkcapital_companies.json
Source: https://www.deepworkcapital.com/portfolio — the portfolio gallery's own captions: company
name (caption title), one-line description, location (city, state) and the site's outcome line
("Acquired by X" -> status + acquirer, "Exited", "Nasdaq: TICK" -> ticker), plus the company's
DeepWork profile page link."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.deepworkcapital.com/portfolio"
PRIMARY = "DeepWork Capital"
LOC = re.compile(r"^[A-Z][A-Za-z .'-]+, ([A-Z]{2}|[A-Z][a-z]+)$")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for cap in s.select(".caption-container"):
        h = cap.select_one(".caption-title")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        lines = [clean(p.get_text(" ", strip=True)) for p in cap.select(".caption-text p")]
        lines = [x for x in lines if x]
        desc = loc = status = acquirer = ticker = None
        for x in lines:
            m = re.match(r"(?i)^acquired by (.+)$", x)
            mt = re.match(r"(?i)^(nasdaq|nyse|tsx|asx)\s*:\s*([A-Z.]+)$", x)
            if m:
                status, acquirer = "Acquired", clean(m.group(1))
            elif mt:
                status, ticker = "Public", f"{mt.group(1).upper() if mt.group(1).lower() != 'nasdaq' else 'Nasdaq'}: {mt.group(2)}"
            elif re.match(r"(?i)^exited$", x):
                status = "Exited"
            elif LOC.match(x) and not loc:
                loc = x
            elif not desc:
                desc = x
        wrap = cap.find_parent(class_="thumbnailInnerWrapper") or cap.parent
        a = wrap.find("a", href=True) if wrap else None
        prof = urljoin(SOURCE_URL, a["href"]) if a and a["href"].startswith("/") and len(a["href"]) > 1 else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, location=loc, status=status,
                       acquirer=acquirer, ticker=ticker, profile_url=prof))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} DeepWork companies")
    finish(out, "deepworkcapital", ("description", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
