#!/usr/bin/env python3
"""Third Prime portfolio scraper -> thirdprime_companies.json
Source: https://www.thirdprime.vc/portfolio — Webflow + Finsweet CMS filter,
one page. Each card: name, description (often naming the HQ city in
parentheses, e.g. "Alto Solutions (Nashville) is ..."), company website, a
status filter value (Active / Realized) and an exit tab ("Exit via M&A",
"Exit via IPO"). Exit via M&A -> acquired; Active -> active.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://www.thirdprime.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "thirdprime_companies.json")
PRIMARY = "Third Prime"
CITY = re.compile(r"^[^()]{1,60}?\(([A-Z][A-Za-z .,'-]{2,40})\)\s+(?:is|was|are|has|builds|provides|offers|enables|helps|develops|makes)\b")


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".portoflio-item"):
        h = it.select_one(".portfolio-headline")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = it.select_one(".portfolio-description")
        desc = clean(d.get_text(" ")) if d else None
        a = it.select_one("a.desktop_link_portfolio_wrapper[href], a.portfolio[href]")
        st = it.select_one("[fs-cmsfilter-field=status]")
        st = clean(st.get_text()) if st else None
        ex = it.select_one(".exit-tab:not(.w-condition-invisible)")
        ex = clean(ex.get_text(" ")) if ex else None
        if ex and "m&a" in ex.lower():
            status = "acquired"
        elif (st or "").lower() == "active" and not ex:
            status = "active"
        else:
            status = None
        m = CITY.match(desc or "")
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": a["href"].strip() if a and a["href"].startswith("http") else None,
            "status": status,
            "site_status": st or None,
            "exit": ex,
            "location": m.group(1) if m else None,
            "everywhere_tags": tags_for(name, desc, []),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "exit", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
