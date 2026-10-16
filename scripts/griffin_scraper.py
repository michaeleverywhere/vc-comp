#!/usr/bin/env python3
"""Griffin Gaming Partners portfolio scraper -> griffin_companies.json
Source: https://griffingp.com/ — homepage Our Portfolio logo links.
Caveat: featured logo subset on homepage (not a full paginated index).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://griffingp.com/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "griffin_companies.json")
PRIMARY = "Griffin Gaming Partners"
TAG_OVERRIDES = {}
# known filename fixes
NAME_FIX = {"forte 5": "Second Dinner", "overwolf": "Overwolf"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "griffingp" in href or is_social(href):
            continue
        img = a.find("img")
        if not img:
            continue
        alt = clean(img.get("alt"))
        src = img.get("src") or ""
        name = alt
        if not name:
            fn = unquote(src.split("/")[-1].split("?")[0])
            fn = re.sub(r"\.(png|jpg|jpeg|svg|webp)$", "", fn, flags=re.I)
            fn = re.sub(r"[-_+]", " ", fn)
            name = clean(fn) or urlparse(href).netloc.replace("www.", "").split(".")[0].title()
        name = NAME_FIX.get(name.lower(), name) if name else name
        if name and name.lower() in NAME_FIX:
            name = NAME_FIX[name.lower()]
        # also apply if raw name key
        for k, v in NAME_FIX.items():
            if name and name.lower() == k:
                name = v
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
            "everywhere_tags": tags_for(name, None, ["Gaming / Media / Entertainment"],
                                        {"gaming / media / entertainment": ["Gaming / Media / Entertainment"]}),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
