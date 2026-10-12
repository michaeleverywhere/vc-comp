#!/usr/bin/env python3
"""Liquid 2 Ventures portfolio scraper -> liquid2_companies.json
Source: https://www.liquid2.vc/portfolio — Webflow; .portfolio_item-main cards with
description text and external company website link. Name from link text / heading.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.liquid2.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "liquid2_companies.json")
PRIMARY = "Liquid 2 Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio_item-main"):
        # external company link
        url = None
        for a in it.select("a[href^=http]"):
            u = a["href"]
            if "liquid2.vc" in u or "webflow.io" in u or is_social(u) or "crunchbase.com" in u.lower():
                continue
            url = clean_url(u)
            if url:
                break
        txt = clean(it.get_text(" "))
        if txt:
            txt = re.sub(r"\s*Visit site\s*$", "", txt, flags=re.I)
            txt = re.sub(r"\s*crunchbase\s*$", "", txt, flags=re.I)
        # name: from img alt, or domain, or first words
        img = it.select_one("img[src], img[alt]")
        name = clean(img.get("alt")) if img and img.get("alt") else None
        if not name and img and img.get("src"):
            from urllib.parse import unquote
            m = re.search(r"/([^/]+?)\.(?:svg|png|jpg|jpeg|webp)(?:$|\?)", img.get("src"), re.I)
            if m:
                slug = unquote(m.group(1))
                slug = re.sub(r"[-_]?(logo|Logo|colored|Colored|white|White)$", "", slug)
                # uuid prefixes like 665d92738dc6ec89f9dbbde6_gitlab
                slug = re.sub(r"^[0-9a-f]{20,}_", "", slug, flags=re.I)
                slug = slug.replace("-", " ").replace("_", " ")
                name = clean(slug.title()) if slug else None
                # known filename fixes
                fixes = {"Andruil": "Anduril", "Athelas": "Athelas", "Applied Intuition Logo Colored": "Applied Intuition",
                         "Applied Intuition Logo": "Applied Intuition", "Kepler Compute Logo": "Kepler Compute",
                         "Bearflag": "Bear Flag Robotics", "Gitlab": "GitLab", "Stoke": "Stoke Space",
                         "Astra": "Astranis"}
                name = fixes.get(name, name)
                if name:
                    name = clean(re.sub(r"\s+Logo\s*$", "", name, flags=re.I))
        if not name and url:
            from urllib.parse import urlsplit
            host = urlsplit(url).netloc.lower().removeprefix("www.")
            specials = {"about.gitlab.com": "GitLab", "gitlab.com": "GitLab", "www.anduril.com": "Anduril",
                        "anduril.com": "Anduril", "www.athelas.com": "Athelas", "athelas.com": "Athelas",
                        "www.bearflagrobotics.com": "Bear Flag Robotics", "www.keplercompute.com": "Kepler Compute",
                        "www.stokespace.com": "Stoke Space", "www.astranis.com": "Astranis",
                        "www.appliedintuition.com": "Applied Intuition", "www.jasper.ai": "Jasper",
                        "jasper.ai": "Jasper", "retool.com": "Retool", "www.rippling.com": "Rippling",
                        "remote.com": "Remote"}
            name = specials.get(host) or specials.get(host.removeprefix("www."))
            if not name:
                name = host.split(".")[0].replace("-", " ").title()
                if host.startswith("about."):
                    name = host.split(".")[1].title()
        if not name and txt:
            m = re.match(r"^([A-Z][A-Za-z0-9 .&'’+/-]{1,40}?)(?:\s+is|\s+enables|\s+helps|\s+builds|\s+provides|\s+offers|\s+manages|\s+delivers|\s+makes)", txt)
            name = clean(m.group(1)) if m else None
        if name:
            name = {"Gitlab": "GitLab", "Stoke": "Stoke Space", "Astra": "Astranis",
                    "Applied Intuition Logo": "Applied Intuition"}.get(name, name)
            name = clean(re.sub(r"\s+Logo\s*$", "", name or "", flags=re.I))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": txt,
            "company_url": url,
            "everywhere_tags": tags_for(name, txt),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
