#!/usr/bin/env python3
"""MEVP portfolio scraper -> mevp_companies.json
Source: https://mevp.com/portfolio — Webflow portfolio cards: company name, description,
location, sector, stage (incl. Exited) and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://mevp.com/portfolio"
PRIMARY = "MEVP"


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
    for it in s.select("div.port_collection-item.w-dyn-item"):
        nm = txt(it.select_one(".text-block-20"))
        if not nm:
            continue
        g = lambda k: txt(it.select_one(f"[fs-cmsfilter-field={k}]"))
        a = it.select_one("a.port_collection-link2[href]")
        stage = g("stage")
        sec = g("sector")
        out.append(rec(nm, txt(it.select_one("p.port_card-p")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       location=g("location"), stage=stage, status="exited" if stage and "exit" in stage.lower() else None,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "mevp", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
