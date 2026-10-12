#!/usr/bin/env python3
"""Quona Capital portfolio scraper -> quona_companies.json
Source: https://quona.com/portfolio/ — each .companyAnchor links to an on-page
#slug section with name, description, and company website domain.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://quona.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "quona_companies.json")
PRIMARY = "Quona Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "payments": ["FinTech / Insurance"],
    "lending": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"],
    "banking": ["FinTech / Insurance"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.companyAnchor[href]"):
        name = clean(a.get_text(" "))
        href = a.get("href") or ""
        slug = href.split("#")[-1].strip() if "#" in href else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc, url, loc = None, None, None
        section = None
        if slug:
            section = soup.find(id=slug) or soup.find(id=f"company_{slug}") or soup.find(id=lambda x: x and x.lower() in {slug.lower(), f"company_{slug.lower()}"})
        if section:
            tagline_el = section.select_one(".cpSubtex")
            tagline = clean(tagline_el.get_text(" ")) if tagline_el else None
            body_el = section.select_one(".cptBl2") or section.select_one(".cpTtext")
            body = clean(body_el.get_text(" ")) if body_el else None
            txt = clean(" ".join(x for x in (tagline, body) if x)) or clean(section.get_text(" "))
            # strip chrome / name
            if txt and txt.lower().startswith(name.lower()):
                txt = clean(txt[len(name):])
            m = re.search(r"\b((?:www\.)?[a-z0-9-]+\.[a-z]{2,}(?:\.[a-z]{2,})?)\s*$", txt or "", re.I)
            if m:
                url = clean_url("https://" + m.group(1).removeprefix("www."))
                txt = clean(txt[:m.start()])
            # also look for domain-only link text inside section
            if not url:
                for a2 in section.select("a[href^=http]"):
                    u = clean_url(a2["href"])
                    if u and "quona.com" not in u:
                        url = u
                        break
            if not url:
                m2 = re.search(r"\b((?:www\.)?[a-z0-9-]+\.[a-z]{2,}(?:\.[a-z]{2,})?)\b", body or "", re.I)
                if m2 and "quona" not in m2.group(1).lower():
                    url = clean_url("https://" + m2.group(1).removeprefix("www."))
                    body = clean((body or "").replace(m2.group(0), ""))
                    txt = clean(" ".join(x for x in (tagline, body) if x))
            desc = txt
        # region from nearest h2 ancestor section
        parent = a
        for _ in range(12):
            parent = parent.parent if parent else None
            if not parent:
                break
            h2 = parent.find("h2")
            if h2:
                loc = clean(h2.get_text(" "))
                break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "location": loc,
            "everywhere_tags": tags_for(name, desc, None, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    # Quona is fintech-for-emerging-markets; ensure FinTech when untagged but has desc
    for r in out:
        if not r["everywhere_tags"] and r.get("description"):
            r["everywhere_tags"] = tags_for(r["company_name"], r["description"] + " fintech", None, SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
