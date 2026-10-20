#!/usr/bin/env python3
"""Ride Home Fund portfolio scraper -> ridehomefund_companies.json
Source: https://www.ridehomefund.com/rolling-fund — portfolio cards on the Rolling Fund page plus the
Ride Home AI Fund page (https://www.ridehomefund.com/ai-fund): company name, description, exit banner
("Acquired by …") and the company website; fund records which Ride Home vehicle lists the company."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.ridehomefund.com/rolling-fund"
PAGES = [(SOURCE_URL, "Rolling Fund"), ("https://www.ridehomefund.com/ai-fund", "Ride Home AI Fund")]
PRIMARY = "Ride Home Fund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    by = {}
    for url, fund in PAGES:
        s = BeautifulSoup(fetch(url), "html.parser")
        for c in s.select("article.card"):
            n = c.select_one(".card__name")
            name = clean(n.get_text(" ", strip=True)) if n else None
            if not name:
                continue
            d = c.select_one(".card__desc")
            b = c.select_one(".card__banner")
            a = c.select_one("a.card__btn[href^=http]")
            r = by.setdefault(name.lower(), {"name": name, "funds": []})
            r["funds"].append(fund)
            r.setdefault("desc", clean(d.get_text(" ", strip=True)) if d else None)
            banner = clean(b.get_text(" ", strip=True)) if b else None
            if banner:
                r["banner"] = banner
            if a and not is_social(a["href"]) and "ridehomefund.com" not in a["href"]:
                r.setdefault("url", a["href"])
    out = []
    for r in by.values():
        ban = r.get("banner")
        acq = re.match(r"Acquired by (.+)", ban or "", re.I)
        out.append(rec(r["name"], r.get("desc"), r.get("url"), PRIMARY, SOURCE_URL, scraped_at,
                       fund=list(dict.fromkeys(r["funds"])), acquired_by=acq.group(1) if acq else None,
                       status="acquired" if acq else "active", exit_note=ban))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Ride Home Fund companies")
    finish(out, "ridehomefund", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
