#!/usr/bin/env python3
"""Redalpine portfolio scraper -> redalpine_companies.json
Source: https://www.redalpine.com/portfolio — Wix (server-rendered repeater).
The portfolio table gives, per company: name, one-line description, status
(active / exited) and Redalpine's sector. Each /portfolio/<slug> page adds the
company website and a long description. Redalpine publishes all names and
copy in lower case; text is kept exactly as published.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, is_social

SOURCE_URL = "https://www.redalpine.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "redalpine_companies.json")
PRIMARY = "Redalpine"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "frontier science & biotech": ["BioTech"],
    "digital health & medtech": ["Health"], "consumer platforms": ["Consumer"],
    "ai infrastructure & security": ["Dev Tools / Cloud", "Cybersecurity"], "foodtech": ["CPG", "Climate / Sustainability"],
    "energy & climate tech": ["Climate / Sustainability"], "robotics & intelligent systems": ["Deeptech / Robotics / AR/VR"],
    "space & defence": ["Deeptech / Robotics / AR/VR"], "marketplaces": ["Consumer"],
}
SKIP = ("join the community", "©", "privacy policy", "related stories")


def texts(el):
    out = []
    for t in el.select("[data-testid=richTextElement]"):
        s = clean(t.get_text(" "))
        if s and s != "\u200b":
            out.append(s)
    return out


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".wixui-repeater__item"):
        t = texts(it)
        if len(t) != 5:
            continue
        a = it.select_one("a[href*='/portfolio/']")
        if t[0].lower() in seen:
            continue
        seen.add(t[0].lower())
        rows.append({"name": t[0], "blurb": t[2], "site_status": t[3], "sector": t[4],
                     "profile": a["href"].strip() if a else None})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows if r["profile"]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        site = None
        for a in d.select("a[href^='http']"):
            h = a["href"].strip()
            if "redalpine" in h or is_social(h) or "wix" in h:
                continue
            site = h
            break
        longs = [x for x in texts(d) if len(x) > 80 and not any(k in x.lower() for k in SKIP)]
        desc = longs[0] if longs else r["blurb"]
        st = (r["site_status"] or "").lower()
        sectors = [r["sector"]] if r["sector"] else []
        out.append({
            "company_name": r["name"],
            "description": desc,
            "tagline": r["blurb"],
            "company_url": site,
            "company_profile_url": r["profile"],
            "status": "active" if st == "active" else None,
            "site_status": r["site_status"],
            "sectors": sectors,
            "everywhere_tags": tags_for(r["name"], " ".join([r["blurb"] or "", desc or ""]), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
