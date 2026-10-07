#!/usr/bin/env python3
"""Spero Ventures portfolio scraper -> spero_companies.json
Source: https://spero.vc/portfolio/ — WordPress; every displayed company card
is server-rendered with a status badge, one-line description, website link
("Visit Website"), Founder(s)/CEO, Investment Details (entry round + month
and year of investment) and a "Why we Invested" link. The company name comes
from the logo alt text ("<Name> logo").
Only the companies shown on the portfolio page are kept; the WP REST
portfolio_company collection also lists older companies but without any
published fields (no status, description or website), so they are skipped.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, stage_label, clean_url, year_of, apply_tag_overrides

SOURCE_URL = "https://spero.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "spero_companies.json")
PRIMARY = "Spero Ventures"
STATUS = {"active": "active", "acquired": "acquired", "exited": "acquired"}


def lines(el):
    return [clean(t) for t in el.get_text("\n").split("\n") if clean(t)]


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Juno": ["FinTech / Insurance", "Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in soup.select(".portfolio-card"):
        logo = c.select_one("img[alt$=' logo']")
        name = clean(re.sub(r"\s+logo$", "", logo["alt"])) if logo else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        badge = c.select_one("span")
        raw_status = clean(badge.get_text()) if badge else None
        d = c.select_one(".leading-relaxed")
        desc = clean(d.get_text(" ")) if d else None
        site = None
        for a in c.select("a[href^=http]"):
            if (a.get("title") or "").lower() == "visit website" or "visit website" in a.get_text(" ").lower():
                site = clean_url(a["href"])
                break
        founders, stage_raw, inv_date, why = [], None, None, None
        g = c.select_one(".grid")
        for blk in (g.find_all("div", recursive=False) if g else []):
            lab = blk.select_one(".opacity-75")
            if not lab:
                continue
            key = clean(lab.get_text()).lower()
            val = lab.find_next_sibling("div")
            vals = lines(val) if val else []
            if key.startswith("founder"):
                founders = vals
            elif key.startswith("investment"):
                for v in vals:
                    if year_of(v):
                        inv_date = v
                    elif not stage_raw:
                        stage_raw = v
            elif key == "links" and val:
                a = val.select_one("a[href]")
                why = a["href"] if a else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "status": STATUS.get((raw_status or "").lower()),
            "site_status": raw_status,
            "stage": stage_label(stage_raw),
            "first_invested": str(year_of(inv_date)) if inv_date else None,
            "investment_date": inv_date,
            "founders": founders,
            "why_we_invested_url": why,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
