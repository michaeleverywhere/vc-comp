#!/usr/bin/env python3
"""4DX Ventures portfolio scraper -> 4dxventures_companies.json
Source: https://www.4dxventures.com/portfolio — Webflow CMS (Finsweet
filters), server-rendered (pagination followed). Each portfolio item has a
modal with the company name (logo alt), website link, description, and a
metadata block: industry, founded (year), hq (country). The optional card
subtext (e.g. "Acquired by ...") is kept in site_status. No investment stage
or year is published, so stage / first_invested stay blank.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.4dxventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "4dxventures_companies.json")
PRIMARY = "4DX Ventures"
SECTOR_TAG_MAP = {
    "climate": ["Climate / Sustainability"], "edtech": ["Future of Work"], "fintech": ["FinTech / Insurance"],
    "healthtech": ["Health"], "logistics": ["Logistics / Supply Chain"], "food & beverage": ["CPG"],
    "e-commerce & marketplaces": ["Consumer"], "creative industries": ["Gaming / Media / Entertainment"],
    "deeptech / ai": ["Deeptech / Robotics / AR/VR"], "enterprise software": ["Future of Work"],
    "connectivity": ["Dev Tools / Cloud"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Zoie": ["Health"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio-item.w-dyn-item"):
            img = it.select_one(".modal-top-bar img[alt]")
            name = clean(img.get("alt")) if img else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            site = None
            for a in it.select("a.modal-link[href]"):
                if clean(a.get_text(" ")) == "Website":
                    site = a["href"]
            d = it.select_one(".modal-card .w-richtext")
            desc = clean(d.get_text(" ")) if d else None
            meta = {}
            for m in it.select(".modal-meta-data"):
                h = m.select_one("h5")
                v = m.select_one("div")
                if h and v:
                    meta[clean(h.get_text()).lower()] = clean(v.get_text(" "))
            sub = it.select_one(".portfolio-subtext-margin")
            subtext = clean(sub.get_text(" ")) if sub else None
            inds = [clean(x.get_text()) for x in it.select('.portfolio-flex-wrapper [fs-cmsfilter-field="industries"]')]
            inds = [x for x in inds if x and x != "All"]
            acq = re.search(r"(?i)acquired by\s+(.+)", subtext or "")
            acquirer = clean(acq.group(1)) if acq else None
            # Exited cards show the ACQUIRER's logo/name/website with subtext
            # "Acquired <portfolio company>" (e.g. Carta / "Acquired Tactyc"):
            # the 4DX portfolio company is the one named in the subtext.
            m2 = re.fullmatch(r"(?i)acquired\s+(?!by\b)(.+)", subtext or "")
            if m2:
                acquirer, name = name, clean(m2.group(1))
                site = None  # the card's website link is the acquirer's
            founded = meta.get("founded")
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(site),
                "status": "acquired" if acquirer else None,
                "site_status": subtext,
                "acquirer": acquirer,
                "location": meta.get("hq"),
                "year_founded": int(founded) if founded and re.fullmatch(r"\d{4}", founded) else None,
                "sectors": inds or ([meta["industry"]] if meta.get("industry") else []),
                "everywhere_tags": tags_for(name, desc, inds, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "year_founded", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
