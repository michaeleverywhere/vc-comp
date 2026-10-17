#!/usr/bin/env python3
"""Brooklyn Bridge Ventures portfolio scraper -> brooklynbridge_companies.json
Source: https://www.brooklynbridge.vc/portfolio — Gatsby page-data JSON for the
Full Portfolio page: company name, summary and sector tags."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.brooklynbridge.vc/portfolio"
PRIMARY = "Brooklyn Bridge Ventures"


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
    import json as _j
    data = _j.loads(fetch_response("https://www.brooklynbridge.vc/page-data/portfolio/page-data.json").content.decode("utf-8"))
    for n in data["result"]["data"]["allPrismicCompany"]["nodes"]:
        d = n.get("data") or {}
        nm = clean((d.get("name") or {}).get("text")) or clean((d.get("title") or {}).get("text"))
        if not nm:
            continue
        out.append(rec(nm, (d.get("summary") or {}).get("text"), None, PRIMARY, SOURCE_URL, scraped_at, sectors=n.get("tags") or [],
                       featured=bool(d.get("feature")), detail_url=urljoin(SOURCE_URL, "/portfolio/" + n["uid"]) if n.get("uid") else None))
    finish(out, "brooklynbridge", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
