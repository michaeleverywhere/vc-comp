#!/usr/bin/env python3
"""Reign Ventures portfolio scraper -> reignvc_companies.json
Source: https://www.reignvc.com/our-portfolio — portfolio cards (`li.w-64`): company
name (logo alt), founder names and profile page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.reignvc.com/our-portfolio"
PRIMARY = "Reign Ventures"


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
    for li in s.select("li.w-64"):
        img = next((i for i in li.select("img[alt]") if re.search(r"\sLogo$", i.get("alt") or "")), None)
        nm = clean(re.sub(r"\s*Logo$", "", img.get("alt"))) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = li.select_one("a[href]")
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "reignvc", ("everywhere_tags",))


if __name__ == "__main__":
    main()
