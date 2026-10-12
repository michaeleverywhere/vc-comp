#!/usr/bin/env python3
"""Molten Ventures portfolio scraper -> molten_companies.json
Source: https://www.moltenventures.com/portfolio/all — .portfolio-row cards with
sector (title), description, Invested In year, company website, and optional
/portfolio/<slug> more-info link (used for company name).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, year_of,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.moltenventures.com/portfolio/all"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "molten_companies.json")
PRIMARY = "Molten Ventures"
SECTOR_TAG_MAP = {
    "enterprise": ["Future of Work", "Dev Tools / Cloud"],
    "digital consumer": ["Consumer"], "consumer": ["Consumer"],
    "data & infrastructure": ["Data & Analytics", "Dev Tools / Cloud"],
    "data and infrastructure": ["Data & Analytics", "Dev Tools / Cloud"],
    "hardware & deeptech": ["Deeptech / Robotics / AR/VR"],
    "hardware and deeptech": ["Deeptech / Robotics / AR/VR"],
    "digital health & wellness": ["Health"],
    "fintech": ["FinTech / Insurance"],
    "climate": ["Climate / Sustainability"],
}
TAG_OVERRIDES = {}


def name_from_row(row, desc, url):
    more = row.select_one('a.btn[href*="/portfolio/"]')
    if more:
        href = more.get("href") or ""
        m = re.search(r"/portfolio/([^/?#]+)", href)
        if m and m.group(1) not in ("spotlight", "new", "all", "exits", "open"):
            slug = m.group(1).replace("-", " ")
            # &Open special-case
            if slug == "open":
                return "&Open"
            return clean(slug.title())
    if desc:
        m = re.match(r"^([&A-Z0-9][A-Za-z0-9 .:&'’+/-]{0,40}?)(?:\s+is|\s+helps|\s+provides|\s+delivers|\s+empowers|\s+enables|\s+builds|\s+offers|\s+makes|\s+brings|\s+transforms|\s+has|\s+creates|\s+develops|\s+connects|\s+powers|\s+redefines|\s+automates|\s+gives)", desc)
        if m:
            return clean(m.group(1))
    if url:
        host = urlsplit(url).netloc.lower().removeprefix("www.")
        return clean(host.split(".")[0].replace("-", " ").title())
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for row in soup.select(".portfolio-row"):
        sector_el = row.select_one(".portfolio-row__title")
        sector = clean(sector_el.get_text(" ")) if sector_el else None
        desc_el = row.select_one(".portfolio-details__text") or row.select_one(".portfolio-details")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        url = None
        for a in row.select("a[href^=http]"):
            if "Website" in (a.get_text(" ") or "") or "moltenventures.com" not in a["href"]:
                u = clean_url(a["href"])
                if u and "moltenventures.com" not in u:
                    url = u
                    break
        first = None
        for item in row.select(".portfolio-item"):
            t = clean(item.get_text(" "))
            if t and t.lower().startswith("invested in"):
                first = year_of(t)
        name = name_from_row(row, desc, url)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "sectors": sectors,
            "first_invested": first,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "first_invested", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
