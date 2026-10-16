#!/usr/bin/env python3
"""Breega portfolio scraper -> breega_companies.json
Source: https://www.breega.com/ — homepage featured company names (Alice & Bob,
Exotec, ...). Caveat: featured subset only; no dedicated public portfolio index.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.breega.com/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "breega_companies.json")
PRIMARY = "Breega"
TAG_OVERRIDES = {}
# Featured names published as headings on the homepage portfolio strip
FEATURED_HINTS = {
    "alice & bob", "exotec", "moneybox", "011h", "sava", "gojob",
    "coverflex", "carbon maps", "socium",
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for h in soup.find_all(["h2", "h3", "h4", "h5"]):
        name = clean(h.get_text(" "))
        if not name:
            continue
        if name.lower() not in FEATURED_HINTS and name.upper() not in {x.upper() for x in FEATURED_HINTS}:
            # also accept exact case variants present on page
            if name.lower() not in FEATURED_HINTS:
                continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "everywhere_tags": tags_for(name, None),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("everywhere_tags",))


if __name__ == "__main__":
    main()
