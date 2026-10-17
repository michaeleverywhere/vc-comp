#!/usr/bin/env python3
"""GTMfund portfolio scraper -> gtmfund_companies.json
Source: https://www.gtmfund.com/portfolio/ — WordPress; every company comes from the
site's own REST endpoint /wp-json/wp/v2/portfolio with its taxonomies resolved:
portfolio_category (sector), portfolio-invested (round GTMfund entered at -> stage),
current-stage (company's latest round / Acquired), portfolio-investor (co-investors
the firm lists) and the Featured tag. The site publishes no company websites."""
import os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, html_text
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://www.gtmfund.com"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "GTMfund"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "health care": ["Health"], "govtech": ["RegTech/Gov/Legal"],
              "cloud infrastructure": ["Dev Tools / Cloud"], "devtools": ["Dev Tools / Cloud"],
              "devops & infra": ["Dev Tools / Cloud"], "crypto & web3": ["Web3 / Crypto"],
              "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"], "climate tech": ["Climate / Sustainability"],
              "edtech": ["Future of Work"], "delivery & logistics": ["Logistics / Supply Chain"],
              "data": ["Data & Analytics"], "analytics": ["Data & Analytics"], "proptech": ["PropTech"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    tx = {t: wp_terms(ORIGIN, t) for t in ("portfolio_category", "portfolio-invested", "current-stage",
                                             "portfolio-investor", "portfolio_tag")}
    names = lambda p, t: [tx[t][i] for i in (p.get(t) or []) if i in tx[t]]
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        sectors = names(p, "portfolio_category")
        entry = names(p, "portfolio-invested")
        cur = names(p, "current-stage")
        co = [x for x in names(p, "portfolio-investor") if "not publicly" not in x.lower()]
        desc = html_text(p.get("content", {}).get("rendered"))
        acquired = any(c.lower() == "acquired" for c in cur) or bool(re.search(r"\(acquired\b", desc or "", re.I))
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       stage=", ".join(entry) or None,
                       current_stage=", ".join(c for c in cur if c.lower() != "acquired") or None,
                       co_investors=co, featured="Featured" in names(p, "portfolio_tag"),
                       status="acquired" if acquired else "active", detail_url=p.get("link")))
    finish(out, "gtmfund", ("description", "stage", "current_stage", "co_investors", "everywhere_tags"))


if __name__ == "__main__":
    main()
