#!/usr/bin/env python3
"""Vibe Capital portfolio scraper -> vibecapital_companies.json
Source: https://vibe.vc/portfolio — Notion portfolio gallery: company name, sector, region
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://vibe.vc/portfolio"
PRIMARY = "Vibe Capital"


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
    for t in s.select("div.notion-property__title"):
        card = t.find_parent("a") or t.parent
        nm = txt(t)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in card.stripped_strings if clean(x) and clean(x) != nm]
        web = next((x for x in p if re.match(r"^(www\.|https?://)", x)), None)
        tags = [x for x in p if x != web]
        a = card.select_one("a[href^=http]")
        u = a["href"] if a else (("https://" + web) if web and web.startswith("www.") else web)
        out.append(rec(nm, None, u, PRIMARY, SOURCE_URL, scraped_at, sectors=tags[:1], location=tags[1] if len(tags) > 1 else None))
    finish(out, "vibecapital", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
