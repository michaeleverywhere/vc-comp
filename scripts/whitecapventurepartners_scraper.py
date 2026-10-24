#!/usr/bin/env python3
"""Whitecap Venture Partners portfolio scraper -> whitecapventurepartners_companies.json
Source: https://www.whitecapvp.com/portfolio — Whitecap Venture Partners, Toronto-based early-stage venture capital
firm. Each portfolio card gives the sector, status, company website and a short bio. The site shows company names
only as logos, so the name is taken from the start of the bio and kept only when it matches the company's own
website domain (unconfirmable cards are skipped rather than guessed)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.whitecapvp.com/portfolio"
PRIMARY = "Whitecap Venture Partners"
SUFFIX = ("", "hq", "app", "ai", "inc", "co", "io", "labs", "health", "tech", "group", "software")
PREFIX = ("", "get", "try", "use", "join", "go", "my")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def stem(url):
    host = urlparse(url or "").netloc.lower().split(":")[0]
    host = re.sub(r"^www\d?\.", "", host)
    parts = host.split(".")
    return parts[0] if parts and parts[0] else None


def name_from(bio, url):
    st = stem(url)
    if not bio or not st:
        return None
    words = bio.split()
    for k in range(min(6, len(words)), 0, -1):
        cand = clean(re.sub(r"['\u2019]s$", "", " ".join(words[:k]).rstrip(",.:;")))
        n = norm(cand)
        if len(n) < 2:
            continue
        if any(st == p + n + s for p in PREFIX for s in SUFFIX):
            return cand
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen, skipped = [], set(), []
    for item in soup.select(".collection-fund-item"):
        a = item.select_one("a.fund-item-logo-wrap[href]")
        url = a["href"] if a else None
        bio_el = item.select_one(".fund-item-bio")
        bio = clean(bio_el.get_text(" ")) if bio_el else None
        name = name_from(bio, url)
        if not name:
            skipped.append(url)
            continue
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        sec = item.select_one(".fund-sector")
        stt = item.select_one(".fund-company-status")
        sec_t = clean(sec.get_text(" ")) if sec else None
        st_t = clean(stt.get_text(" ")) if stt and "w-dyn-bind-empty" not in (stt.get("class") or []) else None
        out.append(rec(name, bio, url, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec_t] if sec_t else None,
                       status=st_t or "Active"))
    print(f"skipped {len(skipped)} unconfirmable cards: {skipped}", file=sys.stderr)
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Whitecap companies")
    finish(out, "whitecapventurepartners", ("description", "website", "everywhere_tags"))


if __name__ == "__main__":
    main()
