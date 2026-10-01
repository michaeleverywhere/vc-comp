#!/usr/bin/env python3
"""Slow Ventures portfolio scraper -> slowventures_companies.json
Source: https://slow.co/portfolio — plain-text company name roster.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

PORTFOLIO_URL = "https://slow.co/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "slowventures_companies.json")
PRIMARY = "Slow Ventures"
SKIP = {"slow ventures - portfolio", "portfolio", "slow ventures", "home", "team", "about"}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    # Prefer link/list structure if present; else line-split body text
    names = []
    for a in soup.select("a"):
        t = clean(a.get_text())
        if t and 1 < len(t) <= 80 and t.lower() not in SKIP:
            names.append(t)
    if len(names) < 20:
        text = soup.get_text("\n", strip=True)
        names = []
        for line in text.split("\n"):
            t = clean(line)
            if not t or t.lower() in SKIP:
                continue
            if len(t) > 80:
                continue
            names.append(t)
    out, seen = [], set()
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        # Parenthetical acquisition hints e.g. "Behance (Adobe)"
        status = "Active"
        if "(" in name and ")" in name:
            # keep name as shown; treat as possibly exited only if clear
            inner = name[name.find("(")+1:name.find(")")].lower()
            if any(x in inner for x in ("adobe", "acquired", "ipo", "google", "meta", "amazon", "microsoft")):
                status = "Exited"
        rec = {
            "company_name": name,
            "description": None,
            "company_url": None,
            "status": status,
            "stage": None,
            "everywhere_tags": classify(name, None)[:4],
            "primary_investor": PRIMARY,
            "source_url": PORTFOLIO_URL,
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
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged (name-only; site is name roster)")


if __name__ == "__main__":
    main()
