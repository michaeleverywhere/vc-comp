#!/usr/bin/env python3
"""Keen Venture Partners portfolio scraper -> keen_companies.json
Source: https://www.keenventurepartners.com/portfolio — Portfolio cards: company name, description, investment
round, year established and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.keenventurepartners.com/portfolio"
PRIMARY = "Keen Venture Partners"


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
    for c in s.select("div.card-company_item"):
        p = [clean(x).replace("\u200d", "").strip() for x in c.stripped_strings]
        p = [x for x in p if x]
        nm = p[p.index("Company:") + 1] if "Company:" in p[:-1] else None
        if not nm:
            nm = re.sub(r"^Company:\s*", "", txt(c.select_one("div.card-company_details_name")) or "").strip()
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        inv = p[p.index("Investment:") + 1] if "Investment:" in p[:-1] else None
        est = p[p.index("Established:") + 1] if "Established:" in p[:-1] else None
        d = p[0] if p and p[0] not in ("Company:",) else None
        a = c.select_one("a[href^=http]")
        out.append(rec(nm, d, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, round=inv, founded=est))
    finish(out, "keen", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
