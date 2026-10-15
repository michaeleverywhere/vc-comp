#!/usr/bin/env python3
"""Third Rock Ventures portfolio scraper -> thirdrock_companies.json
Source: https://www.thirdrockventures.com/portfolio — SSR cards with data-slug
and logo image; detail pages are JS hash routes (not crawlable). Names come
from the logo filename / slug. Biotech-focused firm.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.thirdrockventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "thirdrock_companies.json")
PRIMARY = "Third Rock Ventures"
TAG_OVERRIDES = {}


def name_from(slug, img_src):
    if img_src:
        base = unquote(img_src.split("/")[-1].split("?")[0])
        base = re.sub(r"\.(png|jpg|jpeg|webp|svg)$", "", base, flags=re.I)
        base = re.sub(r"[-_]+", " ", base).strip()
        # drop trailing size tokens
        base = re.sub(r"\s+\d+x\d+$", "", base)
        if base and base.lower() not in ("logo", "image", "production"):
            return clean(base)
    return clean(slug.replace("-", " ").title()) if slug else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".js-portfolio-company"):
        slug = it.get("data-slug")
        img = it.select_one("img")
        src = img.get("src") if img else None
        name = name_from(slug, src)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "sectors": ["Healthcare"],
            "everywhere_tags": tags_for(name, None, ["Healthcare"], {"healthcare": ["Health", "BioTech"]}),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("everywhere_tags",))


if __name__ == "__main__":
    main()
