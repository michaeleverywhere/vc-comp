#!/usr/bin/env python3
"""IGNIA portfolio scraper -> ignia_companies.json
Source: https://www.ignia.vc/portfolio — Webflow portfolio list: company name, fund, status,
year, sectors, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ignia.vc/portfolio"
PRIMARY = "IGNIA"


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
    for it in s.select(".collection-item-9"):
        nm = txt(it.select_one(".heading_look-card"))
        if not nm:
            continue
        top = [txt(x) for x in it.select(".icons_tags-wrapper .small_heading-card") if txt(x)]
        secs = [txt(x) for x in it.select(".tags-wrapper.no-align .small_heading-card") if txt(x)]
        st = next((x for x in top if x.lower() in ("active", "exited", "realized", "written off")), None)
        secs = [x for x in secs if x.lower() not in ("active", "exited", "realized", "written off")]
        web = next((a for a in it.select("a.button[href^='http']") if site(a)), None)
        out.append(rec(nm, txt(it.select_one(".portfolio_info-wrapper p")), site(web), PRIMARY, SOURCE_URL, scraped_at, sectors=secs,
                       fund=top[0] if top else None, vintage_year=next((year_of(x) for x in top if year_of(x)), None), portfolio_status=st,
                       status="exited" if st and st.lower() != "active" else ("active" if st else None)))
    finish(out, "ignia", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
