#!/usr/bin/env python3
"""TLV Partners portfolio scraper -> tlv_companies.json
Source: https://www.tlv.partners/portfolio/ — SSR .tlv_company drawers with
Sector, Entry-stage (Seed/A/B...), Visit website, tagline + description.
Company name derived from description lead-in or logo filename (site does not
publish a separate name field).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, stage_label,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.tlv.partners/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "tlv_companies.json")
PRIMARY = "TLV Partners"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "ai/ml": ["Data & Analytics"], "ai": ["Data & Analytics"],
    "devtools": ["Dev Tools / Cloud"], "dev tools": ["Dev Tools / Cloud"],
    "health/biotech": ["Health", "BioTech"], "health": ["Health"], "biotech": ["BioTech"],
    "cyber": ["Cybersecurity"], "cybersecurity": ["Cybersecurity"],
    "enterprise": ["Future of Work"], "consumer": ["Consumer"],
    "climate": ["Climate / Sustainability"], "marketplace": ["Consumer"],
}
TAG_OVERRIDES = {}


def name_from(desc, url, logo_style):
    if desc:
        m = re.match(r"^([A-Z0-9][A-Za-z0-9 .:&'’+/-]{0,40}?)(?:\s+is|\s+has|\s+helps|\s+builds|\s+provides|\s+offers|\s+enables|\s+optimizes|\s+transforms|\s+delivers|\s+empowers|\s+creates|\s+develops|\s+brings|\s+makes|\s+uses|\s+connects|\s+powers|\s+redefines|\s+automates)", desc)
        if m:
            return clean(m.group(1))
    # logo filename
    if logo_style:
        m = re.search(r"/([^/]+?)\.(?:svg|png|jpg|jpeg|webp)", logo_style, re.I)
        if m:
            slug = unquote(m.group(1))
            slug = re.sub(r"[-_]?(White|Color|Logo|1|2)$", "", slug, flags=re.I)
            slug = slug.replace("-", " ").replace("_", " ")
            if slug and slug.lower() not in ("next",):  # next.svg is Next Insurance - keep
                return clean(slug)
            return clean(slug)
    if url:
        host = urlsplit(url).netloc.lower().removeprefix("www.")
        return clean(host.split(".")[0].replace("-", " ").title())
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for c in soup.select(".tlv_company"):
        details = { }
        for p in c.select(".tlv_details p"):
            t = clean(p.get_text(" "))
            if not t:
                continue
            if t.lower().startswith("sector:"):
                details["sector"] = clean(t.split(":", 1)[1])
            elif t.lower().startswith("entry-stage:") or t.lower().startswith("entry stage:"):
                details["stage"] = clean(t.split(":", 1)[1])
        a = c.select_one(".visit a[href], .tlv_details a[href^=http]")
        url = clean_url(a["href"]) if a else None
        tagline = clean(c.select_one(".tlv_desc strong").get_text(" ")) if c.select_one(".tlv_desc strong") else None
        desc_el = c.select_one(".tlv_desc span") or (c.select(".tlv_desc p")[-1] if c.select(".tlv_desc p") else None)
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        logo = c.select_one(".tlv_logo_color, .tlv_logo_white_horizontal")
        logo_style = (logo.get("style") if logo else "") or ""
        name = name_from(desc, url, logo_style)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = [s.strip() for s in re.split(r",|/", details.get("sector") or "") if s.strip()]
        # map Entry-stage A/B to Series A/B; Seed stays Seed
        raw_stage = details.get("stage")
        stage = None
        if raw_stage:
            rs = raw_stage.strip()
            if re.fullmatch(r"[A-H]", rs, re.I):
                stage = stage_label("Series " + rs.upper())
            else:
                stage = stage_label(rs)
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": tagline,
            "company_url": url,
            "sectors": sectors,
            "stage": stage,
            "everywhere_tags": tags_for(name, " ".join(x for x in (desc, tagline) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "stage", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
