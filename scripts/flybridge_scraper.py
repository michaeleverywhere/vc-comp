#!/usr/bin/env python3
"""Flybridge portfolio scraper -> flybridge_companies.json
Source: https://www.flybridge.com/portfolio — Squarespace logo grid; company
website from anchor, name from image filename or domain.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.flybridge.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "flybridge_companies.json")
PRIMARY = "Flybridge"
TAG_OVERRIDES = {}


def name_from_img(src, alt=""):
    if alt and len(alt.strip()) > 1 and "logo" not in alt.lower():
        return clean(alt)
    fn = unquote((src or "").split("/")[-1].split("?")[0])
    fn = re.sub(r"\.(png|jpg|jpeg|svg|webp|avif)$", "", fn, flags=re.I)
    fn = re.sub(r"[-_+]+", " ", fn)
    fn = re.sub(r"\s*\(\d+\)\s*", " ", fn)
    fn = re.sub(r"\s*(logo|lockup|wordmark|black|white|bg removed|all portfolio logos).*$", "", fn, flags=re.I)
    fn = clean(fn)
    if fn and len(fn) > 1 and not fn.isdigit() and not re.fullmatch(r"\d+", fn):
        return fn
    return None


def name_from_url(url):
    host = urlparse(url).netloc.lower().replace("www.", "")
    base = host.split(".")[0]
    return base.replace("-", " ").title() if base else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "flybridge.com" in href or is_social(href):
            continue
        img = a.find("img")
        if not img:
            continue
        src = img.get("src") or img.get("data-src") or ""
        # Prefer domain name (filenames are often opaque hashes)
        name = name_from_url(href) or name_from_img(src, img.get("alt") or "")
        if not name or name.lower() in seen:
            continue
        if re.fullmatch(r"[\d\s]+", name) or len(name) < 2:
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
