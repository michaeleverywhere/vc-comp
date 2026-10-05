#!/usr/bin/env python3
"""Congruent Ventures portfolio scraper -> congruent_companies.json
Source: https://www.congruentvc.com/portfolio — Webflow. The list page (61
links, no pagination) gives name + one-line blurb; exits are denormalized into
the blurb ("(Acquired by BP) ..."). Each /portfolio/<slug> detail page adds the
Congruent sector (e.g. "Mobility + Urbanization"), long description, company
team, Congruent partner(s) and website. No stage, location or invest year.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for

BASE = "https://www.congruentvc.com"
SOURCE_URL = BASE + "/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "congruent_companies.json")
PRIMARY = "Congruent Ventures"
SECTOR_TAG_MAP = {
    "mobility + urbanization": ["Transportation / Mobility", "Climate / Sustainability"],
    "energy transition": ["Climate / Sustainability"],
    "sustainable production + consumption": ["Climate / Sustainability"],
    "energy + power": ["Climate / Sustainability"],
    "energy": ["Climate / Sustainability"],
    "food + agriculture": ["Climate / Sustainability"],
    "industry + materials": ["Climate / Sustainability"],
    "buildings + construction": ["PropTech", "Climate / Sustainability"],
    "carbon + climate": ["Climate / Sustainability"],
    "water": ["Climate / Sustainability"],
}
ACQ_RE = re.compile(r"\((?:Acquired|Merged)[^)]*\)|\bacquired by\b", re.I)
IPO_RE = re.compile(r"\((?:NYSE|NASDAQ|IPO|TSX|LSE)[^)]*\)", re.I)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for a in soup.select("a.portfolio-link-block[href]"):
        nm = a.select_one(".company-name")
        name = clean(nm.get_text()) if nm else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        bl = a.select_one(".company-desc")
        rows.append({"name": name, "profile": urljoin(BASE, a["href"]),
                     "blurb": clean(bl.get_text(" ")) if bl else None})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        titles = [clean(x.get_text()) for x in d.select(".companypagemaininfo .companynametitle")]
        sector = titles[0] if len(titles) > 1 else None
        longd = d.select_one(".companylongdescription")
        desc = clean(longd.get_text(" ")) if longd else None
        team, partners, website = [], [], None
        for blk in d.select(".companydetailsright .contactdiv"):
            lab = clean(blk.select_one(".contactlabel").get_text()) if blk.select_one(".contactlabel") else ""
            if lab.upper() == "TEAM":
                team = [clean(p.get_text()) for p in blk.select("p") if clean(p.get_text())]
            elif lab.upper() == "CONGRUENT":
                partners = [clean(x.get_text()) for x in blk.select("a") if clean(x.get_text())]
            elif lab.lower() == "website":
                w = blk.select_one("a[href]")
                website = clean(w["href"]) if w else None
        blurb = r["blurb"] or ""
        acq = ACQ_RE.search(blurb) or ACQ_RE.search(desc or "")
        m = re.search(r"\((?:Acquired|Merged)(?: by| with)? ([^)]+)\)", blurb, re.I)
        status = "acquired" if acq else "active"
        sectors = [sector] if sector else []
        out.append({
            "company_name": r["name"],
            "description": desc or r["blurb"],
            "tagline": r["blurb"],
            "company_url": website,
            "company_profile_url": r["profile"],
            "status": status,
            "acquirer": clean(m.group(1)) if m else None,
            "ipo_note": clean(IPO_RE.search(blurb).group(0)) if IPO_RE.search(blurb) else None,
            "stage": None,
            "location": None,
            "sectors": sectors,
            "founders_team": team,
            "congruent_partners": partners,
            "everywhere_tags": tags_for(r["name"], (desc or "") + " " + blurb, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "acquirer", "sectors", "founders_team", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
