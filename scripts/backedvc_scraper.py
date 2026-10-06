#!/usr/bin/env python3
"""Backed VC portfolio scraper -> backedvc_companies.json
Source: https://www.backed.vc/portfolio — Webflow + Finsweet CMS filter. Each
card carries name, one-liner and three filter fields (sector, region, stage);
each /portfolio/<slug> detail page adds Year Backed, Stage, website and a long
description. The card "status" filter field holds the investment stage
(Pre-Seed/Seed/Series A), so it is mapped to `stage`, not lead status.
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, round_label, label_after, year_of, is_social

BASE = "https://www.backed.vc"
SOURCE_URL = BASE + "/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "backedvc_companies.json")
PRIMARY = "Backed VC"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "health": ["Health"], "healthcare": ["Health"],
    "consumer": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
    "crypto": ["Web3 / Crypto"], "web3": ["Web3 / Crypto"], "climate": ["Climate / Sustainability"],
    "future of work": ["Future of Work"], "deeptech": ["Deeptech / Robotics / AR/VR"],
    "developer tools": ["Dev Tools / Cloud"], "proptech": ["PropTech"], "mobility": ["Transportation / Mobility"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for card in soup.select(".portfolio_card"):
        h = card.select_one(".portfolio_card-heading")
        name = clean(h.get_text()) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        a = card.select_one("a.card_link[href]")
        f = {el.get("fs-cmsfilter-field"): clean(el.get_text()) for el in card.select("[fs-cmsfilter-field]")}
        p = card.select_one(".portfolio_par")
        rows.append({"name": name, "profile": urljoin(BASE, a["href"]) if a else None,
                     "blurb": clean(p.get_text(" ")) if p else None, **{k: v for k, v in f.items() if k}})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows if r["profile"]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        for t in d(["script", "style", "nav", "footer", "svg"]):
            t.decompose()
        main_el = d.select_one("main") or d
        strings = list(main_el.stripped_strings)
        year = year_of(label_after(strings, "Year Backed"))
        stage_raw = label_after(strings, "Stage") or r.get("status")
        site = None
        for a in main_el.select("a[href^='http']"):
            if clean(a.get_text()) == "Website" and not is_social(a["href"]):
                site = a["href"].strip()
                break
        longd = None
        if "Careers" in strings or "Website" in strings:
            idx = max(i for i, s in enumerate(strings) if s in ("Website", "Careers"))
            cand = clean(strings[idx + 1]) if idx + 1 < len(strings) else None
            if cand and cand != "Founders" and len(cand) > 40:
                longd = cand
        desc = longd or r["blurb"]
        sectors = [r["sector"]] if r.get("sector") and r["sector"] != "Other" else []
        out.append({
            "company_name": r["name"],
            "description": desc,
            "tagline": r["blurb"],
            "company_url": site,
            "company_profile_url": r["profile"],
            "status": None,
            "stage": round_label(stage_raw),
            "investment_stage_raw": stage_raw,
            "first_invested": year,
            "location": r.get("region"),
            "sectors": sectors,
            "everywhere_tags": tags_for(r["name"], desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "stage", "first_invested", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
