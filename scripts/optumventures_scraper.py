#!/usr/bin/env python3
"""Optum Ventures portfolio scraper -> optumventures_companies.json
Source: https://www.optumventures.com/portfolio — Webflow portfolio table + panels: company name,
description, founded and invested years, stage (incl. Exited), leaders, location and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.optumventures.com/portfolio"
PRIMARY = "Optum Ventures"


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
    for it in s.select("div.company-card.w-dyn-item"):
        nm = txt(it.select_one("[fs-cmsfilter-field=Title]"))
        if not nm:
            continue
        f = lambda k: txt(it.select_one(f"[fs-cmsfilter-field={k}]"))
        det = {}
        for d in it.select(".cp-detail-item"):
            ks = d.select("div")
            if len(ks) >= 2:
                det[(txt(ks[0]) or "").strip()] = txt(ks[1])
        web = next((site(a) for a in it.select(".company-panel a[href^=http]") if site(a)), None)
        stage = f("stage")
        out.append(rec(nm, f("Desc") or txt(it.select_one(".company-panel-header h1")), web, PRIMARY, SOURCE_URL, scraped_at,
                       founded_year=f("founded"), invested_year=f("invested"), stage=stage, leaders=det.get("Leaders(s)"),
                       location=det.get("Location"), status="exited" if stage and "exit" in stage.lower() else None))
    finish(out, "optumventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
