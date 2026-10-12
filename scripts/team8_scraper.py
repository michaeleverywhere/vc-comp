#!/usr/bin/env python3
"""Team8 portfolio scraper -> team8_companies.json
Source: https://team8.vc/portfolio/ — .portfolio-card with name, tagline/desc,
Founded year. Detail pages for company websites.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             year_of, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://team8.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "team8_companies.json")
PRIMARY = "Team8"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select(".portfolio-card"):
        a = card.select_one("a[href*='/portfolio/']")
        txt = clean(card.get_text(" "))
        # name: first token before tagline; often first short heading
        # structure: Name | tagline | tagline | Founded | YYYY
        parts = [clean(x) for x in re.split(r"\s*\|\s*", card.get_text(" | ")) if clean(x)]
        name = None
        if parts:
            name = parts[0]
        if name and name.lower() in ("founded", "+"):
            name = None
        if not name and a:
            m = re.search(r"/portfolio/([^/]+)/?", a["href"])
            if m:
                name = clean(m.group(1).replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = None
        # tagline-like: parts that aren't Founded/year/name
        for p in parts[1:]:
            if p.lower() in ("founded", name.lower()):
                continue
            if re.fullmatch(r"\d{4}", p or ""):
                continue
            if len(p) > 10:
                desc = p
                break
        founded = year_of(txt)
        detail = a["href"] if a and a.get("href") else None
        if detail and not detail.startswith("http"):
            detail = "https://team8.vc" + detail
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "founded_year": founded,
            "detail_url": detail,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.15)
    for r in out:
        html = pages.get(r.pop("detail_url", None))
        if html:
            ds = BeautifulSoup(html, "html.parser")
            if not r.get("description"):
                for p in ds.select("p"):
                    t = clean(p.get_text(" "))
                    if t and len(t) > 40:
                        r["description"] = t
                        break
            r["company_url"] = clean_url(first_external_link(ds, ("team8.vc",)))
            r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "founded_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
