#!/usr/bin/env python3
"""Lumia Capital portfolio scraper -> lumia_companies.json
Source: https://lumiacapital.com/companies/ — Portfolio grid: company name (site logo alt)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://lumiacapital.com/companies/"
PRIMARY = "Lumia Capital"


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
    seen = set()
    own = {'lumia capital'}
    for it in s.select('div.portfolios__grid__item'):
        img = it.select_one("img[alt]")
        nm = clean(re.sub(r"[\s\-]*(logo|Logo|LOGO)( tile| white| black)?$", "", img.get("alt") or "")) if img else None
        if not nm or nm.lower() in seen or nm.lower() in own or len(nm) > 60:
            continue
        seen.add(nm.lower())
        a = it if it.name == "a" else None
        if a is None or not a.get("href", "").startswith(("http", "//")):
            a = next((x for x in it.select("a[href]") if x["href"].startswith(("http", "//"))), None)
        u = None
        if a is not None and False:
            u = a["href"]
            u = "https:" + u if u.startswith("//") else u
        p = [clean(x) for x in it.stripped_strings if clean(x)]
        p = [x for x in p if x.lower() not in ("view fullsize", "find out more", "visit website", "learn more", nm.lower())]
        st = "exited" if any(x.lower() in ("exited", "exit", "acquired", "ipo") for x in p) else None
        d = next((x for x in p if len(x) > 25), None) if False else None
        out.append(rec(nm, d, u, PRIMARY, SOURCE_URL, scraped_at, status=st))
    finish(out, "lumia", ("everywhere_tags",))


if __name__ == "__main__":
    main()
