#!/usr/bin/env python3
"""Data Point Capital portfolio scraper -> datapoint_companies.json
Source: https://www.datapointcapital.com/datapoint-portfolio/ — Elementor flip boxes:
company name, description (the 'DPC Lead' partner split out) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.datapointcapital.com/datapoint-portfolio/"
PRIMARY = "Data Point Capital"


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
    for fb in s.select("div.elementor-flip-box"):
        back = fb.select_one(".elementor-flip-box__back")
        nm = txt(back.select_one(".elementor-flip-box__layer__title")) if back else None
        if not nm:
            continue
        d = txt(back.select_one(".elementor-flip-box__layer__description")) or ""
        m = re.search(r"\s*DPC Leads?:\s*(.+)$", d)
        lead = clean(m.group(1)) if m else None
        d = d[:m.start()] if m else d
        out.append(rec(nm, d, site(back) if back.name == "a" else None, PRIMARY, SOURCE_URL, scraped_at, dpc_lead=lead))
    finish(out, "datapoint", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
