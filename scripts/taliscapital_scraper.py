#!/usr/bin/env python3
"""Talis Capital portfolio scraper -> taliscapital_companies.json
Source: https://www.taliscapital.com/portfolio/ — the site's own public WordPress REST list of
"portfolio" posts (/wp-json/wp/v2/portfolio): company name, Talis stage term (Seed / Series A /
Series B / Growth -> stage), region term (United Kingdom / Europe / USA -> location) and the
"Exited" status term; plus each company's Talis profile page: description, founded year,
year invested (-> first_invested) and website ("View website")."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish, wp_all

SOURCE_URL = "https://www.taliscapital.com/portfolio/"
ORIGIN = "https://www.taliscapital.com"
PRIMARY = "Talis Capital"


def terms(tax):
    return {t["id"]: t["name"] for t in fetch(f"{ORIGIN}/wp-json/wp/v2/{tax}?per_page=100&_fields=id,name", as_json=True)}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "portfolio", "&_fields=id,slug,link,title,status,seed,location")
    st, sd, loc = terms("status"), terms("seed"), terms("location")
    pages = fetch_many([p["link"] for p in posts], workers=3, pause=0.3)
    out = []
    for p in posts:
        name = clean(BeautifulSoup(p["title"]["rendered"], "html.parser").get_text())
        stat = [st.get(i) for i in (p.get("status") or []) if st.get(i)]
        stage = [sd.get(i) for i in (p.get("seed") or []) if sd.get(i)]
        where = [loc.get(i) for i in (p.get("location") or []) if loc.get(i)]
        desc = url = founded = invested = None
        h = pages.get(p["link"])
        if h:
            s = BeautifulSoup(h, "html.parser")
            txt = re.sub(r"\s+", " ", s.get_text(" ", strip=True))
            m = re.search(r"Founded (\d{4}) Invested (\d{4}) (.*?) Founded \d{4} Invested \d{4}", txt)
            if m:
                founded, invested, desc = int(m.group(1)), int(m.group(2)), clean(m.group(3))
            else:
                founded = year_of((re.search(r"Founded (\d{4})", txt) or [None])[0]) if re.search(r"Founded (\d{4})", txt) else None
                mi = re.search(r"Invested (\d{4})", txt); invested = int(mi.group(1)) if mi else None
            a = next((x for x in s.find_all("a", href=True) if re.search(r"view website", x.get_text(" ", strip=True), re.I)), None)
            if a and a.get("href", "").startswith("http") and not is_social(a["href"]) and "taliscapital.com" not in a["href"]:
                url = a["href"]
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at,
                       stage=stage[0] if stage else None, location=where[0] if where else None,
                       founded_year=founded, first_invested=invested,
                       status="Exited" if "Exited" in stat else None, profile_url=p["link"]))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Talis companies")
    finish(out, "taliscapital", ("description", "company_url", "stage", "location", "founded_year",
                                  "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
