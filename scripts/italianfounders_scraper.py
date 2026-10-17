#!/usr/bin/env python3
"""Italian Founders Fund portfolio scraper -> italianfounders_companies.json
Source: https://www.italianfoundersfund.com/ — homepage portfolio pop-ups: company name,
country, sector, stage, description, website and founders."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.italianfoundersfund.com/"
PRIMARY = "Italian Founders Fund"


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
    for c in s.select(".card-portfolio"):
        nm = txt(c.select_one(".pop-up-portfolio h3"))
        if not nm:
            continue
        tr = [txt(x) for x in c.select(".card-trigger .div-block-6 > div") if txt(x)]
        flag = c.select_one(".card-trigger img.image-7")
        web = next((a for a in c.select(".pop-up-portfolio a[href^='http']") if site(a)), None)
        founders = [clean(i.get("alt")) for i in c.select(".founder-item img") if clean(i.get("alt"))]
        out.append(rec(nm, txt(c.select_one(".portfolio_text")), site(web), PRIMARY, SOURCE_URL, scraped_at, sectors=tr[:1],
                       stage=tr[1] if len(tr) > 1 else None, country=clean(flag.get("alt")) if flag else None, founders=founders))
    finish(out, "italianfounders", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
