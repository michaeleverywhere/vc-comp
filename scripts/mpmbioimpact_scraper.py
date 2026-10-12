#!/usr/bin/env python3
"""MPM BioImpact portfolio scraper -> mpmbioimpact_companies.json
Source: https://mpmbioimpact.com/portfolio/ — .portfolio-item cards with name;
detail pages publish description / website when available. Biotech-focused.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://mpmbioimpact.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "mpmbioimpact_companies.json")
PRIMARY = "MPM BioImpact"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-item"):
        img = it.select_one("img[alt]")
        a = it.select_one("a[href]")
        name = clean(img.get("alt") if img and img.get("alt") else None) or clean(it.get_text(" "))
        if name:
            name = clean(re.sub(r"\s+Logo\s*$", "", name, flags=re.I))
        if not name or name.lower() in seen or name.lower() in ("investor login", "map", "portfolio"):
            continue
        if len(name) > 60:
            continue
        seen.add(name.lower())
        detail = None
        if a and a.get("href") and not a["href"].startswith("#"):
            detail = urljoin(SOURCE_URL, a["href"])
            if "mpmbioimpact.com" not in detail and detail.startswith("http"):
                # direct external
                out.append({
                    "company_name": name,
                    "description": None,
                    "company_url": clean_url(detail),
                    "sectors": ["BioTech"],
                    "everywhere_tags": ["BioTech"],
                    "primary_investor": PRIMARY,
                    "source_url": SOURCE_URL,
                    "scraped_at": scraped_at,
                })
                continue
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "sectors": ["BioTech"],
            "detail_url": detail,
            "everywhere_tags": ["BioTech"],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.15)
    for r in out:
        du = r.pop("detail_url", None)
        html = pages.get(du) if du else None
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for p in ds.select("p"):
                t = clean(p.get_text(" "))
                if t and len(t) > 60:
                    r["description"] = t
                    break
            r["company_url"] = clean_url(first_external_link(ds, ("mpmbioimpact.com", "mpmcapital.com")))
        r["sectors"] = r.get("sectors") or ["BioTech"]
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"), r["sectors"], {"biotech": ["BioTech"]}) or ["BioTech"]
    prune_substring_tags(out, {"biotech": ["BioTech"]})
    for r in out:
        if "BioTech" not in (r.get("everywhere_tags") or []):
            r["everywhere_tags"] = (["BioTech"] + list(r.get("everywhere_tags") or []))[:4]
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
