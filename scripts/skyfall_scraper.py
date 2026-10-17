#!/usr/bin/env python3
"""Skyfall Ventures portfolio scraper -> skyfall_companies.json
Source: https://www.skyfall.vc/portfolio — Webflow portfolio list (all paginated pages):
company name, description, co-investors, initial investment year, status and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.skyfall.vc/portfolio"
PRIMARY = "Skyfall Ventures"


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
    seen = set()
    s0 = soup_of(SOURCE_URL)
    keys = sorted({m for a in s0.select("a[href*=_page]") for m in re.findall(r"(\w+)_page=", a["href"])})
    pages = [s0]
    for k in keys:
        for n in range(2, 30):
            sp = soup_of(f"{SOURCE_URL}?{k}_page={n}")
            if not sp.select("div.company-row_wrapper"):
                break
            pages.append(sp)
            if not sp.select(f"a[href*='{k}_page={n + 1}']"):
                break
    for s in pages:
        for r in s.select("div.company-row_wrapper"):
            p = [txt(x) for x in r.select(".list_company-name > div")]
            nm = p[0] if p else None
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            co = r.select(".list_coinvestors > div")
            a = r.select_one(".list_website a[href^=http]")
            out.append(rec(nm, p[1] if len(p) > 1 else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                           co_investors=txt(co[1]) if len(co) > 1 else None, initial_investment_year=txt(r.select_one(".list_year")),
                           portfolio_status=txt(r.select_one(".list_status"))))
    finish(out, "skyfall", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
