#!/usr/bin/env python3
"""BMW i Ventures portfolio scraper -> bmwiventures_companies.json
Source: https://www.bmwiventures.com/portfolio — Webflow CMS .portfolio00__card
with description, HQ, sector, status (IPO/Acquired/...), and company website.
Name taken from description lead-in or website domain (logos lack alts).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.bmwiventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bmwiventures_companies.json")
PRIMARY = "BMW i Ventures"
SECTOR_TAG_MAP = {
    "car development": ["Transportation / Mobility"],
    "energy": ["Climate / Sustainability"],
    "production": ["Deeptech / Robotics / AR/VR"],
    "customer experience": ["Consumer"],
    "supply chain": ["Logistics / Supply Chain"],
    "materials": ["Deeptech / Robotics / AR/VR", "Climate / Sustainability"],
    "ai": ["Data & Analytics"],
    "mobility": ["Transportation / Mobility"],
}
TAG_OVERRIDES = {}


def name_from(desc, url, img_srcs):
    if desc:
        m = re.match(r"^([A-Z0-9][A-Za-z0-9 .:&'’+/-]{0,50}?)(?:\s+is|\s+has|\s+provides|\s+offers|\s+builds|\s+helps|\s+enables|\s+delivers|\s+develops|\s+creates|\s+makes|\s+designs|\s+operates|\s+brings|\s+transforms|\s+redefines|\s+connects|\s+powers)", desc)
        if m:
            return clean(m.group(1))
    for src in img_srcs:
        m = re.search(r"/([^/]*?(?:logo|Logo)[^/]*?)\.(?:png|jpg|jpeg|webp|svg)", src)
        if m:
            slug = m.group(1)
            slug = re.sub(r"[-_]?(logo|Logo|white|White|img|small|desktop)", " ", slug)
            slug = clean(slug.replace("-", " ").replace("_", " "))
            if slug and len(slug) > 1:
                return slug
    if url:
        host = urlsplit(url).netloc.lower().removeprefix("www.")
        base = host.split(".")[0].replace("-", " ").title()
        return clean(base)
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select(".portfolio00__card"):
        desc = clean(card.select_one(".portfolio00__rich-text").get_text(" ")) if card.select_one(".portfolio00__rich-text") else None
        loc = clean(card.select_one(".portfolio00__loc-text").get_text(" ")) if card.select_one(".portfolio00__loc-text") else None
        # sector / status from labeled info items
        sector, status_raw = None, None
        items = card.select(".portfolio00__info-item")
        for it in items:
            t = clean(it.get_text(" "))
            if not t:
                continue
            if t.lower().startswith("sector"):
                sector = clean(re.sub(r"^[Ss]ector\s*", "", t))
            elif t.lower().startswith("status"):
                status_raw = clean(re.sub(r"^[Ss]tatus\s*", "", t))
            elif t.lower().startswith("description"):
                pass
            elif t.lower().startswith("hq"):
                if not loc:
                    loc = clean(re.sub(r"^[Hh][Qq]\s*", "", t))
        a = card.select_one('a[href^="http"]')
        url = clean_url(a["href"]) if a else None
        imgs = [(img.get("src") or "") for img in card.select("img")]
        name = name_from(desc, url, imgs)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        status = None
        site_status = status_raw
        if status_raw:
            low = status_raw.lower()
            if "acquired" in low:
                status = "acquired"
            elif "ipo" in low or "public" in low:
                status = "active"  # IPO kept as active per pipeline convention; site_status holds IPO
            elif "active" in low or "current" in low:
                status = "active"
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "sectors": sectors,
            "location": loc,
            "status": status,
            "site_status": site_status,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "status", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
