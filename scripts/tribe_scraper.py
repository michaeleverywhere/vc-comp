#!/usr/bin/env python3
"""Tribe Capital portfolio scraper -> tribe_companies.json
Source: https://tribecap.co/portfolio — Webflow dyn items "// NAME LOC …".
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://tribecap.co/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "tribe_companies.json")
PRIMARY = "Tribe Capital"


def titlecase_name(name: str) -> str:
    if not name:
        return name
    if name.isupper() and len(name) > 3:
        # Keep short tickers/acronyms; else title-case
        parts = name.split()
        return " ".join(p if len(p) <= 3 and p.isalpha() else p.title() for p in parts)
    return name


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".w-dyn-item"):
        raw = " ".join(t.strip() for t in it.stripped_strings if t.strip())
        m = re.match(
            r"//\s*([A-Z0-9][A-Z0-9\s&\.\-/'+]+?)\s+(USA|IND|UK|EU|ISR|SGP|CAN|DEU|FRA|CHN|AUS|KOR|JPN|BRA|MEX|[A-Z]{2,3})\b(.*)$",
            raw,
        )
        if not m:
            continue
        name = titlecase_name(clean(m.group(1)))
        loc = m.group(2)
        rest = (m.group(3) or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        status = "Active"
        ticker = None
        tm = re.match(r"(NSE|NASDAQ|NYSE|IPO|LSE|HKEX):\s*(\S+)\s*(.*)$", rest)
        if tm:
            ticker = f"{tm.group(1)}: {tm.group(2)}"
            rest = tm.group(3).strip()
            status = "Public"
        desc = clean(rest) if rest else None
        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if "tribecap" in href or "webflow" in href:
                continue
            website = clean(href)
            break
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "ticker_symbol": ticker,
            "stage": None,
            "location": loc,
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
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
