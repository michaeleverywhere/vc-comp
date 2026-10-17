#!/usr/bin/env python3
"""Ingressive Capital portfolio scraper -> ingressive_companies.json
Source: https://ingressivecapital.com/our-portfolio/ — WordPress; companies come from
the site's own REST endpoint /wp-json/wp/v2/cpt_services (portfolio-company posts).
Each post body gives the description, founder names, and (on newer pages) labelled
Fund / Industry / Location / Website lines plus a "Visit Website" link; the
cpt_services_group taxonomy gives the sector."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social, html_text
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://ingressivecapital.com"
SOURCE_URL = ORIGIN + "/our-portfolio/"
PRIMARY = "Ingressive Capital"
LABELS = ("Founders", "Founder", "Fund", "Industry", "Location", "Website", "Visit Website", "Sector", "Stage")
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "healthtech": ["Health"],
              "logistics": ["Logistics / Supply Chain"], "agritech": ["Climate / Sustainability"],
              "energy": ["Climate / Sustainability"], "gaming": ["Gaming / Media / Entertainment"],
              "edtech": ["Future of Work"], "hr": ["Future of Work"], "saas": ["Dev Tools / Cloud"],
              "proptech": ["PropTech"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    groups = wp_terms(ORIGIN, "cpt_services_group")
    out = []
    for p in wp_all(ORIGIN, "cpt_services"):
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        s = BeautifulSoup(p.get("content", {}).get("rendered") or "", "html.parser")
        frags = [clean(t) for t in s.find_all(string=True) if clean(t)]
        idx = [i for i, f in enumerate(frags) if f in LABELS]
        desc = clean(" ".join(frags[:idx[0]] if idx else frags)) or None
        sec = {}
        for n, i in enumerate(idx):
            end = idx[n + 1] if n + 1 < len(idx) else len(frags)
            sec[frags[i]] = frags[i + 1:end]
        site = next((a["href"] for a in s.select("a[href^=http]")
                     if "ingressive" not in a["href"] and not is_social(a["href"])), None)
        loc = clean(", ".join(sec.get("Location") or [])) or None
        ind = clean(", ".join(sec.get("Industry") or [])) or None
        sectors = [groups[i] for i in (p.get("cpt_services_group") or []) if i in groups]
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors + ([ind] if ind and ind not in sectors else []), sector_map=SECTOR_MAP,
                       founders=sec.get("Founders") or sec.get("Founder") or [],
                       fund=clean(", ".join(sec.get("Fund") or [])) or None, location=loc,
                       status="active", detail_url=p.get("link")))
    finish(out, "ingressive", ("description", "company_url", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
