#!/usr/bin/env python3
"""PROfounders Capital portfolio scraper -> profounders_companies.json
Source: https://www.profounderscapital.com/portfolio — Webflow portfolio cards: company name (site logo
alt), problem area, country, status tag, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.profounderscapital.com/portfolio"
PRIMARY = "PROfounders Capital"


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
    for w in s.select("div.companies_card-wrap"):
        img = w.select_one(".companies_item img[alt]")
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = w.find_parent("a")
        sec = [txt(x) for x in w.select(".companies_sector-wrap > div")]
        tag = txt(w.select_one(".companies_tag"))
        out.append(rec(nm, txt(w.select_one(".text-style-5lines")), site(a) if a and a.get("href", "").startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec[0]] if sec and sec[0] else [], location=sec[1] if len(sec) > 1 else None, portfolio_status=tag,
                       status="exited" if tag and "exit" in tag.lower() else None))
    finish(out, "profounders", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
