#!/usr/bin/env python3
"""Humba Ventures portfolio scraper -> humba_companies.json
Source: https://humbaventures.com/ — homepage PORTFOLIO section, grouped by core
theme: one-line description with the named company and its homepage link (stealth
entries without a name are skipped)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://humbaventures.com/"
PRIMARY = "Humba Ventures"


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
    h = s.find(id="portfolio")
    theme = None
    for el in h.find_next_siblings() if h else []:
        if el.name in ("h1", "h2", "h3"):
            break
        if el.name == "h4":
            theme = txt(el)
            continue
        if el.name != "p" or not theme:
            continue
        line = []
        for node in list(el.children) + [None]:
            if node is None or getattr(node, "name", None) == "br":
                a = next((x for x in line if getattr(x, "name", None) == "a"), None)
                if a is not None and txt(a):
                    raw = clean("".join(x if isinstance(x, str) else x.get_text() for x in line)) or ""
                    d = clean(re.sub(r"\(\s*" + re.escape(a.get_text()) + r"\s*\)", "", raw))
                    d = clean(re.sub(r"^[^A-Za-z0-9]+", "", d or ""))
                    out.append(rec(txt(a), d, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[theme]))
                line = []
            else:
                line.append(node)
    finish(out, "humba", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
