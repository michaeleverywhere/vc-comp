#!/usr/bin/env python3
"""Hetz Ventures portfolio scraper -> hetz_companies.json
Source: https://www.hetz.vc/our-portfolio — Webflow CMS (.cl-item-portfolio)
with name, tagline, year, sector tag, acquired badge, and Visit website link.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.hetz.vc/our-portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hetz_companies.json")
PRIMARY = "Hetz Ventures"
SECTOR_MAP = {
    "cybersecurity": ["Cybersecurity"], "applied ai": [], "devtools": ["Dev Tools / Cloud"],
    "infrastructure": ["Dev Tools / Cloud"], "enterprise": [], "fintech": ["FinTech / Insurance"],
}
TAG_OVERRIDES = {}
SKIP_TOKENS = {"hiring", "acquired", "reset all", "visit website", "read more"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".cl-item-portfolio.w-dyn-item"):
        tags = [clean(t.get_text(" ")) for t in it.select(".hidden-tag") if clean(t.get_text(" "))]
        texts = [clean(t) for t in it.stripped_strings if clean(t)]
        # filter chrome
        content = [t for t in texts if t.lower() not in SKIP_TOKENS and not t.lower().startswith("acquired by")]
        # remaining typically: sector(s already in tags), name, tagline, year
        name = desc = None
        year = None
        for t in content:
            if t in tags:
                continue
            if re.fullmatch(r"(19|20)\d\d", t):
                year = int(t)
                continue
            if not name and len(t) < 60:
                name = t
                continue
            if name and not desc and len(t) > 15:
                desc = t
        if not name:
            a = it.select_one("a[href*='/portfolio/']")
            if a:
                slug = a["href"].rstrip("/").split("/")[-1]
                name = clean(slug.replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        website = None
        for a in it.find_all("a", href=True):
            href = a["href"]
            label = (clean(a.get_text(" ")) or "").lower()
            if label == "visit website" and href.startswith("http"):
                website = clean_url(href)
                break
        status = None
        acquirer = None
        if it.select_one(".square-tag.is-acquired") and "w-condition-invisible" not in " ".join(it.select_one(".square-tag.is-acquired").get("class", [])):
            status = "acquired"
        # also check acquired-wrapper visibility
        for t in texts:
            if t.lower().startswith("acquired by"):
                status = "acquired"
                acquirer = clean(re.sub(r"(?i)^acquired by\s*", "", t))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": tags,
            "first_invested": year,
            "status": status,
            "acquirer": acquirer,
            "everywhere_tags": tags_for(name, desc, tags, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
