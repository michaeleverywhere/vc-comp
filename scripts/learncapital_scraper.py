#!/usr/bin/env python3
"""Learn Capital portfolio scraper -> learncapital_companies.json
Source: https://learn.vc/ventures (learncapital.com redirects here) — the page's own
embedded Next.js data (Prismic "ventures" documents): company name, headline,
description, website ("Visit" link), Learn's category tags (education / community /
gaming / finance / health) and the acquired / public flags (-> status)."""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://learn.vc/ventures"
PRIMARY = "Learn Capital"
SECTOR_MAP = {"education": ["Future of Work"], "community": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"],
              "finance": ["FinTech / Insurance"], "health": ["Health"]}


def rt(v):
    if isinstance(v, list):
        return clean(" ".join((x.get("text") or "") for x in v if isinstance(x, dict))) or None
    return clean(v) if isinstance(v, str) else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: __NEXT_DATA__ not found")
    ventures = json.loads(m.group(1))["props"]["pageProps"]["ventures"]
    out = []
    for v in ventures:
        d = v.get("data") or {}
        name = rt(d.get("name"))
        if not name:
            continue
        head, desc = rt(d.get("headline")), rt(d.get("description"))
        url = (d.get("visit") or {}).get("url")
        status = "acquired" if d.get("acquired") else ("public" if d.get("public") else "active")
        out.append(rec(name, desc or head, url if url and not is_social(url) else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[clean(t) for t in v.get("tags") or []], sector_map=SECTOR_MAP,
                       tagline=head if desc else None, founders=rt(d.get("founders")), status=status))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Learn Capital companies")
    finish(out, "learncapital", ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
