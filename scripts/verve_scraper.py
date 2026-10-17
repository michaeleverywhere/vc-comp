#!/usr/bin/env python3
"""Verve Ventures portfolio scraper -> verve_companies.json
Source: https://www.verve.vc/ — WordPress REST post type "verve_portfolio_new" (name,
description, portfolio-status Holding / Exit / Pre-close, portfolio-industry) plus each
company's public detail page for website, "Located in", "Invested since" (first invested
year), investment topic and one-line mission. Verve is a Zurich-based European deep tech VC."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, clean, html_text, is_social
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://www.verve.vc"
SOURCE_URL = "https://www.verve.vc/portfolio/"
PRIMARY = "Verve Ventures"
STATUS = {"holding": "active", "exit": "exited", "pre-close": "active"}
SECTOR_MAP = {"health & bio": ["Health"]}


def detail(html):
    f = {}
    if not html:
        return f
    s = BeautifulSoup(html, "html.parser")
    for d in s.select("div.vc_sw-acf"):
        lab = d.select_one(".sw-acf-field-label")
        if lab:
            key = clean(lab.get_text(" ", strip=True)).lower()
            lab.extract()
            f[key] = clean(d.get_text(" ", strip=True))
        elif "type-url" in (d.get("class") or []):
            a = d.select_one("a[href^=http]")
            if a and not is_social(a["href"]) and "verve.vc" not in a["href"] and "website" not in f:
                f["website"] = a["href"]
    m = s.select_one(".data-field--mission .data-field-value")
    if m:
        f["mission"] = clean(m.get_text(" ", strip=True))
    return f


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "verve_portfolio_new")
    st, ind = wp_terms(ORIGIN, "portfolio-status"), wp_terms(ORIGIN, "portfolio-industry")
    pages = fetch_many([p["link"] for p in posts], workers=3, pause=0.3)
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        f = detail(pages.get(p["link"]))
        desc = html_text(p["content"]["rendered"]) or f.get("mission")
        status_names = [st.get(i, "") for i in p.get("portfolio-status") or []]
        status = next((STATUS[x.lower()] for x in status_names if x.lower() in STATUS), None)
        sectors = [ind[i] for i in p.get("portfolio-industry") or [] if ind.get(i)]
        topic = f.get("investment topic")
        if topic:
            sectors.append(topic)
        yr = f.get("invested since")
        out.append(rec(name, desc, f.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, sector_map=SECTOR_MAP, location=f.get("located in"),
                       first_invested=yr if yr and re.fullmatch(r"(19|20)\d\d", yr) else None,
                       tagline=f.get("mission"), status=status, detail_url=p["link"]))
    finish(out, "verve", ("description", "company_url", "location", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
