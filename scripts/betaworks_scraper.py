#!/usr/bin/env python3
"""Betaworks portfolio scraper -> betaworks_companies.json
Source: https://www.betaworks.com/companies — Webflow CMS logo grid; name from
logo filename, website from anchor href.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.betaworks.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "betaworks_companies.json")
PRIMARY = "Betaworks"
TAG_OVERRIDES = {}


def name_from_img(src):
    fn = (src or "").split("/")[-1].split("?")[0]
    fn = re.sub(r"\.(png|jpg|jpeg|svg|webp|avif)$", "", fn, flags=re.I)
    fn = re.sub(r"%20", " ", fn)
    fn = re.sub(r"[-_+]+", " ", fn)
    fn = re.sub(r"\s*(logo|lockup|wordmark|black|white|frame|second).*$", "", fn, flags=re.I)
    fn = clean(fn)
    return fn if fn and len(fn) > 1 and not fn.isdigit() else None


def name_from_url(url):
    host = urlparse(url).netloc.lower().replace("www.", "")
    base = host.split(".")[0]
    if base in ("linktr", "bitly", "t", "creators"):
        # creators.spotify.com -> Spotify (Anchor)
        parts = host.split(".")
        if len(parts) >= 2 and parts[0] == "creators":
            return parts[1].title()
        return None
    return base.replace("-", " ").title()


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".w-dyn-item"):
        a = it.select_one("a.company-logo-container[href], a[href]")
        if not a:
            continue
        href = a.get("href") or ""
        if not href.startswith("http") or "betaworks" in href or is_social(href):
            continue
        img = a.find("img")
        # Prefer domain-derived names; logo filenames often include Webflow asset hashes.
        name = name_from_url(href) or name_from_img(img.get("src") if img else "")
        if name:
            # strip leading hex hash crumbs
            import re as _re
            name = _re.sub(r"^[0-9a-f]{8,}\s*", "", name, flags=_re.I).strip()
            # known domain polish
            polish = {"huggingface": "Hugging Face", "granola": "Granola", "giphy": "GIPHY",
                      "bitly": "Bitly", "tumblr": "Tumblr", "spotify": "Anchor / Spotify",
                      "thebrowser": "The Browser Company", "twodots-game": "Two Dots"}
            key = name.lower().replace(" ", "")
            for k,v in polish.items():
                if k in (href or "").lower() or key == k:
                    name = v
                    break
        if not name or name.lower() in seen or name.isdigit():
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
            "everywhere_tags": tags_for(name, None),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
