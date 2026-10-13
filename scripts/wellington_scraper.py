#!/usr/bin/env python3
"""Wellington Management private investments scraper -> wellington_companies.json
Source: https://www.wellington.com/en/capabilities/private-investing/our-investments
AEM content fragments; fields from data-cmp-data-layer JSON (description/URL dd nodes are empty in SSR).
"""
import json, os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, html_text,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.wellington.com/en/capabilities/private-investing/our-investments"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "wellington_companies.json")
PRIMARY = "Wellington Management"
SECTOR_TAG_MAP = {
    "information technology": ["Enterprise / SaaS"],
    "financials": ["Fintech"],
    "biotechnology": ["BioTech / HealthTech"],
    "health care": ["BioTech / HealthTech"],
    "industrials": ["Deeptech / Robotics / AR/VR"],
    "consumer discretionary": ["Consumer"],
    "consumer staples": ["Consumer"],
    "communication services": ["Consumer"],
    "energy": ["Climate / Sustainability"],
    "real estate": ["PropTech / Real Estate"],
    "materials": ["Climate / Sustainability"],
}
TAG_OVERRIDES = {}
SECTOR_LABEL = {
    "information-technology": "Information technology",
    "financials": "Financials",
    "biotechnology": "Biotechnology",
    "health-care": "Health care",
    "industrials": "Industrials",
    "consumer-discretionary": "Consumer discretionary",
    "consumer-staples": "Consumer staples",
    "communication-services": "Communication services",
    "energy": "Energy",
    "real-estate": "Real estate",
    "materials": "Materials",
}


def elems_map(elements):
    out = {}
    for el in elements or []:
        title = (el.get("xdm:title") or "").rstrip(":")
        out[title] = el.get("xdm:text")
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select(".cmp-contentfragment"):
        raw = card.get("data-cmp-data-layer")
        if not raw:
            continue
        try:
            layer = json.loads(raw)
            inner = next(iter(layer.values()))
        except Exception:
            continue
        name = clean(inner.get("dc:title"))
        em = elems_map(inner.get("elements"))
        if not name:
            name = html_text(em.get("Company Title") or "")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = html_text(em.get("Company Description") or "")
        url = clean_url(em.get("Company URL") or "")
        if not url:
            # CTA html may hold the link
            cta = em.get("Company CTA") or ""
            m = re.search(r'href="(https?://[^"]+)"', cta)
            if m:
                url = clean_url(m.group(1))
        sector_token = em.get("Sector:") or em.get("Sector") or ""
        sector = None
        m = re.search(r"sector/([a-z0-9-]+)", sector_token)
        if m:
            sector = SECTOR_LABEL.get(m.group(1), m.group(1).replace("-", " ").title())
        # also try visible sector value
        if not sector:
            sv = card.select_one(".cmp-sectorvalue")
            if sv:
                sector = clean(sv.get_text(" "))
        status_token = em.get("Realization Status:") or em.get("Realization Status") or ""
        status = site_status = None
        if "unrealized" in status_token:
            status, site_status = "active", "unrealized"
        elif "realized" in status_token:
            status, site_status = "acquired", "realized"
        # class fallback
        classes = " ".join(card.get("class") or []).lower()
        if not status:
            if "unrealized" in classes:
                status, site_status = "active", "unrealized"
            elif re.search(r"(?<!un)realized", classes):
                status, site_status = "acquired", "realized"
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "sectors": sectors,
            "status": status,
            "site_status": site_status,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "status", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
