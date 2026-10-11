#!/usr/bin/env python3
"""Revolution portfolio scraper -> revolution_companies.json
Source: https://www.revolution.com/portfolio — Webflow CMS list
(.portfolio_list-wrapper, paginated `?<hash>_page=N`). Each .portfolio_item has
the company name, the company website (full-card link), an outcome line
(e.g. "Acquired by Edison Partners"), a one-line description, Finsweet fields
fund (Rise of the Rest / Revolution Growth / Revolution Ventures), region,
status (Active / Realized) and sector, plus the HQ city and state.
status: outcome "Acquired by ..." -> acquired; status Active -> active;
"Realized" (incl. IPOs) kept in site_status. No round or year published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.revolution.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "revolution_companies.json")
PRIMARY = "Revolution"
SECTOR_TAG_MAP = {
    "finance": ["FinTech / Insurance"], "real estate & hospitality": ["PropTech"],
    "sports, media, & entertainment": ["Gaming / Media / Entertainment"], "food & agriculture": ["CPG"],
    "healthcare": ["Health"], "fintech": ["FinTech / Insurance"], "financial services": ["FinTech / Insurance"],
    "education & workforce": ["Future of Work"], "consumer & e-commerce": ["Consumer"],
    "real estate": ["PropTech"], "logistics": ["Logistics / Supply Chain"], "food": ["CPG"],
    "energy & sustainability": ["Climate / Sustainability"], "mobility": ["Transportation / Mobility"],
    "agtech": ["Climate / Sustainability"], "media & entertainment": ["Gaming / Media / Entertainment"],
    "security": ["Cybersecurity"], "defense": ["RegTech/Gov/Legal"],
}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "75F": ["PropTech", "Climate / Sustainability"],
    "86 Repairs": ["PropTech"],
    "Acres": ["PropTech", "Data & Analytics"],
    "Anvl": ["Future of Work", "Cybersecurity"],
    "Aurora Insight": ["Data & Analytics"],
    "Boundless Mind": ["Data & Analytics"],
    "Chassi": ["Deeptech / Robotics / AR/VR"],
    "Cultured Decadence": ["CPG", "Climate / Sustainability"],
    "Decide": ["Gaming / Media / Entertainment"],
    "Event.Gives": ["Consumer"],
    "GoSpotCheck": ["Future of Work"],
    "K4Connect": ["Health"],
    "Kangarootime": ["Future of Work"],
    "Membersuite": ["Future of Work"],
    "Place Exchange": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Playa": ["CPG"],
    "Resolute AI": ["Data & Analytics"],
    "Schola": ["Consumer"],
    "UberMedia": ["Data & Analytics"],
    "ZenBusiness": ["Future of Work", "RegTech/Gov/Legal"],
}


def field(it, name):
    vals = [clean(x.get_text(" ")) for x in it.select(f"[fs-list-field={name}]")]
    return [v for v in vals if v]


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL, max_pages=120):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio_list-wrapper .portfolio_item"):
            n = it.select_one(".company-name")
            name = clean(n.get_text(" ")) if n else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            a = it.select_one("a.portfolio_link-full[href]")
            d = it.select_one(".portfolio_description .w-richtext")
            desc = clean(d.get_text(" ")) if d else None
            nm = it.select_one(".portfolio_name")
            outcome = None
            if nm:
                o = nm.select_one("[fs-list-field=fund]")
                outcome = clean(o.get_text(" ")) if o else None
            desc_box = it.select_one(".portfolio_description")
            funds = field(desc_box, "fund") if desc_box else []
            region = field(desc_box, "region") if desc_box else []
            st = field(desc_box, "status") if desc_box else []
            sectors = field(it, "sector")
            locp = [clean(p.get_text(" ")) for p in it.select(".portfolio_location p") if clean(p.get_text(" ")) not in (None, ",")]
            loc = ", ".join(locp) or None
            st = st[0] if st else None
            acquired = (outcome or "").lower().startswith("acquired")
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(a["href"]) if a else None,
                "sectors": sectors,
                "location": loc,
                "revolution_fund": funds[0] if funds else None,
                "region": region[0] if region else None,
                "outcome": outcome,
                "site_status": st,
                "status": "acquired" if acquired else ("active" if (st or "").lower() == "active" else None),
                "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "location", "revolution_fund", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
