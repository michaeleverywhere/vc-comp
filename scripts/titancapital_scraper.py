#!/usr/bin/env python3
"""Titan Capital (India) portfolio scraper -> titancapital_companies.json
Source: https://titancapital.vc/portfolio — the page is fed by the firm's own public
Sanity CMS (project suel5z6g, dataset production); the portfolioGrid singleton holds
every company on the grid: brand name, one-liner + about text, website, founders,
founding year, investment stage (funding round), sector, status tags (Recent
Investment / Unicorn / IPO / Exited), fund vintage ("2025-26") and a milestones line
("Founded 2023, Partnered 2025") giving the year Titan first invested."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urlencode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://titancapital.vc/portfolio"
API = "https://suel5z6g.api.sanity.io/v2021-10-21/data/query/production"
PRIMARY = "Titan Capital"
GROQ = ('*[_type=="portfolioGrid"][0].companies[]{brandName,oneLiner,about,website,"founders":founders[].name,'
        'foundingYear,fundType,investmentStage,sector,status,milestones,year}')
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "consumer brand": ["CPG"],
              "consumer tech": ["Consumer"], "ai & saas": ["Dev Tools / Cloud"]}


def as_list(v):
    return [clean(x) for x in (v if isinstance(v, list) else [v]) if clean(x)]


def site(w):
    w = clean(w)
    if not w:
        return None
    if not w.startswith("http"):
        w = "https://" + w.lstrip("/")
    return None if is_social(w) else w


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows = fetch(API + "?" + urlencode({"query": GROQ}), as_json=True)["result"] or []
    out = []
    for c in rows:
        name = clean(c.get("brandName"))
        if not name:
            continue
        tags = as_list(c.get("status"))
        low = [t.lower() for t in tags]
        status = "public" if "ipo" in low else ("exited" if "exited" in low else "active")
        m = re.search(r"Partnered\s+((?:19|20)\d{2})", c.get("milestones") or "")
        vint = re.match(r"((?:19|20)\d{2})", clean(c.get("year")) or "")
        first = int(m.group(1)) if m else (int(vint.group(1)) if vint else None)
        stage = as_list(c.get("investmentStage"))
        sectors = as_list(c.get("sector"))
        desc = clean(c.get("about")) or clean(c.get("oneLiner"))
        out.append(rec(name, desc, site(c.get("website")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, sector_map=SECTOR_MAP, tagline=c.get("oneLiner"),
                       founders=as_list(c.get("founders")), founded_year=clean(c.get("foundingYear")),
                       stage=", ".join(stage) or None, fund=clean(c.get("fundType")),
                       fund_vintage=clean(c.get("year")), first_invested=first,
                       portfolio_tags=tags, status=status))
    finish(out, "titancapital", ("description", "company_url", "stage", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
