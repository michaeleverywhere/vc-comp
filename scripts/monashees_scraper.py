#!/usr/bin/env python3
"""Monashees portfolio scraper -> monashees_companies.json
Source: https://www.monashees.com/portfolio — Framer page; featured company
links with nearby text. Caveat: featured subset on the public portfolio page.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.monashees.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "monashees_companies.json")
PRIMARY = "Monashees"
TAG_OVERRIDES = {}


def name_from_url(url):
    host = urlparse(url).netloc.lower().replace("www.", "")
    base = host.split(".")[0]
    return base.replace("-", " ").title() if base else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "monashees" in href or is_social(href):
            continue
        img = a.find("img")
        text = clean(a.get_text(" "))
        name = None
        desc = None
        if text and len(text) > 2:
            # "Vambe AI Agentic Marketing SMBs Vambe is..."
            words = text.split()
            name = words[0]
            if len(words) > 1 and words[1] in ("AI",) or (len(words) > 1 and words[1][0].isupper() and len(words[1]) < 10):
                if len(words) > 1 and words[1][0].isupper():
                    name = words[0] + " " + words[1]
            # description: longer remainder
            if len(text) > len(name) + 10:
                desc = clean(text[len(name):])
        if not name:
            name = (clean(img.get("alt")) if img and img.get("alt") and "logo" not in img.get("alt", "").lower() else None) or name_from_url(href)
        if not name or name.lower() in seen:
            continue
        if name.lower() in ("wordmark logo", "logo"):
            name = name_from_url(href)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": desc if desc and len(desc) > 20 else None,
            "company_url": clean_url(href),
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
