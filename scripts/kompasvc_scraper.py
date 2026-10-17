#!/usr/bin/env python3
"""KOMPAS VC portfolio scraper -> kompasvc_companies.json
Source: https://www.kompas.vc/portfolio — portfolio cards: company name (site-authored
logo alt), sector, exited flag, description and profile link."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.kompas.vc/portfolio"
PRIMARY = "KOMPAS VC"


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
    for a in s.select("a[href*='/portfolio/']"):
        img = a.find("img", alt=True)
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in a.parent.parent.stripped_strings if clean(x)]
        ex = "Exited" in ss
        rest = [x for x in ss if x not in ("Exited", nm)]
        d = next((x for x in rest if len(x) > 25), None)
        sec = next((x for x in rest if len(x) <= 25), None)
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, sector=sec, profile_url=urljoin(SOURCE_URL, a["href"]),
                       status="exited" if ex else None))
    finish(out, "kompasvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
