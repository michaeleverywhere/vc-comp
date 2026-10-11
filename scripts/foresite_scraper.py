#!/usr/bin/env python3
"""Foresite Capital portfolio scraper -> foresite_companies.json
Source: https://www.foresitecapital.com/portfolio/ — WordPress; each
<article class="portfolio-block <categories>"> links to a detail page and its
name carries "(Alumni)" for former holdings. Category classes (therapeutics,
life-sciences, healthcare-tech-and-services, biopharmaceutical) -> sectors.
Detail pages give the company website (first header link), a public ticker
tag when listed (e.g. "NASDAQ: TXG") and Foresite's narrative paragraph(s).
description = the first paragraph. stage / first_invested only when that
narrative explicitly states Foresite's first investment round, e.g. "We made
our first investment in X in the Series A financing in November of 2013".
Alumni / ticker kept in site_status; no lead status is asserted.
"""
import os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, fetch_many, clean, tags_for, clean_url, year_of, stage_label,
                             prune_substring_tags, apply_tag_overrides, is_social)
from _d20_common import write_out

SOURCE_URL = "https://www.foresitecapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "foresite_companies.json")
PRIMARY = "Foresite Capital"
CATS = {"therapeutics": "Therapeutics", "life-sciences": "Life Sciences",
        "healthcare-tech-and-services": "Healthcare Tech and Services", "biopharmaceutical": "Biopharmaceutical"}
SECTOR_TAG_MAP = {"therapeutics": ["BioTech"], "biopharmaceutical": ["BioTech"], "life sciences": ["BioTech"],
                  "healthcare tech and services": ["Health"]}
TAG_OVERRIDES = {}
FIRST_RX = re.compile(r"[^.]*\bfirst invest\w*[^.]*?\b(pre-seed|seed|series [a-h])\b[^.]*\.", re.I)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for art in soup.select("article.portfolio-block"):
        a = art.select_one(".portfolio-block__header a[href]")
        if not a or a["href"] in seen:
            continue
        seen.add(a["href"])
        raw = clean(a.get_text(" "))
        alumni = "(alumni)" in (raw or "").lower()
        name = clean(re.sub(r"\(\s*alumni\s*\)", "", raw or "", flags=re.I))
        cats = [CATS[c] for c in art.get("class", []) if c in CATS]
        rows.append({"name": name, "href": a["href"], "alumni": alumni, "cats": cats})
    pages = fetch_many([r["href"] for r in rows], workers=6)
    out, names = [], set()
    for r in rows:
        if not r["name"] or r["name"].lower() in names:
            continue
        names.add(r["name"].lower())
        site = ticker = desc = stage = None
        first = None
        html = pages.get(r["href"])
        if html:
            d = BeautifulSoup(html, "html.parser")
            for a in d.select(".portfolio-single__header a[href^=http]"):
                if not is_social(a["href"]):
                    site = clean_url(a["href"])
                    break
            t = d.select_one(".nasdaq-tag__text")
            ticker = clean(t.get_text(" ")) if t else None
            paras = [clean(p.get_text(" ")) for p in d.select(".portfolio-single__content p") if clean(p.get_text(" "))]
            desc = paras[0] if paras else None
            full = " ".join(paras)
            m = FIRST_RX.search(full)
            if m:
                stage = stage_label(m.group(1))
                first = year_of(m.group(0))
        site_status = ", ".join(x for x in (("Alumni" if r["alumni"] else None), ticker) if x) or None
        out.append({
            "company_name": r["name"],
            "description": desc,
            "company_url": site,
            "sectors": r["cats"],
            "stage": stage,
            "first_invested": first,
            "ticker": ticker,
            "site_status": site_status,
            "everywhere_tags": tags_for(r["name"], desc, r["cats"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": r["href"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "stage", "first_invested", "ticker", "everywhere_tags"))


if __name__ == "__main__":
    main()
