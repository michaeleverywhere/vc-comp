#!/usr/bin/env python3
"""Openspace Ventures portfolio scraper -> openspace_companies.json
Source: https://www.openspacecapital.com/companies (openspace.vc redirects here)
— Webflow, one server-rendered list (.portfolio-item, no pagination): logo alt
= company name, one-line description, stock ticker (listed) or "Acquired by X" (exits) and a
/portfolio/<slug> link. Each detail page adds country, industry, founded,
founders, investment year and website. Webflow's unfilled-field placeholder
("This is some text inside of a div block.") is treated as empty.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for

BASE = "https://www.openspacecapital.com"
SOURCE_URL = BASE + "/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "openspace_companies.json")
PRIMARY = "Openspace Ventures"
PLACEHOLDER = "this is some text inside of a div block"
SECTOR_TAG_MAP = {
    "energy": ["Climate / Sustainability"], "climate": ["Climate / Sustainability"],
    "fintech": ["FinTech / Insurance"], "financial services": ["FinTech / Insurance"],
    "insurtech": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"],
    "healthcare": ["Health"], "healthtech": ["Health"], "health": ["Health"],
    "education": ["Consumer"], "edtech": ["Consumer"], "e-commerce": ["Consumer"],
    "consumer": ["Consumer"], "consumer internet": ["Consumer"], "logistics": ["Logistics / Supply Chain"],
    "supply chain": ["Logistics / Supply Chain"], "mobility": ["Transportation / Mobility"],
    "transportation": ["Transportation / Mobility"], "property": ["PropTech"], "proptech": ["PropTech"],
    "real estate": ["PropTech"], "media": ["Gaming / Media / Entertainment"], "gaming": ["Gaming / Media / Entertainment"],
    "enterprise software": ["Dev Tools / Cloud"], "software": ["Dev Tools / Cloud"], "saas": ["Dev Tools / Cloud"],
    "b2b software": ["Dev Tools / Cloud"], "cybersecurity": ["Cybersecurity"], "agriculture": ["Climate / Sustainability"],
    "food": ["CPG"], "f&b": ["CPG"], "hr": ["Future of Work"], "web3": ["Web3 / Crypto"],
}


def val(el):
    t = clean(el.get_text(" ")) if el else None
    return None if not t or t.lower().rstrip(".") == PLACEHOLDER else t

# Hand-assigned tags (reviewer judgment from the firm-site description; no LLM)
# for companies the keyword classifier leaves untagged. Applied only when empty.
TAG_OVERRIDES = {
    "Neuroglee Health": [
        "Health"
    ],
    "Fano": [
        "Future of Work"
    ],
    "Sirsak": [
        "Climate / Sustainability"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".portfolio-list-wrapper .portfolio-item"):
        a = it.select_one("a.portfolio-link-wrapper[href]")
        img = next((i for i in it.select("img[alt]") if clean(i.get("alt"))), None)
        name = clean(img.get("alt")) if img else None
        if not a or not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        rows.append({"name": name, "profile": urljoin(BASE, a["href"]),
                     "blurb": val(it.select_one(".portfolio-hover-wrapper .white")),
                     "ticker": val(it.select_one(".stock-market"))})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        rich = d.select_one(".container-640px.w-richtext")
        desc = val(rich)
        info = {}
        for row in d.select(".portfolio-info2-wrapper .flexhorizontal"):
            kids = row.find_all("div", recursive=False)
            if len(kids) >= 2:
                info[clean(kids[0].get_text()).rstrip(":")] = val(kids[1])
        stats = {}
        for blk in d.select(".investment-year"):
            h3 = blk.select_one("h3")
            if h3:
                stats[clean(h3.get_text())] = val(blk.select_one(".portfolio-stat"))
        website = None
        for a in d.select(".new-portfolio-info-content a[href^='http'], .portfolio-info2-wrapper a[href^='http']"):
            if "openspace" not in a["href"]:
                website = clean(a["href"])
                break
        industry = info.get("Industry")
        sectors = [s.strip() for s in re.split(r",|/", industry or "") if s.strip()]
        yr = stats.get("Investment Year")
        yr_m = re.search(r"\b(19|20)\d{2}\b", yr or "")
        founded = info.get("Founded")
        fy = re.search(r"\b(19|20)\d{2}\b", founded or "")
        founders = [clean(x) for x in re.split(r",|&| and ", info.get("Founders") or "") if clean(x)]
        ticker = r["ticker"]
        acq = re.match(r"(?i)acquired by\s+(.+)", ticker or "")
        acquirer = clean(acq.group(1)) if acq else None
        if acq:
            ticker = None
        out.append({
            "company_name": r["name"],
            "description": desc or r["blurb"],
            "tagline": r["blurb"],
            "company_url": website,
            "company_profile_url": r["profile"],
            "status": "acquired" if acquirer else "active",
            "acquirer": acquirer,
            "ticker": ticker,
            "stage": None,
            "first_invested": int(yr_m.group(0)) if yr_m else None,
            "founded_year": int(fy.group(0)) if fy else None,
            "location": stats.get("Country") or val(d.select_one(".text-block-16")),
            "sectors": sectors,
            "founders": founders,
            "everywhere_tags": tags_for(r["name"], " ".join(x for x in (r["blurb"], desc) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for rec in out:
        if not rec["everywhere_tags"] and rec["company_name"] in TAG_OVERRIDES:
            rec["everywhere_tags"] = TAG_OVERRIDES[rec["company_name"]]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "ticker", "first_invested", "founded_year", "location",
              "sectors", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
