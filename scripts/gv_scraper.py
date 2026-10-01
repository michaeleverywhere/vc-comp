#!/usr/bin/env python3
"""GV (Google Ventures) portfolio scraper -> gv_companies.json
Source: https://www.gv.com/portfolio — schema.org ItemList in ld+json.
Trailing " *" on a name is treated as exited when present on the firm page.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

PORTFOLIO_URL = "https://www.gv.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "gv_companies.json")
PRIMARY = "GV"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    items = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        if isinstance(data, dict) and "ItemList" in (data.get("@type") or []):
            items = data.get("itemListElement") or []
            break
        if isinstance(data, dict) and data.get("@type") == "ItemList":
            items = data.get("itemListElement") or []
            break
    out, seen = [], set()
    for it in items:
        node = it.get("item") if isinstance(it, dict) else None
        raw = None
        if isinstance(node, dict):
            raw = node.get("name")
        elif isinstance(it, dict):
            raw = it.get("name")
        raw = clean(raw)
        if not raw:
            continue
        exited = raw.endswith("*")
        name = clean(raw.rstrip("*").strip())
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        rec = {
            "company_name": name,
            "description": None,
            "company_url": None,
            "status": "Exited" if exited else "Active",
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
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged (name-only classify; GV list has no blurbs)")


if __name__ == "__main__":
    main()
