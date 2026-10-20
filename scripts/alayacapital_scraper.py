#!/usr/bin/env python3
"""ALAYA Capital portfolio scraper -> alayacapital_companies.json
Source: https://alaya-capital.com/portfolio/ — every company in Alaya's own WordPress portfolio
(avada_portfolio posts, the same records the portfolio grid links to) plus each company's Alaya
profile page: company name, Alaya's headline, description and the company website ("WEB" link)."""
import html, os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://alaya-capital.com/portfolio/"
API = "https://alaya-capital.com/wp-json/wp/v2/avada_portfolio?per_page=100&page={}&_fields=id,slug,title,link"
PRIMARY = "ALAYA Capital"


def posts():
    out, page = [], 1
    while True:
        d = fetch(API.format(page), as_json=True)
        out += d
        if len(d) < 100:
            return out
        page += 1


def profile(h, own):
    if not h:
        return {}
    s = BeautifulSoup(h, "html.parser")
    c = s.select_one(".fusion-content-tb") or s
    head = c.select_one("h2.fusion-title-heading")
    paras = [clean(p.get_text(" ", strip=True)) for p in c.select(".fusion-text p")]
    paras = [p for p in paras if p and p.upper() not in ("WEB", "CEO") and not p.lower().startswith("supporting the sdg")]
    web = None
    for a in c.select("a[href^=http]"):
        t = clean(a.get_text(" ", strip=True)) or ""
        if "alaya-capital.com" in a["href"] or is_social(a["href"]):
            continue
        if t.upper() == "WEB" or web is None:
            web = a["href"]
            if t.upper() == "WEB":
                break
    return {"headline": clean(head.get_text(" ", strip=True)) if head else None,
            "description": " ".join(paras) or None, "website": web}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    ps = posts()
    pages = fetch_many([p["link"] for p in ps])
    out = []
    for p in ps:
        name = clean(html.unescape(p["title"]["rendered"]))
        if not name:
            continue
        pr = profile(pages.get(p["link"]), name)
        out.append(rec(name, pr.get("description"), pr.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       headline=pr.get("headline"), profile_url=p["link"]))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Alaya companies")
    finish(out, "alayacapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
