#!/usr/bin/env python3
"""Harlem Capital portfolio scraper -> harlem_companies.json
Source: https://harlem.capital/portfolio/ — the page's React app loads its company
grid from the site's own public WPGraphQL endpoint (https://harlem.capital/graphql,
the same unauthenticated query main.js sends: themeSettings.global.portfolioColumns).
Each profile gives company name, description, founder(s), website and Harlem Capital
category labels; the "Exited" label marks exits ("Spotlight" is a display flag)."""
import html as _html, os, re, sys
from datetime import datetime, timezone

import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://harlem.capital/portfolio/"
GRAPHQL = "https://harlem.capital/graphql"
PRIMARY = "Harlem Capital"
QUERY = ("{ themeSettings { global { portfolioColumns { items { ... on Profile { title slug content "
         "portfolio { founder website { url } } portfolioCategories { nodes { name } } } } } } } }")
SECTOR_MAP = {"consumer": ["Consumer"], "deep tech": ["Deeptech / Robotics / AR/VR"], "ecommerce": ["Consumer"],
              "energy": ["Climate / Sustainability"], "fintech": ["FinTech / Insurance"], "healthcare": ["Health"],
              "web3/crypto": ["Web3 / Crypto"], "ai": [], "enterprise": [], "software": []}


def text(h):
    return clean(re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h or "")))) or None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.post(GRAPHQL, json={"query": QUERY}, headers={**HEADERS, "Content-Type": "application/json"}, timeout=60)
    r.raise_for_status()
    cols = r.json()["data"]["themeSettings"]["global"]["portfolioColumns"] or []
    out, seen = [], set()
    for col in cols:
        for it in col.get("items") or []:
            if not it or not it.get("title"):
                continue
            name = clean(_html.unescape(it["title"]))
            if not name or it.get("slug") in seen:
                continue
            seen.add(it.get("slug"))
            p = it.get("portfolio") or {}
            fl = clean(p.get("founder") or "")
            founders = [x.strip() for x in re.split(r",|&|\band\b", fl or "") if x.strip()]
            web = ((p.get("website") or {}).get("url") or "").strip() or None
            cats = [n["name"] for n in ((it.get("portfolioCategories") or {}).get("nodes") or []) if n.get("name")]
            secs = [c for c in cats if c.lower() not in ("exited", "spotlight")]
            out.append(rec(name, text(it.get("content")), web if web and not is_social(web) else None, PRIMARY,
                           SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP, founders=founders,
                           status="exited" if any(c.lower() == "exited" for c in cats) else "active",
                           profile_url=f"https://harlem.capital/portfolio/{it['slug']}/" if it.get("slug") else None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Harlem Capital companies")
    finish(out, "harlem", ("description", "company_url", "founders", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
