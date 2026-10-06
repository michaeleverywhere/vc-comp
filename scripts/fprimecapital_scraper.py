#!/usr/bin/env python3
"""F-Prime Capital portfolio scraper -> fprimecapital_companies.json
Source: https://fprimecapital.com/portfolio/ — WordPress. The grid lists every
company (name in the link title, one-line description); each /company/<slug>/
detail page adds the long description, website, investment team, sectors,
location, Initial Investment year, and a status-{private,public,acquired}
class on the <article>. Status "private" is the site's active label.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for

SOURCE_URL = "https://fprimecapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fprimecapital_companies.json")
PRIMARY = "F-Prime Capital"
SECTOR_TAG_MAP = {
    "healthtech + services": ["Health"], "life sciences": ["BioTech"], "therapeutics": ["BioTech"],
    "medtech": ["Health"], "fintech": ["FinTech / Insurance"], "crypto": ["Web3 / Crypto"],
    "frontier": ["Deeptech / Robotics / AR/VR"],
}


def section(art, cls):
    el = art.select_one("." + cls)
    if not el:
        return []
    h = el.find("h3")
    if h:
        h.extract()
    return [clean(t) for t in el.stripped_strings if clean(t)]


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".portfolio_item"):
        a = it.select_one("a[href*='/company/']")
        if not a:
            continue
        url = a["href"].split("#")[0]
        if url in seen:
            continue
        seen.add(url)
        d = it.select_one(".portfolio_item_desc")
        rows.append({"name": clean(a.get("title")), "profile": url,
                     "blurb": clean(d.get_text(" ")) if d else None})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows], workers=4)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        art = d.select_one("article.type-company") or d
        h1 = art.select_one(".company_name h1")
        name = clean(h1.get_text()) if h1 else r["name"]
        if not name:
            continue
        classes = art.get("class") or [] if hasattr(art, "get") else []
        site_status = next((c.split("-", 1)[1] for c in classes if c.startswith("status-") and c != "status-publish"), None)
        status = {"acquired": "acquired", "private": "active"}.get(site_status)
        txt = art.select_one(".company_text")
        longd = clean(txt.get_text(" ")) if txt else None
        logo = art.select_one(".company_logo_col a[href]")
        loc = section(art, "company_location")
        init = section(art, "company_init")
        yr = re.search(r"\b(19|20)\d{2}\b", " ".join(init))
        sectors = section(art, "sector")
        team = [clean(x.get_text()) for x in art.select(".company_team a") if clean(x.get_text())]
        desc = longd or r["blurb"]
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": r["blurb"],
            "company_url": logo["href"].strip() if logo else None,
            "company_profile_url": r["profile"],
            "status": status,
            "site_status": site_status,
            "first_invested": int(yr.group(0)) if yr else None,
            "location": ", ".join(loc) if loc else None,
            "sectors": sectors,
            "investment_team": team,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "first_invested", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
