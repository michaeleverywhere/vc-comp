#!/usr/bin/env python3
"""MAYA Capital portfolio scraper -> maya_companies.json
Source: https://maya.capital/portfolio — Portfolio table: company name, description, sector,
website, co-investors and founders."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://maya.capital/portfolio"
PRIMARY = "MAYA Capital"


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
    for d in s.select("details.collapse-table"):
        sm = d.select_one("summary")
        sp = [txt(x) for x in sm.select("span")] if sm else []
        nm = sp[0] if sp else None
        if not nm:
            continue
        p = list(d.stripped_strings)
        def after(lbl):
            if lbl in p:
                i = p.index(lbl)
                return p[i + 1] if i + 1 < len(p) else None
            return None
        f = []
        if "Founders" in p:
            f = p[p.index("Founders") + 1:]
        web = after("Website")
        out.append(rec(nm, sp[1] if len(sp) > 1 else None, ("https://" + web) if web and not web.startswith("http") else web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x.strip() for x in (after("Sector") or "").split(",") if x.strip()], co_investors=after("Co-Investors"),
                       founders=", ".join(f) or None))
    finish(out, "maya", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
