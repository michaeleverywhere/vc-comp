#!/usr/bin/env python3
"""Zenda portfolio scraper -> zenda_companies.json
Source: https://www.zenda.vc/portfolio/ — server-rendered WordPress grid: company name,
one-line description, HQ, named co-investors, website and exit note (e.g.
"Acquired by Stripe"). Unnamed "STEALTH" tiles are skipped."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.zenda.vc/portfolio/"
PRIMARY = "Zenda"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in s.select("li.grid-item"):
        t = it.select_one(".title")
        name = clean(t.get_text(" ", strip=True)) if t else None
        if not name or name.upper() == "STEALTH" or name.lower() in seen:
            continue
        seen.add(name.lower())
        body = it.select_one(".body")
        info = {}
        for dt in it.select("dl.list dt"):
            dd = dt.find_next_sibling("dd")
            info[(clean(dt.get_text(" ", strip=True)) or "").lower()] = clean(dd.get_text(" ", strip=True)) if dd else None
        bottom = clean(it.select_one(".bottom").get_text(" ", strip=True)) if it.select_one(".bottom") else None
        a = it.select_one("a.view-website-button[href^=http]")
        co = [x.strip() for x in (info.get("co-investors") or "").split(",") if x.strip()]
        out.append(rec(name, clean(body.get_text(" ", strip=True)) if body else None,
                       a["href"].strip() if a and not is_social(a["href"]) else None, PRIMARY, SOURCE_URL, scraped_at,
                       location=info.get("hq") or None, co_investors=co, exit_note=bottom or None,
                       status="acquired" if bottom and re.search(r"acqui", bottom, re.I) else ("exited" if bottom else "active")))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Zenda companies")
    finish(out, "zenda", ("description", "company_url", "location", "co_investors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
