#!/usr/bin/env python3
"""Draft Ventures portfolio scraper -> draft_companies.json
Source: https://draftvc.com/ — Notion-hosted portfolio page; each toggle block is a
company: linked name (website), optional status marker such as (IPO) or
(Acquired), and a one-line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://draftvc.com/"
PRIMARY = "Draft Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select(".notion-toggle"):
        summ = it.select_one(".notion-toggle__summary")
        a = summ.find("a", href=True) if summ else None
        nm = txt(a)
        if not nm:
            continue
        mark = txt(summ.select_one(".highlighted-color"))
        low = (mark or "").lower()
        out.append(rec(nm, txt(it.select_one(".notion-toggle__content")), site(a), PRIMARY, SOURCE_URL, scraped_at,
                       exit_note=mark.strip("()") if mark else None,
                       status="public" if "ipo" in low else ("acquired" if "acqui" in low else None)))
    finish(out, "draft", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
