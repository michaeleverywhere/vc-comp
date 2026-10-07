#!/usr/bin/env python3
"""Square Peg portfolio scraper -> squarepeg_companies.json
Source: https://www.squarepeg.vc/portfolio — Webflow + Finsweet CMS filter,
one page. Each grid item: name, category filter value(s), entry stage and an
"exited" filter value (Acquired / IPO / Other, blank when not exited). Each
/portfolio/<slug> page adds the website link, description, founded year,
founders, "First Partnered In" year and the Square Peg investment team.
Hidden Webflow blocks (w-condition-invisible) are dropped before reading.
Status: Acquired -> acquired, IPO -> active (listed); blank/Other -> null.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, year_of, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.squarepeg.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "squarepeg_companies.json")
PRIMARY = "Square Peg"
SECTOR_TAG_MAP = {"fintech": ["FinTech / Insurance"], "saas": ["Future of Work"]}
LABELS = {"founded in", "founders", "first partnered in", "investment team", "open jobs", "acquired", "investment notes"}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Constantinople": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Joyous": ["Future of Work"],
    "Limitless Labs": ["Dev Tools / Cloud"],
    "Prospa": ["FinTech / Insurance"],
    "XFlow": ["FinTech / Insurance", "Dev Tools / Cloud"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for it in soup.select(".portfolio-grid > .w-dyn-item"):
        a = it.select_one("a.portfolio-box[href]")
        nm = it.select_one("[fs-cmsfilter-field=name]")
        name = clean(nm.get_text(" ")) if nm else None
        if not a or not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        g = lambda f: clean(it.select_one(f".filters-hide [fs-cmsfilter-field={f}]").get_text(" ")) if it.select_one(f".filters-hide [fs-cmsfilter-field={f}]") else None
        cats = [clean(x.get_text()) for x in it.select(".filters-hide [fs-cmsfilter-field=category]") if clean(x.get_text())]
        rows.append({"name": name, "href": urljoin(SOURCE_URL, a["href"]), "cats": cats, "stage": g("stage"), "exited": g("exited")})
        if limit and len(rows) >= limit:
            break
    details = fetch_many([r["href"] for r in rows])
    out = []
    for r in rows:
        url = desc = founded = partnered = None
        founders, team = [], []
        html = details.get(r["href"])
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for inv in ds.select(".w-condition-invisible"):
                inv.decompose()
            main_el = ds.find("main") or ds.body or ds
            st = [s.strip() for s in main_el.stripped_strings]
            for x in main_el.select("a[href^=http]"):
                u = clean_url(x["href"])
                if u and "squarepeg" not in u and "careers" not in u and "jobs" not in u:
                    url = u
                    break
            desc = next((clean(s) for s in st if len(s) > 60 and "Square Peg Capital Pty" not in s), None)
            founded = year_of(label_after(st, "founded in"))
            cur = None
            for s in st:
                low = s.lower()
                if low in LABELS:
                    cur = low
                    continue
                if cur == "founders":
                    founders.append(clean(s))
                elif cur == "investment team":
                    team.append(clean(s))
                elif cur == "first partnered in" and not partnered:
                    partnered = year_of(s)
        ex = (r["exited"] or "").lower()
        out.append({
            "company_name": r["name"],
            "description": desc,
            "company_url": url,
            "company_profile_url": r["href"],
            "status": "acquired" if ex == "acquired" else ("active" if ex == "ipo" else None),
            "site_status": r["exited"],
            "stage": stage_label(r["stage"]),
            "first_invested": partnered,
            "founded_year": founded,
            "founders": founders,
            "investment_team": team,
            "sectors": r["cats"],
            "everywhere_tags": tags_for(r["name"], desc, r["cats"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "founders", "investment_team", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
