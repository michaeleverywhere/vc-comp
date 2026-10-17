#!/usr/bin/env python3
"""Earth Foundry portfolio scraper -> earthfoundry_companies.json
Source: https://www.earthfoundry.com/portfolio — Webflow portfolio grid: company name, description,
status and categories."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.earthfoundry.com/portfolio"
PRIMARY = "Earth Foundry"


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
    for it in s.select("div.portfolio-item.w-dyn-item"):
        nm = txt(it.select_one("a.link-block"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        st = txt(it.select_one("[fs-cmsfilter-field=Status]"))
        a = it.select_one("a.link-block[href^=http]")
        out.append(rec(nm, txt(it.select_one(".modal-description")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[txt(x) for x in it.select(".portco-info-txt") if txt(x)], portfolio_status=st,
                       status="exited" if st and st.lower() == "exited" else None))
    finish(out, "earthfoundry", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
