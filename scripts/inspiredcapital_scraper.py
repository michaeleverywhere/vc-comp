#!/usr/bin/env python3
"""Inspired Capital portfolio scraper -> inspiredcapital_companies.json
Source: https://www.inspiredcapital.com/portfolio — Webflow + JSON-LD Organizations.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.inspiredcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "inspiredcapital_companies.json")
PRIMARY = "Inspired Capital"

SKIP_NAMES = {
    "inspired capital", "founders", "what people will crave in an ai-led economy",
    "why we invested: buywander",
}


def json_ld_orgs(soup):
    orgs = {}
    for s in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue

        def walk(o):
            if isinstance(o, dict):
                if o.get("@type") == "Organization" and o.get("name"):
                    n = clean(o["name"])
                    if n and n.lower() != "inspired capital":
                        founders = []
                        for f in o.get("founder") or []:
                            if isinstance(f, dict) and f.get("name"):
                                founders.append(clean(f["name"]))
                        orgs[n.lower()] = {
                            "name": n,
                            "description": clean(o.get("description")),
                            "founders": founders or None,
                        }
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(data)
    return orgs


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    ld = json_ld_orgs(soup)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    # Walk dyn items for company cards
    for it in soup.select(".w-dyn-item"):
        imgs = [i for i in it.select("img[alt]") if i.get("alt") and len(i.get("alt")) > 1]
        h3s = it.select("h3")
        name = None
        if imgs:
            alt = clean(imgs[0].get("alt"))
            if alt and alt.lower() not in SKIP_NAMES and len(alt) < 50:
                name = alt
        if not name and h3s:
            t = clean(h3s[0].get_text())
            if t and t.lower() not in SKIP_NAMES and t.lower() != "founders" and len(t) < 40:
                name = t
        if not name:
            continue
        if name.lower() in seen or name.lower() in SKIP_NAMES:
            continue
        # sectors from short tokens near name
        texts = [clean(t) for t in it.stripped_strings if clean(t)]
        sectors = []
        known = {
            "AI", "Fintech", "Healthcare", "Consumer", "B2B", "Industrial",
            "Future of Work", "Growth", "Early", "New Frontier", "Climate",
            "Crypto", "Enterprise", "Marketplace",
        }
        for t in texts:
            if t in known and t not in ("Growth", "Early") and t not in sectors:
                sectors.append(t)
        stage = None
        if "Growth" in texts:
            stage = "Growth"
        elif "Early" in texts:
            stage = "Seed"  # site says Early — map conservatively? Better leave as Early label only if it's a funding round
            stage = None  # "Early" is not a standard funding-round label in our schema
        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["inspiredcapital", "webflow", "linkedin.com", "twitter.com", "x.com", "website-files"]):
                continue
            website = clean(href)
            break
        # description from JSON-LD or founder-card tagline
        desc = None
        founders = None
        if name.lower() in ld:
            desc = ld[name.lower()].get("description")
            founders = ld[name.lower()].get("founders")
        if not desc:
            for p in it.select("p"):
                pt = clean(p.get_text())
                if pt and len(pt) > 20:
                    desc = pt
                    break
        if not desc:
            # founder cards: "build ..." taglines after Founders
            for i, t in enumerate(texts):
                if t and t.lower().startswith(("build ", "make ", "connect ", "power ", "give ", "modernize", "safeguard", "simplify", "reimagine", "accelerate", "empower")):
                    desc = t
                    break

        seen.add(name.lower())
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "founders": founders,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    # Add any JSON-LD orgs missed in HTML walk
    for key, info in ld.items():
        if key in seen:
            continue
        name = info["name"]
        seen.add(key)
        rec = {
            "company_name": name,
            "description": info.get("description"),
            "company_url": None,
            "status": "Active",
            "stage": None,
            "founders": info.get("founders"),
            "sectors": None,
            "everywhere_tags": classify(name, info.get("description"))[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
