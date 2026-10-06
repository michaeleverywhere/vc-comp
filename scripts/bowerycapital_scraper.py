#!/usr/bin/env python3
"""Bowery Capital portfolio scraper -> bowerycapital_companies.json
Source: https://bowerycap.com/portfolio — Craft CMS, one server-rendered table.
Each row: logo (alt "<Name> logo"), description, city, website link and an
"Exited" flag. Name casing is recovered from the description when the logo alt
differs only by case. status = acquired only when the site's own text says the
company was acquired / sold / merged; other exits keep site_status "Exited".
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://bowerycap.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bowerycapital_companies.json")
PRIMARY = "Bowery Capital"
ACQ = re.compile(r"(?i)\b(acquired by|sold to|merged with|acquisition by|was acquired)\b")


def recover_case(name, desc):
    m = re.search(r"(?i)(?<![\w])" + re.escape(name) + r"(?![\w])", desc or "")
    return m.group(0) if m and m.group(0).lower() == name.lower() else name


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for row in soup.select("[data-test=portfolio-result]"):
        logo = next((i for i in row.select("img[alt]") if i.get("alt", "").lower().endswith(" logo")), None)
        if not logo:
            continue
        name = re.sub(r"(?i)\s+logo$", "", clean(logo["alt"]))
        p = row.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        name = recover_case(name, desc)
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        cols = row.select(":scope > div")
        city = None
        tail = row.select_one(".md\\:basis-1\\/5")
        if tail:
            c = tail.select_one("div")
            city = clean(c.get_text(" ")) if c else None
        a = row.select_one("a[href^='http']")
        exited = any("exited" in (i.get("alt", "") + i.get("src", "")).lower() for i in row.select("img")) or \
            (clean(row.get_text(" ")) or "").startswith("Exited")
        status = "acquired" if exited and ACQ.search(desc or "") else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": a["href"].strip() if a else None,
            "status": status,
            "site_status": "Exited" if exited else None,
            "location": city,
            "everywhere_tags": tags_for(name, desc, []),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
