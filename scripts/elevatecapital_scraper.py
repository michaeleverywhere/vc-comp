#!/usr/bin/env python3
"""Elevate Capital portfolio scraper -> elevatecapital_companies.json
Source: https://elevate.vc/portfolio/ — Elementor portfolio archive (paginated): status
badge and detail page; company name (page heading) and description from each page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://elevate.vc/portfolio/"
PRIMARY = "Elevate Capital"


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
    url, seen, items = SOURCE_URL, set(), []
    while url and url not in seen:
        seen.add(url)
        s = soup_of(url)
        for c in s.select(".elementor-post__card"):
            a = c.select_one("a[href]")
            if a:
                items.append((a["href"], txt(c.select_one(".elementor-post__badge"))))
        nx = s.select_one("a.page-numbers.next[href], .elementor-pagination a.next[href]")
        url = nx["href"] if nx else None
    pages = fetch_many(list(dict.fromkeys(u for u, _ in items)))
    for u, badge in items:
        h = pages.get(u)
        if not h:
            continue
        d = BeautifulSoup(h, "html.parser")
        nm = txt(d.select_one("h1")) or clean((txt(d.title) or "").split(" - Elevate")[0])
        if not nm:
            continue
        m = d.find("meta", attrs={"name": "description"}) or d.find("meta", attrs={"property": "og:description"})
        web = next((x for x in d.select("a[href^='http']") if site(x) and (txt(x) or "").lower().startswith("visit ")), None)
        b = (badge or "").lower()
        out.append(rec(nm, m.get("content") if m else None, site(web), PRIMARY, SOURCE_URL, scraped_at, portfolio_status=badge,
                       status="exited" if any(w in b for w in ("exit", "acquir")) else ("active" if "active" in b else None), detail_url=u))
    finish(out, "elevatecapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
