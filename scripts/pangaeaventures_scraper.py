#!/usr/bin/env python3
"""Pangaea Ventures portfolio scraper -> pangaeaventures_companies.json
Source: https://pangaeaventures.com/portfolio — Pangaea Ventures (Vancouver), hard-tech / advanced-materials venture
firm. Current companies each have a page with a tagline, description and website link; exited companies are listed
on https://pangaeaventures.com/exited-companies with a name and description."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://pangaeaventures.com/portfolio"
EXIT_URL = "https://pangaeaventures.com/exited-companies"
PRIMARY = "Pangaea Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    urls = []
    for a in s.select("a[href^='/portfolio/']"):
        u = urljoin(SOURCE_URL, a["href"])
        if u not in urls:
            urls.append(u)
    pages = fetch_many(urls)
    out, seen = [], set()
    for u in urls:
        html = pages.get(u)
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        m = d.find("main") or d
        h = m.find("h2", class_=lambda c: not c or "item-pagination-title" not in c)
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name or name.lower() in seen:
            continue
        ps = [clean(p.get_text(" ", strip=True)) for p in m.find_all("p")]
        ps = [p for p in ps if p and p not in ("Back to portfolio", "Visit website", "Next", "Previous")]
        tag = ps[0] if len(ps) > 1 else None
        desc = ps[1] if len(ps) > 1 else (ps[0] if ps else None)
        web = None
        for a in m.find_all("a", href=True):
            if a["href"].startswith("http") and not is_social(a["href"]) and "pangaea" not in a["href"]:
                web = a["href"]
                break
        seen.add(name.lower())
        out.append(rec(name, desc, web, PRIMARY, u, scraped_at, tagline=tag, status="active"))
    x = BeautifulSoup(fetch(EXIT_URL), "html.parser")
    for sec in x.select("section[data-section-id]"):
        h = sec.find(["h1", "h2", "h3"])
        name = clean(h.get_text(" ", strip=True).replace("\u200b", "")) if h else None
        if not name or name.lower() in seen:
            continue
        p = h.find_next("p")
        desc = clean(p.get_text(" ", strip=True)) if p and sec in p.parents else None
        seen.add(name.lower())
        out.append(rec(name, desc, None, PRIMARY, EXIT_URL, scraped_at, status="exited"))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Pangaea companies")
    finish(out, "pangaeaventures", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
