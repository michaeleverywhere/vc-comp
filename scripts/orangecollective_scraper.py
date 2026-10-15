#!/usr/bin/env python3
"""Orange Collective portfolio scraper -> orangecollective_companies.json
Source: https://www.orangecollective.vc/portfolio — JSON-LD ItemList of YC
portfolio companies (name + relative portfolio URL). Detail pages for desc/batch.
"""
import os, json, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://www.orangecollective.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "orangecollective_companies.json")
PRIMARY = "Orange Collective"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for sc in soup.find_all("script", type=lambda t: t and "ld+json" in str(t).lower()):
        try:
            d = json.loads(sc.string)
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") == "ItemList":
            items = d.get("itemListElement") or []
            break
    pairs = []
    for it in items:
        name = clean(it.get("name"))
        url = it.get("url")
        if name and url:
            pairs.append((name, urljoin(SOURCE_URL, url)))
    pages = fetch_many([u for _, u in pairs], workers=6, pause=0.1)
    out, seen = [], set()
    for name, url in pairs:
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        html = pages.get(url) or ""
        dsoup = BeautifulSoup(html, "html.parser") if html else None
        desc = batch = None
        if dsoup:
            # YC-style one-liner often in first substantial p or meta
            for el in dsoup.select("p, h2, h3"):
                t = clean(el.get_text(" "))
                if t and len(t) > 20 and t != name:
                    desc = t
                    break
            text = dsoup.get_text(" ")
            import re
            m = re.search(r"\b([WSFP]\d{2})\b", text)
            if m:
                batch = m.group(1)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,  # site links to OC detail, not company site
            "yc_batch": batch,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "yc_batch", "everywhere_tags"))


if __name__ == "__main__":
    main()
