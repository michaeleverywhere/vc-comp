#!/usr/bin/env python3
"""CoinFund portfolio scraper -> coinfund_companies.json
Source: https://www.coinfund.io/portfolio — featured companies with Visit/See website links.
Caveat: page exposes a featured subset (not full portfolio dump).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.coinfund.io/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "coinfund_companies.json")
PRIMARY = "CoinFund"
TAG_OVERRIDES = {}


def name_from_url(url):
    host = urlparse(url).netloc.lower().replace("www.", "")
    if host in ("x.com", "twitter.com"):
        path = urlparse(url).path.strip("/")
        return path.split("/")[0].replace("_", " ").title() if path else None
    base = host.split(".")[0]
    return base.replace("-", " ").title() if base else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        label = (clean(a.get_text(" ")) or "").lower()
        if "coinfund" in href:
            continue
        if "website" not in label:
            continue
        if is_social(href) and "x.com" not in href:
            continue
        name = None
        parent = a.find_parent(["div", "article", "section", "li"])
        if parent:
            for h in parent.find_all(["h1", "h2", "h3", "h4", "p", "span"]):
                t = clean(h.get_text(" "))
                if t and t.lower() not in ("see website", "visit website", "website") and len(t) < 50:
                    name = t
                    break
        name = name or name_from_url(href)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
            "everywhere_tags": tags_for(name, None, ["Web3 / Crypto"], {"web3 / crypto": ["Web3 / Crypto"]}),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
