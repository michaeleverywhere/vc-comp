#!/usr/bin/env python3
"""Vestar Capital Partners portfolio scraper -> vestar_companies.json
Source: https://www.vestarcapital.com/portfolio-companies/ — WP REST `portfolio`
post type (name, detail link, portfolio_postion-current/realized and
portfolio_category-* term slugs in class_list); each detail page gives the
"Visit ... Website" link, HQ, investment date and description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish, wp_all

ORIGIN = "https://www.vestarcapital.com"
SOURCE_URL = ORIGIN + "/portfolio-companies/"
PRIMARY = "Vestar Capital Partners"
PRETTY = {"business-and-technology-services": "Business & Technology Services"}
SECTOR_MAP = {"healthcare": ["Health"], "consumer": ["Consumer"]}


def parse_detail(html, title):
    d = BeautifulSoup(html or "", "html.parser")
    for t in d(["script", "style", "nav", "footer"]):
        t.decompose()
    site = next((a["href"] for a in d.select("a[href^=http]")
                 if a.get_text(" ", strip=True).lower().startswith("visit") and not is_social(a["href"])), None)
    s = [clean(x) for x in (d.body.stripped_strings if d.body else [])]
    key = (title or "").lower()
    i = next((k for k, x in enumerate(s) if (x or "").lower() == key), None)
    if i is None:
        return site, None, None, None
    stops = ("sector information", "back to portfolio companies")
    j = next((k for k in range(i + 1, len(s)) if (s[k] or "").lower().startswith(stops)), len(s))
    body = [x for x in s[i + 1:j] if x]
    loc = body[0] if body and len(body[0]) < 60 else None
    rest = body[1:] if loc else body
    date = rest[0] if rest and len(rest[0]) < 30 and year_of(rest[0]) else None
    desc = " ".join(rest[1:] if date else rest) or None
    return site, loc, date, desc


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    ps = wp_all(ORIGIN, "portfolio")
    pages = fetch_many([p["link"] for p in ps])
    out = []
    for p in ps:
        cl = p.get("class_list") or []
        if "portfolio_category-case-study" in cl:  # case-study pages duplicate real portfolio entries
            continue
        cats = [c[len("portfolio_category-"):] for c in cl if c.startswith("portfolio_category-") and c != "portfolio_category-case-study"]
        pos = next((c.split("-", 1)[1] for c in cl if c.startswith("portfolio_postion-")), None)
        site, loc, date, desc = parse_detail(pages.get(p["link"]), html_text(p["title"]["rendered"]))
        out.append(rec(html_text(p["title"]["rendered"]), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[PRETTY.get(c) or c.replace("-", " ").title() for c in cats], sector_map=SECTOR_MAP,
                       hq_location=loc, investment_date=date, first_invested_year=year_of(date or ""),
                       portfolio_status=pos.title() if pos else None,
                       status={"current": "active", "realized": "realized"}.get(pos), detail_url=p.get("link")))
    finish(out, "vestar", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
