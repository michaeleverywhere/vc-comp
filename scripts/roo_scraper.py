#!/usr/bin/env python3
"""Roo Capital portfolio scraper -> roo_companies.json
Source: https://roocapital.com/companies — Next.js company cards: name (logo alt),
stage, sector tags, description, website and case study."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://roocapital.com/companies"
PRIMARY = "Roo Capital"


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
    for c in s.select("div.group\\/card"):
        nm = next((clean(i.get("alt")) for i in c.select("img") if clean(i.get("alt"))), None)
        if not nm:
            continue
        tags = [txt(x) for x in c.select("span.text-p-sm") if txt(x)]
        stages = [t for t in tags if re.search(r"(?i)seed|series|growth", t)]
        web = next((a for a in c.select("a[href^='http']") if site(a)), None)
        cs = c.select_one("a[href^='/case-studies/']")
        out.append(rec(nm, txt(c.select_one("p")), site(web), PRIMARY, SOURCE_URL, scraped_at, sectors=[t for t in tags if t not in stages],
                       stage=stages[0] if stages else None, case_study_url=urljoin(SOURCE_URL, cs["href"]) if cs else None))
    finish(out, "roo", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
