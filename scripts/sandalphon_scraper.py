#!/usr/bin/env python3
"""Sandalphon Capital portfolio scraper -> sandalphon_companies.json
Source: https://sandalphoncapital.com/portfolio/ — portfolio grid: company name, sector/fund/
stage tags and company link (description and website from the detail page where the tile
links to one)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://sandalphoncapital.com/portfolio/"
PRIMARY = "Sandalphon Capital"


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
    items = []
    for a in s.select("a.portfolio-container-progression"):
        nm = txt(a.select_one(".invested-portfolio-title"))
        if nm:
            tags = [clean(li.get_text().replace("·", "")) for li in a.select("ul.progressoin-portfolio-tax li")]
            items.append((nm, [t for t in tags if t], urljoin(SOURCE_URL, a["href"])))
    internal = [u for _, _, u in items if "sandalphoncapital.com" in u]
    pages = fetch_many(internal)
    for nm, tags, u in items:
        fund = next((t for t in tags if t.lower().startswith("fund")), None)
        stage = next((t for t in tags if t.lower().startswith("stage")), None)
        secs = [t for t in tags if t not in (fund, stage)]
        stage = clean(re.sub(r"(?i)^stage\s*-\s*", "", stage)) if stage else None
        if u not in internal:
            out.append(rec(nm, None, u, PRIMARY, SOURCE_URL, scraped_at, sectors=secs, fund=fund, stage=stage))
            continue
        d = BeautifulSoup(pages.get(u) or "", "html.parser")
        body = d.select_one(".portfolio-single-content, .entry-content, #content-pro")
        desc = None
        if body is not None:
            ps = [txt(p) for p in body.find_all("p") if txt(p)]
            desc = ps[0] if ps else None
        web = next((x for x in d.select("a[href^='http']") if site(x) and "sandalphon" not in x["href"] and txt(x) and ("site" in txt(x).lower() or "visit" in txt(x).lower() or "." in txt(x))), None)
        out.append(rec(nm, desc, site(web), PRIMARY, SOURCE_URL, scraped_at, sectors=secs, fund=fund, stage=stage, detail_url=u))
    finish(out, "sandalphon", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
