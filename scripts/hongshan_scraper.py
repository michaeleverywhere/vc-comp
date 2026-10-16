#!/usr/bin/env python3
"""HongShan (formerly Sequoia China) portfolio scraper -> hongshan_companies.json
Source: https://www.hongshan.com/companies/ — WP REST `company` (name, sector
class) plus each company page: description (Chinese), website, sector label.
Names and descriptions are kept exactly as published (Chinese).
"""
import os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, fetch_many, is_social
from _d50_common import rec, finish, wp_all, page_strings

ORIGIN = "https://www.hongshan.com"
SOURCE_URL = "https://www.hongshan.com/companies/"
PRIMARY = "HongShan"
SECTOR_MAP = {"healthcare": ["Health"], "医疗": ["Health"], "consumer": ["Consumer"], "消费": ["Consumer"],
              "technology": [], "科技": [], "industrial": ["Deeptech / Robotics / AR/VR"], "工业": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "company")
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        st, s = page_strings(pages.get(p["link"]) or "")
        desc = site = label = None
        if len(st) > 2:
            desc = st[2] if len(st[2]) > 20 else None
            if len(st) > 4:
                label = st[4] if len(st[4]) < 12 else None
        if pages.get(p["link"]):
            for a in s.select("a[href^=http]"):
                if "hongshan" not in a["href"] and not is_social(a["href"]):
                    site = a["href"]; break
        cls = [c[len("sector-"):] for c in p.get("class_list") or [] if c.startswith("sector-")]
        m = re.search(r"[（(]((?:NASDAQ|NYSE|SEHK|HKEX|SSE|SZSE|上交所|深交所|港交所)[^)）]*)[)）]", desc or "")
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=[x for x in [label] + cls if x],
                       sector_map=SECTOR_MAP, listing=m.group(1) if m else None, status="ipo" if m else None,
                       detail_url=p["link"]))
    finish(out, "hongshan", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
