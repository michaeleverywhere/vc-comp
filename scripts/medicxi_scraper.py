#!/usr/bin/env python3
"""Medicxi portfolio scraper -> medicxi_companies.json
Source: https://www.medicxi.com/companies — life-sciences venture firm (London / Geneva); server-rendered company
grid (one tile per company opening /companies/view/<slug>); each company view adds the company name (with the
listing ticker where the site shows one), description, CEO, HQ country, the Medicxi team members on the company
and the company website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.medicxi.com/companies"
PRIMARY = "Medicxi"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    urls = []
    for a in s.select("div.company a[onclick]"):
        m = re.search(r"showCompany\('([^']+)'\)", a["onclick"])
        if m and m.group(1) not in urls:
            urls.append(m.group(1))
    pages = fetch_many(urls, workers=4, pause=0.2)
    out = []
    for u in urls:
        h = pages.get(u)
        if not h:
            continue
        d = BeautifulSoup(h, "html.parser")
        h1 = d.find("h1")
        raw = clean(h1.get_text(" ", strip=True)) if h1 else None
        if not raw:
            continue
        # site titles carry notes after the name: "Ariad - Acquired by Takeda (NASDAQ: ARIA)", "Addex (Swiss ADXN.SW)"
        name = clean(re.split(r"\s+-\s+|\s*\(", raw, maxsplit=1)[0])
        tick = re.findall(r"\(([^)]+)\)", raw)
        ticker = clean(tick[-1]) if tick else None
        note = clean(raw[len(name):].strip(" -")) or None
        if not name:
            continue
        strs = [x for x in (clean(z) for z in d.stripped_strings) if x]
        desc = next((x for x in strs if x != raw and len(x) > 40), None)
        team = [clean(a.get_text(" ", strip=True)) for a in d.select("a[href^='/team/']")]
        web = None
        for a in d.select("a[href^=http]"):
            if "medicxi.com" not in a["href"] and not is_social(a["href"]):
                web = a["href"]
                break
        st = "acquired" if re.search(r"(?i)acquired|merged", note or "") else ("public" if note and note.startswith("(") else None)
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, ticker=ticker, site_title=raw, exit_note=note, status=st,
                       ceo=label_after(strs, "CEO"), location=label_after(strs, "HQ"),
                       medicxi_team=[t for t in team if t], profile_url=u))
    if len(out) < 50:
        raise SystemExit(f"FATAL: only {len(out)} Medicxi companies")
    finish(out, "medicxi", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
