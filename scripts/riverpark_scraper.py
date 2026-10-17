#!/usr/bin/env python3
"""RiverPark Ventures portfolio scraper -> riverpark_companies.json
Source: https://riverparkvc.com/portfolio/ — Cube Portfolio grid: company name, sector filters
and detail page; description, location, stage, sector line and website from each company page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://riverparkvc.com/portfolio/"
PRIMARY = "RiverPark Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    labels = {re.sub(r"[^a-z0-9]", "", (txt(f) or "").lower()): txt(f) for f in s.select(".cbp-filter-item")}
    items, seen = [], set()
    for it in s.select(".cbp-item"):
        nm = txt(it.select_one(".cbp-l-caption-title"))
        a = it.select_one("a[href]")
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        cls = [c for c in it.get("class", []) if c in labels and c not in ("all", "featured")]
        items.append((nm, [labels[c] for c in cls], urljoin(SOURCE_URL, a["href"]) if a else None))
    pages = fetch_many([u for _, _, u in items if u])
    for nm, secs, u in items:
        desc = loc = stage = web = None
        h = pages.get(u) if u else None
        if h:
            d = BeautifulSoup(h, "html.parser").select_one(".theme-content")
            if d:
                for h6 in d.select("h6"):
                    t = txt(h6) or ""
                    if h6.find("a", href=True):
                        web = web or site(h6.find("a", href=True))
                    elif t.startswith("Location:"):
                        loc = clean(t[9:])
                    elif t.startswith("Stage:"):
                        stage = clean(t[6:])
                    elif t.startswith("Sector:"):
                        continue
                    elif not desc:
                        desc = t
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=secs, location=loc, stage=stage, detail_url=u))
    finish(out, "riverpark", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
