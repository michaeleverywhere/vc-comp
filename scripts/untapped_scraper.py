#!/usr/bin/env python3
"""Untapped Capital portfolio scraper -> untapped_companies.json
Source: https://untapped.vc/ — server-rendered `article.portfolio-card` entries: company
name + website, kicker category, description and tag list."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_response, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://untapped.vc/"
PRIMARY = "Untapped Capital"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # the server omits a charset header, so decode the UTF-8 bytes explicitly
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select("article.portfolio-card"):
        h = it.find("h3")
        nm = txt(h)
        if not nm:
            continue
        tags = [txt(t) for t in it.select("li.tag") if txt(t)]
        out.append(rec(nm, txt(it.select_one("p.desc")), site(h.find("a", href=True)), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=tags))
    finish(out, "untapped", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
