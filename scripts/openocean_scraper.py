#!/usr/bin/env python3
"""OpenOcean portfolio scraper -> openocean_companies.json
Source: https://www.openocean.vc/portfolio — Webflow portfolio cards: company name, description,
website, themes, stage, location and investment status."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.openocean.vc/portfolio"
PRIMARY = "OpenOcean"


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
    for it in s.select("div.portfolio_list-item"):
        nm = txt(it.select_one("[fs-cmssort-field=name]"))
        if not nm:
            continue
        g = lambda sel: txt(it.select_one(sel))
        st = g("[fs-cmsfilter-field=status]")
        web = next((site(a) for a in it.select("a[href^=http]") if site(a) and "openocean" not in a["href"]), None)
        desc = next((txt(x) for x in it.select("[fs-cmssort-field=description]") if (txt(x) or "") not in ("Themes", "Investment team", "Stage", "Location")), None)
        out.append(rec(nm, desc or g(".text-size-small"), web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[txt(x) for x in it.select("[fs-cmsfilter-field=theme]") if txt(x)], stage=g("[fs-cmsfilter-field=stage]"),
                       location=g("[fs-cmsfilter-field=location]"), portfolio_status=st,
                       status="exited" if st and "exit" in st.lower() else None))
    finish(out, "openocean", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
