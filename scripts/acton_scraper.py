#!/usr/bin/env python3
"""Acton Capital portfolio scraper -> acton_companies.json
Source: https://www.actoncapital.com/portfolio — Webflow CMS list (one
`.companies-c-item` per company: name, category, Active/Exited state) plus each
company's detail page (/portfolio/<slug>): claim (tagline), description,
Founded, Founders, Exit (acquirer / IPO text), Initial Investment (year),
Category, Base (city, country) and "Visit Company Website".
status: Exited -> acquired, Active -> active. No funding rounds published.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, year_of, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.actoncapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "acton_companies.json")
PRIMARY = "Acton Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "health": ["Health"],
    "b2c": ["Consumer"], "logistics": ["Logistics / Supply Chain"],
    "legaltech": ["RegTech/Gov/Legal"], "cyber security": ["Cybersecurity"],
}
TAG_OVERRIDES = {}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for it in soup.select(".companies-c-item.w-dyn-item"):
        a = it.select_one("a.companies-list-link[href]")
        if not a:
            continue
        href = urljoin(SOURCE_URL, a["href"])
        if href in seen:
            continue
        seen.add(href)
        ps = it.select("p.display-none")
        cat = clean(ps[0].get_text(" ")) if len(ps) > 0 else None
        state = clean(it.select_one("[fs-cmsfilter-field=state]").get_text(" ")) if it.select_one("[fs-cmsfilter-field=state]") else None
        rows.append((clean(a.get_text(" ")), href, cat, state))
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r[1] for r in rows], workers=6)
    out = []
    for name, href, cat, state in rows:
        rec = {"company_name": name, "description": None, "tagline": None, "company_url": None,
               "founded_year": None, "founders": [], "exit": None, "first_invested": None,
               "category": cat, "location": None, "city": None, "country": None,
               "site_status": state, "status": None}
        html = pages.get(href)
        if html:
            d = BeautifulSoup(html, "html.parser")
            box = d.select_one(".team-member-content") or d
            h = box.select_one("h2")
            if h and clean(h.get_text(" ")):
                rec["company_name"] = clean(h.get_text(" "))
            cl = box.select_one(".team-detail-claim")
            rec["tagline"] = clean(cl.get_text(" ")) if cl else None
            tx = box.select_one("p.text")
            rec["description"] = clean(tx.get_text(" ")) if tx else None
            f = {}
            for row in box.select(".company-table-row"):
                if "w-condition-invisible" in (row.get("class") or []):
                    continue
                lab = row.find("p")
                if not lab:
                    continue
                key = clean(lab.get_text(" ")).lower()
                if key == "base":
                    city = row.select_one(".city"); country = row.select_one(".country")
                    f["city"] = clean(city.get_text(" ")) if city else None
                    f["country"] = clean(country.get_text(" ")) if country else None
                else:
                    val = row.select_one(".text-right")
                    f[key] = clean(val.get_text(" ")) if val else None
            rec["founded_year"] = year_of(f.get("founded"))
            rec["founders"] = [x.strip() for x in (f.get("founders") or "").split(",") if x.strip()]
            rec["exit"] = f.get("exit")
            m = re.match(r"(?i)acquired by (.+?)(?: in ((?:19|20)\d{2}))?$", rec["exit"] or "")
            rec["acquirer"] = clean(m.group(1)) if m else None
            rec["exit_year"] = year_of(rec["exit"])
            rec["first_invested"] = year_of(f.get("initial investment"))
            rec["category"] = f.get("category") or cat
            rec["city"], rec["country"] = f.get("city"), f.get("country")
            rec["location"] = ", ".join(x for x in (rec["city"], rec["country"]) if x) or None
            btn = next((x for x in box.select("a[href^=http]") if "website" in x.get_text(" ").lower()), None)
            rec["company_url"] = clean_url(btn["href"]) if btn else None
        st = (state or "").lower()
        rec["status"] = "acquired" if st == "exited" else ("active" if st == "active" else None)
        sectors = [rec["category"]] if rec["category"] else []
        rec["sectors"] = sectors
        rec["everywhere_tags"] = tags_for(rec["company_name"], " ".join(x for x in (rec["tagline"], rec["description"]) if x), sectors, SECTOR_TAG_MAP)
        rec.update({"primary_investor": PRIMARY, "profile_url": href, "source_url": SOURCE_URL, "scraped_at": scraped_at})
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
