#!/usr/bin/env python3
"""Lightstone Ventures portfolio scraper -> lightstone_companies.json
Source: https://www.lightstonevc.com/ — WP REST `portfolio` posts (name,
description, status/sector/fund taxonomies via class_list) joined to the
homepage popups (website, lead partner, fund, location) by company name.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup, Comment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, html_text
from _d50_common import rec, finish

SOURCE_URL = "https://www.lightstonevc.com/"
API = "https://www.lightstonevc.com/wp-json/wp/v2/portfolio?per_page=100"
PRIMARY = "Lightstone Ventures"
STATUS = {"company-active": "active", "company-acquired": "acquired", "company-ipo": "ipo", "company-public": "ipo",
          "company-legacy-deals": None}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = fetch(API, as_json=True)
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    pop = {}
    for h in soup.select(".popup-holder"):
        nm = None
        for c in h.find_all(string=lambda s: isinstance(s, Comment)):
            m = re.search(r"<h2>(.*?)</h2>", c, re.S)
            if m:
                nm = html_text(m.group(1))
                break
        if not nm:
            continue
        info = {}
        for li in h.select("li"):
            dt, dd = li.select_one(".dt"), li.select_one(".dd")
            if dt and dd:
                info[clean(dt.get_text()).rstrip(":").lower()] = clean(dd.get_text(" ", strip=True))
        iv = h.select_one(".info")
        info["status_text"] = clean(iv.get_text(" ", strip=True)) if iv else None
        a = h.select_one("a.link-site[href]")
        info["website"] = a["href"] if a else None
        info["sectors"] = [x.replace("-", " ") for x in (h.get("data-sector") or "").split() if x]
        pop[nm.lower()] = info
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        cl = p.get("class_list") or []
        status = None
        for c in cl:
            if c.startswith("company-"):
                status = STATUS.get(c, c.replace("company-", "").replace("-", " "))
        info = pop.get((name or "").lower(), {})
        st = (info.get("status_text") or "").lower()
        if not status:
            status = next((v for k, v in (("acquired", "acquired"), ("ipo", "ipo"), ("public", "ipo"),
                                         ("active", "active"), ("closed", "closed")) if k in st), None)
        out.append(rec(name, html_text(p["content"]["rendered"]), info.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=info.get("sectors") or [], location=info.get("location"), lead_partner=info.get("lead"),
                       fund=info.get("fund"), status=status))
    finish(out, "lightstone", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
