#!/usr/bin/env python3
"""Visionaries Club portfolio scraper -> visionaries_companies.json
Source: https://www.visionaries.vc/ — the portfolio accordion on the home
page (Alpine.js; every item is server-rendered, the "show all" toggle only
un-hides them). Each item has the company name, a claim line, a
description paragraph, a website link and Visionaries' investment thesis.
No stage, location, year or status labels are published; exits / ARR are
taken only where the description states them explicitly
("has been acquired by X in <Month YYYY>", "$N million in annual recurring
revenue").
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.visionaries.vc/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "visionaries_companies.json")
PRIMARY = "Visionaries Club"
ACQ_RX = re.compile(r"\b(?:has been|was) acquired by ([A-Z][\w&.'’\- ]+?)(?: in ((?:[A-Z][a-z]+ )?(?:19|20)\d{2}))?[,.]")
ARR_RX = re.compile(r"((?:more than |over )?(?:US)?[$€£]\s?\d[\d.,]*\s?(?:million|billion|m|bn))\s+(?:in |of )?annual recurring revenue", re.I)

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Langdock": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Lovable": [
        "Dev Tools / Cloud"
    ],
    "Pigment": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Miro": [
        "Future of Work"
    ],
    "Personio": [
        "Future of Work"
    ],
    "n8n": [
        "Dev Tools / Cloud",
        "Future of Work"
    ],
    "Solve Intelligence": [
        "RegTech/Gov/Legal"
    ],
    "Tacto": [
        "Logistics / Supply Chain"
    ],
    "Black Forest Labs": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "Tandem Health": [
        "Health"
    ],
    "Tendrils Compute": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "Xentral": [
        "Future of Work",
        "Logistics / Supply Chain"
    ],
    "The Token Company": [
        "Dev Tools / Cloud"
    ],
    "11x": [
        "Future of Work"
    ],
    "Accountable": [
        "FinTech / Insurance"
    ],
    "Adfin": [
        "FinTech / Insurance"
    ],
    "Ameba": [
        "Logistics / Supply Chain",
        "Data & Analytics"
    ],
    "Arculus": [
        "Deeptech / Robotics / AR/VR",
        "Logistics / Supply Chain"
    ],
    "automaited": [
        "Future of Work"
    ],
    "Autarc": [
        "Climate / Sustainability",
        "Future of Work"
    ],
    "Causaly": [
        "BioTech",
        "Data & Analytics"
    ],
    "Choco": [
        "Logistics / Supply Chain",
        "CPG"
    ],
    "CodeWords": [
        "Future of Work"
    ],
    "CourtCorrect": [
        "RegTech/Gov/Legal",
        "FinTech / Insurance"
    ],
    "Cycle": [
        "Logistics / Supply Chain",
        "Climate / Sustainability"
    ],
    "GetHarley": [
        "Health",
        "Consumer"
    ],
    "GetMomo": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "H Company": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Hakuna": [
        "FinTech / Insurance"
    ],
    "Introw": [
        "Future of Work"
    ],
    "Kabilio": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Ledgy": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Lindus Health": [
        "Health",
        "BioTech"
    ],
    "Localyze": [
        "Future of Work"
    ],
    "Omnia": [
        "Data & Analytics"
    ],
    "Orbio": [
        "Future of Work"
    ],
    "Pallery": [
        "Future of Work"
    ],
    "Pave Space": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Pivot": [
        "Logistics / Supply Chain",
        "FinTech / Insurance"
    ],
    "Qonversion": [
        "Dev Tools / Cloud"
    ],
    "Quantive": [
        "Future of Work"
    ],
    "Rows": [
        "Data & Analytics",
        "Future of Work"
    ],
    "Secjur": [
        "RegTech/Gov/Legal",
        "Cybersecurity"
    ],
    "Superlist": [
        "Future of Work"
    ],
    "TrueLayer": [
        "FinTech / Insurance"
    ],
    "Turian": [
        "Dev Tools / Cloud",
        "Future of Work"
    ],
    "Two": [
        "FinTech / Insurance"
    ],
    "Workflex": [
        "Future of Work",
        "RegTech/Gov/Legal"
    ],
    "Taktile": [
        "FinTech / Insurance"
    ],
    "Taxdoo": [
        "FinTech / Insurance",
        "RegTech/Gov/Legal"
    ],
    "Yokoy": [
        "FinTech / Insurance"
    ],
    "Apron": [
        "FinTech / Insurance"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select("div.portfolio__item"):
        t = it.select_one(".portfolio__item-title-text")
        name = clean(t.get_text(" ")) if t else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cl = it.select_one(".portfolio__item-claim")
        claim = clean(cl.get_text(" ")) if cl else None
        if claim:
            claim = clean(re.sub(r"^\s*-\s*|\s*[-–]\s*$", "", claim))
        d = it.select_one(".portfolio__item-testimonial-content")
        desc = clean(d.get_text(" ")) if d else None
        th = it.select_one(".portfolio__item-text")
        thesis = None
        if th:
            ps = [clean(p.get_text(" ")) for p in th.select("p")]
            ps = [p for p in ps if p and p.lower() != "our thesis"]
            thesis = " ".join(ps) or None
        a = it.select_one(".portfolio__item-ctas a[href^=http]")
        acq = ACQ_RX.search(" ".join(x for x in (desc, thesis) if x))
        arr = ARR_RX.search(desc or "")
        out.append({
            "company_name": name,
            "description": desc or claim,
            "tagline": claim,
            "investment_thesis": thesis,
            "company_url": clean_url(a["href"]) if a else None,
            "status": "acquired" if acq else None,
            "acquirer": clean(acq.group(1)) if acq else None,
            "exit_year": year_of(acq.group(2)) if acq and acq.group(2) else None,
            "arr": clean(arr.group(1)) if arr else None,
            "everywhere_tags": tags_for(name, " ".join(x for x in (claim, desc) if x)),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "arr", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
