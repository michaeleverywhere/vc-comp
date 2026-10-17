#!/usr/bin/env python3
"""Practica Capital portfolio scraper -> practica_companies.json
Source: https://practica.vc/en/investments — Investments cards: company name, sector and stage."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://practica.vc/en/investments"
PRIMARY = "Practica Capital"


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
    for c in s.select("div.card"):
        nm = txt(c.select_one("h4"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in c.stripped_strings if clean(x) and clean(x) != "Read more"]
        i = p.index(nm) if nm in p else 0
        sec = [x.strip() for x in p[0].split("|")] if i > 0 else []
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sec, stage=p[i + 1] if len(p) > i + 1 else None))
    finish(out, "practica", ("everywhere_tags",))


if __name__ == "__main__":
    main()
