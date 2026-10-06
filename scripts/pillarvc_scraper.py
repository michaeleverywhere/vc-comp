#!/usr/bin/env python3
"""Pillar VC portfolio scraper -> pillarvc_companies.json
Source: https://www.pillar.vc/companies/ — WordPress, one server-rendered
table: name, "<year>, <stage at investment>" (e.g. "2024, Pre-seed (First
Capital In)"), description and focus areas. Each /companies/<slug>/ page adds
the website, founders, co-investors and university. Stage is Pillar's own
"Stage at Investment" label normalized to a round where it names one.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, round_label, label_after, year_of, is_social

SOURCE_URL = "https://www.pillar.vc/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "pillarvc_companies.json")
PRIMARY = "Pillar VC"
SECTOR_TAG_MAP = {
    "agtech": ["Climate / Sustainability"], "climate": ["Climate / Sustainability"], "biotech": ["BioTech"],
    "fintech": ["FinTech / Insurance"], "healthcare": ["Health"], "health": ["Health"], "crypto": ["Web3 / Crypto"],
    "cybersecurity": ["Cybersecurity"], "robotics": ["Deeptech / Robotics / AR/VR"], "consumer": ["Consumer"],
    "defense": ["Deeptech / Robotics / AR/VR"], "future of work": ["Future of Work"], "developer tools": ["Dev Tools / Cloud"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".portfolio-item"):
        t = it.select_one(".portfolio-title a[href]")
        name = clean(t.get_text(" ")) if t else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        inv = it.select_one(".investment-date")
        stage_a = inv.select_one("a") if inv else None
        d = it.select_one(".description")
        rows.append({"name": name, "profile": t["href"].strip(),
                     "year": year_of(inv.get_text(" ") if inv else None),
                     "stage_raw": clean(stage_a.get_text(" ")) if stage_a else None,
                     "desc": clean(d.get_text(" ")) if d else None,
                     "focus": [clean(a.get_text()) for a in it.select(".focus-area a") if clean(a.get_text())]})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        for t in d(["script", "style", "svg", "nav", "footer", "header"]):
            t.decompose()
        main_el = d.select_one("main") or d
        strings = list(main_el.stripped_strings)
        site = None
        for a in main_el.select("a[href]"):
            h = a["href"].strip()
            txt = clean(a.get_text()) or ""
            if h.startswith("http") and "pillar.vc" not in h and not is_social(h):
                site = h
                break
            if not h.startswith("http") and re.fullmatch(r"[\w.-]+\.[a-z]{2,}", txt):
                site = "https://" + txt
                break
        if not site:
            dom = next((s for s in strings[:6] if re.fullmatch(r"[\w-]+(\.[\w-]+)*\.[a-z]{2,}", s or "")), None)
            site = "https://" + dom if dom else None
        coinv = label_after(strings, "Co-investors")
        univ = label_after(strings, "University")
        out.append({
            "company_name": r["name"],
            "description": r["desc"],
            "company_url": site,
            "company_profile_url": r["profile"],
            "status": None,
            "stage": round_label(r["stage_raw"]),
            "investment_stage_raw": r["stage_raw"],
            "first_invested": r["year"],
            "co_investors": [clean(x) for x in (coinv or "").split(",") if clean(x)],
            "university": univ,
            "sectors": r["focus"],
            "everywhere_tags": tags_for(r["name"], r["desc"], r["focus"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "stage", "first_invested", "co_investors", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
