#!/usr/bin/env python3
"""Translink Capital portfolio scraper -> translinkcapital_companies.json
Source: https://www.translinkcapital.com/portfolio — Webflow CMS portfolio grid (all paginated list pages):
each card gives Translink's vertical, stage, one-line tagline and status; each /portfolio/<slug> company
page adds the company name, CEO, country, status, website and the "About" description."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, fetch_many, webflow_pages, label_after, is_social, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://www.translinkcapital.com/portfolio"
PRIMARY = "Translink Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = {}
    for html in webflow_pages(SOURCE_URL):
        s = BeautifulSoup(html, "html.parser")
        for it in s.select("div.portfolio-item-wrapper.w-dyn-item"):
            a = it.select_one("a.portfolio-item-link[href]")
            if not a:
                continue
            u = urljoin(SOURCE_URL, a["href"])
            ind = [clean(x.get_text(" ", strip=True)) for x in it.select('[fs-cmsfilter-field="industry"]')]
            st = it.select_one('[fs-cmsfilter-field="status"]')
            tl = it.select_one("p.p2")
            stage = None
            for t in it.select("div.p3--portfolio-item--data-title"):
                if clean(t.get_text()) == "Stage:":
                    v = t.find_next_sibling("div")
                    stage = clean(v.get_text(" ", strip=True)) if v else None
            cards.setdefault(u, dict(sectors=[x for x in ind if x], status=clean(st.get_text(" ", strip=True)) if st else None,
                                     tagline=clean(tl.get_text(" ", strip=True)) if tl else None, stage=stage))
    pages = fetch_many(list(cards), workers=4, pause=0.3)
    out = []
    for u, c in cards.items():
        h = pages.get(u)
        name = desc = web = ceo = country = None
        status = c["status"]
        if h:
            d = BeautifulSoup(h, "html.parser")
            for t in d(["script", "style", "nav", "footer"]):
                t.decompose()
            strs = [x for x in (clean(z) for z in d.stripped_strings) if x]
            name = clean((d.title.string or "").split("|")[0]) if d.title and d.title.string else None
            ceo = label_after(strs, "CEO")
            country = label_after(strs, "Country")
            status = label_after(strs, "Status") or status
            desc = label_after(strs, "About")
            for a in d.select("a[href^=http]"):
                href = a["href"].strip()
                if "translinkcapital.com" not in href and not is_social(href):
                    web = href
                    break
        if not name:
            continue
        st = (status or "").lower()
        out.append(rec(name, desc or c["tagline"], web, PRIMARY, SOURCE_URL, scraped_at, sectors=c["sectors"],
                       tagline=c["tagline"], stage=stage_label(c["stage"]) or c["stage"], ceo=ceo, location=country,
                       translink_status=status, profile_url=u,
                       status="acquired" if re.search(r"exit|acquir|ipo|public", st) else ("active" if st == "active" else None)))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Translink companies")
    finish(out, "translinkcapital", ("description", "company_url", "sectors", "stage", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
