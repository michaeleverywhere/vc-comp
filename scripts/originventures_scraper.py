#!/usr/bin/env python3
"""Origin Ventures portfolio scraper -> originventures_companies.json
Source: https://www.originventures.com/portfolio — Squarespace gallery
(description in caption, website on clickthrough).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.originventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "originventures_companies.json")
PRIMARY = "Origin Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def name_from(desc, url):
    if desc:
        m = re.match(r"^([A-Z0-9][A-Za-z0-9 .:&'’+/-]{0,40}?)(?:\s+is|\s+helps|\s+building|\s+builds|\s+offers|\s+provides|\s+makes|\s+a |\s+an |\s+the )", desc)
        if m:
            return clean(m.group(1))
        # caption sometimes is just the name
        if len(desc) < 40 and not desc.endswith("."):
            return clean(desc)
    if url:
        host = urlsplit(url).netloc.lower().removeprefix("www.")
        return clean(host.split(".")[0].replace("-", " ").title())
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".gallery-grid-item"):
        cap = it.select_one(".gallery-caption-content, .gallery-caption")
        desc = clean(cap.get_text(" ")) if cap else None
        a = it.select_one("a[href^=http]")
        url = clean_url(a["href"]) if a and not is_social(a["href"]) and "originventures.com" not in a["href"] else None
        name = name_from(desc, url)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        # if name was taken from whole caption, treat caption as description only when longer
        description = desc if desc and len(desc) > 40 else (desc if desc and desc.lower() != name.lower() else None)
        if description and description.lower().startswith(name.lower()) is False and len(desc or "") <= 40:
            # short caption that wasn't the name — keep as desc
            pass
        out.append({
            "company_name": name,
            "description": description if description and description.lower() != name.lower() else (desc if desc and len(desc) > len(name) + 5 else None),
            "company_url": url,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
