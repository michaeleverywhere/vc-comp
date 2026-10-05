#!/usr/bin/env python3
"""Prelude Ventures portfolio scraper -> prelude_companies.json
Source: https://www.preludeventures.com/portfolio — Craft CMS, server-rendered
cards (li[data-card]): name, profile link, data-filter = "current|exited, <sector
slugs>", an "ACQ <acquirer>" badge on acquired exits, and a one-line blurb. Each
/portfolio/<slug> page adds the sector label, headline, Founded year,
Investment Date (= first invested), website, leadership and Prelude investors.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for

SOURCE_URL = "https://www.preludeventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "prelude_companies.json")
PRIMARY = "Prelude Ventures"
SECTOR_NAMES = {
    "energy": "Energy", "manufacturing-industrials": "Manufacturing & Industrials",
    "carbon-management": "Carbon Management", "food-agriculture": "Food & Agriculture",
    "mobility": "Mobility", "built-environment": "Built Environment", "compute": "Compute",
}
SECTOR_TAG_MAP = {
    "energy": ["Climate / Sustainability"],
    "manufacturing & industrials": ["Climate / Sustainability"],
    "carbon management": ["Climate / Sustainability"],
    "food & agriculture": ["Climate / Sustainability"],
    "mobility": ["Transportation / Mobility", "Climate / Sustainability"],
    "built environment": ["PropTech", "Climate / Sustainability"],
    "compute": ["Deeptech / Robotics / AR/VR"],
}
NON_SITE = ("linkedin.com", "twitter.com", "preludeventures.com", "mailto:")


def aside_fields(d):
    out = {}
    asides = [a for a in d.select("aside") if a.select_one("h3")]
    if not asides:
        return out
    for h3 in asides[0].select("h3"):
        lab = clean(h3.get_text())
        nxt = h3.find_next_sibling()
        if not nxt:
            continue
        if nxt.name == "p":
            out[lab] = clean(nxt.get_text())
        elif nxt.name == "ul":
            items = []
            for li in nxt.select("li"):
                for s in li.select(".sr-only"):
                    s.decompose()
                items.append((clean(li.get_text(" ")), [a.get("href") for a in li.select("a[href]")]))
            out[lab] = items
    return out


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for li in soup.select("li[data-card]"):
        a = li.select_one("h2 a[href]")
        name = clean(a.get_text()) if a else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        flt = [x.strip() for x in (li.get("data-filter") or "").split(",") if x.strip()]
        badge = li.select_one("h2 + p")
        btxt = clean(badge.get_text(" ")) if badge else None
        bl = li.select_one("p.text-base-sm")
        blurb = clean(bl.get_text(" ")) if bl else None
        acq = None
        m = re.search(r"\(\s*ACQ\s+([^)]+?)\s*\)", blurb or "") or re.search(r"ACQ\s+(.+)", btxt or "")
        if m:
            acq = clean(m.group(1))
        if blurb:
            blurb = clean(re.sub(r"^(?:ACQ\s*)?\(\s*ACQ[^)]*\)\s*", "", blurb))
        href = a["href"]
        internal = "preludeventures.com/portfolio/" in href
        tick = re.match(r"^\(\s*((?:NYSE|NASDAQ|Nasdaq|TSX|LSE|ASX)\s*:\s*[A-Z.]+)\s*\)\s*", blurb or "")
        ticker = clean(tick.group(1)) if tick else None
        if tick:
            blurb = clean(blurb[tick.end():])
        rows.append({"name": name, "profile": href if internal else None, "ticker": ticker,
                     "external": None if internal else href,
                     "filters": flt, "acq": acq, "blurb": blurb})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows if r["profile"]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser") if r["profile"] else None
        f = aside_fields(d) if d else {}
        h2 = None
        if d:
            for cand in d.select("h2"):
                t = clean(cand.get_text(" "))
                if t and t != r["name"] and len(t) > 25:
                    h2 = cand
                    break
        headline = clean(h2.get_text(" ")) if h2 else None
        website = None
        for txt, hrefs in f.get("Contact", []) if isinstance(f.get("Contact"), list) else []:
            for h in hrefs:
                if h and not any(x in h for x in NON_SITE):
                    website = website or h
        leaders = [t for t, _ in f.get("Leadership", [])] if isinstance(f.get("Leadership"), list) else []
        investors = [t for t, _ in f.get("Prelude Investors", [])] if isinstance(f.get("Prelude Investors"), list) else []
        sectors = [SECTOR_NAMES.get(x, x) for x in r["filters"] if x not in ("current", "exited")]
        exited = "exited" in r["filters"]
        status = "acquired" if r["acq"] else ("active" if ("current" in r["filters"] or r["ticker"]) else None)
        inv = f.get("Investment Date") if isinstance(f.get("Investment Date"), str) else None
        fy = f.get("Founded") if isinstance(f.get("Founded"), str) else None
        desc = headline if headline and len(headline or "") > len(r["blurb"] or "") else (r["blurb"] or headline)
        out.append({
            "company_name": r["name"],
            "description": desc,
            "tagline": r["blurb"],
            "company_url": website,
            "company_profile_url": r["profile"],
            "exit_link": r["external"],
            "status": status,
            "site_status": "exited" if exited else ("current" if "current" in r["filters"] else None),
            "acquirer": r["acq"],
            "ticker": r["ticker"],
            "stage": None,
            "first_invested": int(inv) if inv and inv.isdigit() else inv,
            "founded_year": int(fy) if fy and fy.isdigit() else fy,
            "location": None,
            "sectors": sectors,
            "leadership": leaders,
            "prelude_investors": investors,
            "everywhere_tags": tags_for(r["name"], " ".join(x for x in (r["blurb"], headline) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "acquirer", "first_invested", "founded_year",
              "sectors", "leadership", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
