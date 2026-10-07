#!/usr/bin/env python3
"""Nauta Capital portfolio scraper -> nautacapital_companies.json
Source: https://www.nautacapital.com/portfolio — Webflow + Finsweet CMS list,
paginated via ?<hash>_page=N. Each item carries Finsweet filter fields
(industry, founded, stage, status, location), the company's website link, a
one-liner and "Invested in YYYY" / "Exited in YYYY" lines (the exit line is
hidden with w-condition-invisible when the company has not exited).
Status: Active -> active; Exited / visible exit year -> acquired (raw kept).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, year_of, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.nautacapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "nautacapital_companies.json")
PRIMARY = "Nauta Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "health": ["Health"],
    "ai/ml & data": ["Data & Analytics"], "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"],
    "industry 4.0": ["Deeptech / Robotics / AR/VR"], "insurtech": ["FinTech / Insurance"],
    "g2m & customer": ["Future of Work"], "future of work": ["Future of Work"],
    "dev tools & infra": ["Dev Tools / Cloud"], "security & privacy": ["Cybersecurity"],
    "fintech & insurtech": ["FinTech / Insurance"], "productivity": ["Future of Work"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Tangany": ["FinTech / Insurance", "Web3 / Crypto"],
    "Trustworks": ["Cybersecurity"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".portfolio_collection-item"):
            h = it.select_one(".portfolio_hover-heading")
            name = clean(h.get_text(" ")) if h else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            g = lambda f: clean(it.select_one(f"[fs-cmsfilter-field={f}]").get_text(" ")) if it.select_one(f"[fs-cmsfilter-field={f}]") else None
            a = it.select_one("a.portfolio_item-wrapper[href]")
            d = it.select_one(".text-portfolio-oneliner")
            desc = clean(d.get_text(" ")) if d else None
            embeds = it.select_one(".portfolio_item-wrapper").select(".html-embed-2") if it.select_one(".portfolio_item-wrapper") else []
            invested = exited = None
            for e in embeds:
                t = clean(e.get_text(" ")) or ""
                if t.lower().startswith("invested"):
                    invested = year_of(t)
                elif t.lower().startswith("exited") and "w-condition-invisible" not in (e.get("class") or []):
                    exited = year_of(t)
            st = g("status")
            if (st or "").lower() == "exited" or exited:
                status = "acquired"
            elif (st or "").lower() == "active":
                status = "active"
            else:
                status = None
            ind = g("industry")
            sectors = [x.strip() for x in (ind or "").split(",") if x.strip()]
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(a["href"]) if a else None,
                "status": status,
                "site_status": st,
                "exit_year": exited,
                "first_invested": invested,
                "founded_year": year_of(g("founded")),
                "stage": stage_label(g("stage")),
                "location": g("location"),
                "sectors": sectors,
                "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "first_invested", "stage", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
