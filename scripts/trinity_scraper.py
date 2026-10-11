#!/usr/bin/env python3
"""Trinity Ventures portfolio scraper -> trinity_companies.json
Source: https://www.trinityventures.com/portfolio — server-rendered grid; each
<a class="m-company-list__item"> links to /portfolio/<slug>, with the name in
its title ("View <Name> details") / logo alt and an optional status badge
(Acquired / IPO). Detail pages carry the description paragraph(s) and the
company website (first external link that is not Trinity's own or a browser-
upgrade link). status: Acquired -> acquired; IPO kept in site_status. No
location, round or year published.
Empty descriptions filled from company websites (scripts/fill_descriptions_web.py)
are carried forward on re-runs.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, fetch_many, clean, tags_for, clean_url, first_external_link,
                             prune_substring_tags, apply_tag_overrides,
                             carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://www.trinityventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "trinity_companies.json")
PRIMARY = "Trinity Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Mapper.ai": ["Transportation / Mobility", "Data & Analytics"],
    "Funnel": ["PropTech"],
    "Beautiful.AI": ["Future of Work"],
}
SKIP = ("mozilla.org", "google.com/chrome", "microsoft.com", "/jobs", "jobs.", "svdcdn.com")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for a in soup.select("a.m-company-list__item[href]"):
        href = urljoin(SOURCE_URL, a["href"])
        if href in seen:
            continue
        seen.add(href)
        m = re.match(r"View (.+) details$", a.get("title") or "")
        img = a.select_one("img")
        name = clean(m.group(1)) if m else clean(re.sub(r"\s*logo$", "", (img.get("alt") if img else "") or ""))
        st = a.select_one(".m-company-list__status")
        rows.append({"name": name, "href": href, "status": clean(st.get_text(" ")) if st else None})
    pages = fetch_many([r["href"] for r in rows], workers=6)
    out, names = [], set()
    for r in rows:
        if not r["name"] or r["name"].lower() in names:
            continue
        names.add(r["name"].lower())
        desc = site = None
        html = pages.get(r["href"])
        if html:
            d = BeautifulSoup(html, "html.parser")
            site = first_external_link(d, ("trinityventures.com",), SKIP)
            site = clean_url(site) if site else None
            for t in d(["script", "style", "nav", "header", "footer"]):
                t.decompose()
            paras = [clean(p.get_text(" ")) for p in d.select("main p, article p, .content p, p") if clean(p.get_text(" "))]
            paras = [p for p in paras if len(p) > 40 and "browser" not in p.lower()]
            desc = paras[0] if paras else None
        st = r["status"]
        out.append({
            "company_name": r["name"],
            "description": desc,
            "company_url": site,
            "site_status": st,
            "status": "acquired" if (st or "").lower() == "acquired" else None,
            "everywhere_tags": tags_for(r["name"], desc),
            "primary_investor": PRIMARY,
            "profile_url": r["href"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in carry_forward_descriptions(out, OUT):  # filled earlier by fill_descriptions_web.py
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "site_status", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
