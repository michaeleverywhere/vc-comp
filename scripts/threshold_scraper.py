#!/usr/bin/env python3
"""Threshold Ventures portfolio scraper -> threshold_companies.json
Source: https://www.threshold.vc/companies — Webflow company_collection-item cards.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.threshold.vc/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "threshold_companies.json")
PRIMARY = "Threshold Ventures"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".company_collection-item"):
        texts = [t.strip() for t in it.stripped_strings if t.strip()]
        if not texts:
            continue
        name = clean(texts[0])
        if not name or name.lower() in seen:
            continue
        # skip founder-only cards accidentally matched
        if name.lower() in ("active", "exited", "founder", "founders"):
            continue
        seen.add(name.lower())
        desc = None
        for t in texts[1:]:
            if len(t) >= 40 and not t.startswith("KLUv") and t.lower() not in ("active", "exited", "company website"):
                if not t.upper().startswith("YEAR INVESTED") and t.lower() not in ("founder", "founders"):
                    desc = clean(t)
                    break
        status = "Active"
        blob = " ".join(texts[:12]).lower()
        if re.search(r"\b(exited|acquired|ipo)\b", blob):
            # look for explicit status token
            for t in texts:
                tl = t.lower()
                if tl in ("exited", "acquired"):
                    status = "Acquired"
                    break
                if tl == "ipo" or tl == "public":
                    status = "Public"
                    break
        year = None
        for i, t in enumerate(texts):
            if "year invested" in t.lower() and i + 1 < len(texts):
                m = re.search(r"(19|20)\d{2}", texts[i + 1])
                if m:
                    year = int(m.group(0))
                break
            m = re.search(r"year invested[:\s]*((?:19|20)\d{2})", t, re.I)
            if m:
                year = int(m.group(1))
                break
        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ("threshold.vc", "medium.com", "twitter", "linkedin", "x.com")):
                continue
            website = clean(href)
            break
        founders = []
        for i, t in enumerate(texts):
            if t.lower() in ("founder", "founders") and i + 1 < len(texts):
                raw = texts[i + 1]
                if "year invested" not in raw.lower() and len(raw) < 120:
                    founders = [clean(x) for x in re.split(r"\s+and\s+|,\s*", raw) if clean(x)]
                break
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "investment_year": year,
            "founders": founders or None,
            "everywhere_tags": classify(name, desc)[:4],
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
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
