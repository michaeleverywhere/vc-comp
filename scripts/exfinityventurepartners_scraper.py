#!/usr/bin/env python3
"""Exfinity Venture Partners portfolio scraper -> exfinityventurepartners_companies.json
Source: https://www.exfinityventures.com/portfolio — Bengaluru deep-tech venture firm; Next.js site whose portfolio page
lists every company card (name, Active/Exited badge, theme) and links to a company page with the one-liner, longer
description, inception year, "Partnered since" stage, theme, sector, company status, founders and website."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, year_of, stage_label, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.exfinityventures.com/portfolio"
BASE = "https://www.exfinityventures.com"
PRIMARY = "Exfinity Venture Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = []
    for a in BeautifulSoup(fetch(SOURCE_URL), "html.parser").select("a.portfolio-company-card[href]"):
        img = a.find("img", alt=True)
        name = clean(img.get("alt")) if img and clean(img.get("alt")) else clean((a.get("aria-label") or "").replace("View ", "", 1))
        st = a.select_one(".portfolio-status")
        theme = a.find("p")
        cards.append(dict(name=name, url=urljoin(BASE, a["href"]), status=clean(st.get_text()) if st else None,
                          theme=clean(theme.get_text()) if theme else None))
    pages = fetch_many([c["url"] for c in cards], workers=3, pause=0.3)
    out = []
    for c in cards:
        if not c["name"]:
            continue
        one = desc = web = sector = founders = None
        inception = partnered = None
        h = pages.get(c["url"])
        if h:
            m = BeautifulSoup(h, "html.parser").find("main")
            if m:
                for t in m(["script", "style"]):
                    t.decompose()
                strs = [clean(x) for x in m.stripped_strings if clean(x)]
                if c["name"] in strs:
                    i = strs.index(c["name"])
                    one = strs[i + 1] if i + 1 < len(strs) else None
                    desc = strs[i + 2] if i + 2 < len(strs) and len(strs[i + 2]) > 60 else None
                inception, partnered = year_of(label_after(strs, "Inception year")), label_after(strs, "Partnered since")
                sector, founders = label_after(strs, "Sector"), label_after(strs, "Founders")
                web = next((a["href"] for a in m.select("a[href^=http]")
                            if "exfinity" not in a["href"] and not is_social(a["href"])), None)
        status = (c["status"] or "").lower() or None
        out.append(rec(c["name"], one, web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in (c["theme"], sector) if x], long_description=desc,
                       founded_year=inception, partnered_since=partnered,
                       first_invested_stage=stage_label(partnered) if partnered else None,
                       founders=founders, status=status, profile_url=c["url"]))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Exfinity companies")
    finish(out, "exfinityventurepartners", ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
