#!/usr/bin/env python3
"""Kalaari Capital portfolio scraper -> kalaari_companies.json
Source: https://kalaari.com/portfolio — Webflow. The grid (one page, no
pagination) gives name, one-line blurb, "Series A, 2016"-style stage+year and
sector; each /portfolio/<slug> detail page adds website, founding year,
Status (Active/Exited), sector chips, headline, long description and
leadership. Exited companies sometimes link "Website" to an acquisition press
release — such deep links are kept as website_link, not company_url.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, round_label

BASE = "https://kalaari.com"
SOURCE_URL = BASE + "/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kalaari_companies.json")
PRIMARY = "Kalaari Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "health": ["Health"],
    "edtech": ["Consumer"], "consumer": ["Consumer"], "consumer tech": ["Consumer"],
    "d2c": ["CPG", "Consumer"], "e-commerce": ["Consumer"], "ecommerce": ["Consumer"],
    "deeptech": ["Deeptech / Robotics / AR/VR"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "spacetech": ["Deeptech / Robotics / AR/VR"], "gaming": ["Gaming / Media / Entertainment"],
    "media": ["Gaming / Media / Entertainment"], "logistics": ["Logistics / Supply Chain"],
    "mobility": ["Transportation / Mobility"], "agritech": ["Climate / Sustainability"],
    "climate": ["Climate / Sustainability"], "cleantech": ["Climate / Sustainability"],
    "web3": ["Web3 / Crypto"], "proptech": ["PropTech"], "hrtech": ["Future of Work"],
    "consumertech": ["Consumer"], "consumer brand": ["CPG", "Consumer"], "beauty & personal care": ["CPG"],
    "healthtech": ["Health"], "deeptech": ["Deeptech / Robotics / AR/VR"], "climatetech": ["Climate / Sustainability"],
    "media & entertainment": ["Gaming / Media / Entertainment"], "creator economy": ["Gaming / Media / Entertainment"],
    "ev": ["Transportation / Mobility", "Climate / Sustainability"], "devtools": ["Dev Tools / Cloud"],
    "cloudops/sre": ["Dev Tools / Cloud"], "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"],
    "legal tech": ["RegTech/Gov/Legal"], "risk & compliance": ["RegTech/Gov/Legal"], "hr tech": ["Future of Work"],
    "construction tech": ["PropTech"], "robotics": ["Deeptech / Robotics / AR/VR"], "ai in finance": ["FinTech / Insurance"],
    "marketingtech": ["Gaming / Media / Entertainment"], "consumer electronics": ["Consumer"], "modern retail": ["Consumer"],
    "saas": ["Dev Tools / Cloud"], "ai/saas": ["Dev Tools / Cloud"], "b2b saas": ["Dev Tools / Cloud"],
}


def label_value(soup, label):
    for el in soup.select(".text-block-140"):
        if clean(el.get_text()) == label:
            box = el.parent
            vals = [clean(v.get_text()) for v in box.select(".text-block-141, .text-block-163")
                    if clean(v.get_text()) and "w-dyn-bind-empty" not in (v.get("class") or [])]
            return max(vals, key=len) if vals else None
    return None


def is_homepage(url):
    p = urlparse(url or "")
    return bool(p.netloc) and p.path.strip("/").count("/") == 0 and len(p.path.strip("/")) <= 20


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".portfolio-grid-item"):
        a = it.select_one("a[href^='/portfolio/']")
        nm = it.select_one(".portfolio-name")
        name = clean(nm.get_text()) if nm else (clean(a.get("aria-label")) if a else None)
        if not name or name.lower() in seen or not a:
            continue
        seen.add(name.lower())
        blurb = it.select_one(".text-block-111")
        sy = it.select_one(".hidden-invest-yeaar") or it.select_one(".text-block-114")
        sec = it.select_one(".hidden-sector")
        rows.append({"name": name, "profile": urljoin(BASE, a["href"]),
                     "blurb": clean(blurb.get_text()) if blurb else None,
                     "stage_year": clean(sy.get_text()) if sy else None,
                     "sector": clean(sec.get_text()) if sec else None})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        link = d.select_one("a.link-block-55[href]")
        link = clean(link["href"]) if link else None
        stage_year = label_value(d, "Investing Stage & Year") or r["stage_year"]
        year = re.search(r"\b(19|20)\d{2}\b", stage_year or "")
        founded = label_value(d, "Founding Year")
        site_status = label_value(d, "Status")
        chips = []
        for c in d.select(".desktop-chip .text-block-148"):
            t = clean(c.get_text())
            if t and t not in chips:
                chips.append(t)
        sectors = chips or ([s.strip() for s in r["sector"].split(",")] if r["sector"] else [])
        headline = d.select_one("h2.text-block-143")
        longd = d.select_one(".text-block-146")
        desc = clean(longd.get_text(" ")) if longd else None
        desc = desc or r["blurb"]
        leaders = []
        for blk in d.select(".div-block-236 .w-dyn-item"):
            ts = [clean(t) for t in blk.stripped_strings if clean(t) and clean(t).lower() != "linkedin"]
            if ts:
                leaders.append({"name": ts[0], "title": ts[1] if len(ts) > 1 else None})
        st = (site_status or "").lower()
        status = "acquired" if st in ("exited", "acquired") else ("active" if st == "active" else None)
        out.append({
            "company_name": r["name"],
            "description": desc,
            "tagline": r["blurb"],
            "headline": clean(headline.get_text()) if headline else None,
            "company_url": link if link and is_homepage(link) else None,
            "website_link": link if link and not is_homepage(link) else None,
            "company_profile_url": r["profile"],
            "status": status,
            "site_status": site_status,
            "stage": round_label(stage_year),
            "investment_stage_raw": stage_year,
            "first_invested": int(year.group(0)) if year else None,
            "founded_year": int(founded) if founded and founded.isdigit() else None,
            "location": None,
            "sectors": sectors,
            "leadership": leaders,
            "everywhere_tags": tags_for(r["name"], desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "website_link", "status", "stage", "first_invested",
              "founded_year", "sectors", "leadership", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
