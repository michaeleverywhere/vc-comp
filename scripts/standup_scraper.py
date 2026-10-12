#!/usr/bin/env python3
"""StandUp Ventures portfolio scraper -> standup_companies.json
Source: https://www.standupvc.com/portfolio — Webflow; .portfolio_item cards with
name in img alt; detail pages publish description, founders, and company website.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             prune_substring_tags, apply_tag_overrides, label_after)
from _d20_common import write_out

SOURCE_URL = "https://www.standupvc.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "standup_companies.json")
PRIMARY = "StandUp Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio_item"):
        img = it.select_one("img[alt]")
        a = it.select_one("a[href]")
        name = clean(img.get("alt") if img else None)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        detail = urljoin(SOURCE_URL + "/", a["href"]) if a and a.get("href") else None
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "founders": [],
            "sectors": [],
            "location": None,
            "status": None,
            "detail_url": detail,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.15)
    for r in out:
        html = pages.get(r.pop("detail_url", None))
        if not html:
            r["everywhere_tags"] = tags_for(r["company_name"], None)
            continue
        ds = BeautifulSoup(html, "html.parser")
        strings = list(ds.stripped_strings)
        # description lives as loose text (not always in <p>)
        full = clean(ds.get_text(" "))
        if full:
            # "CompanyName ... Description Founders ..."
            nm = re.escape(r["company_name"])
            m = re.search(nm + r"\s+(?:Careers\s+)?(?:Twitter\s+)?(?:LinkedIn\s+)?(?:Company Website\s+)?" + nm + r"?\s+(.+?)\s+Founders\b", full, re.I)
            if not m:
                m = re.search(nm + r"\s+(.+?)\s+Founders\b", full, re.I)
            if m:
                desc = clean(m.group(1))
                # strip leading duplicate name / chrome
                desc = re.sub(r"^(?:Careers|Twitter|LinkedIn|Company Website)\s+", "", desc or "", flags=re.I)
                if desc and desc.lower().startswith(r["company_name"].lower()):
                    desc = clean(desc[len(r["company_name"]):])
                if desc and re.match(r"^(is|are|has|helps|provides)\b", desc, re.I):
                    desc = clean(r["company_name"] + " " + desc)
                r["description"] = desc if desc and len(desc) > 40 else None
        if not r.get("description"):
            for p in ds.select("p"):
                t = clean(p.get_text(" "))
                if t and len(t) > 60 and not re.search(r"Jean-Christophe|Founders", t):
                    r["description"] = t
                    break
        # founders label
        founders = []
        stop = {"careers", "twitter", "linkedin", "company website", "back to all companies",
                "sector", "location", "status", "active", "exited", "news"}
        for i, s in enumerate(strings):
            if s.strip().lower() == "founders" and i + 1 < len(strings):
                for s2 in strings[i + 1:]:
                    if s2.strip().lower() in stop:
                        break
                    if 2 <= len(s2) <= 60 and not re.search(r"\d{4}", s2):
                        founders.append(clean(s2))
                break
        r["founders"] = [f for f in founders if f][:8] or None
        # also parse Sector / Location / Status when present
        for i, s in enumerate(strings[:-1]):
            key = s.strip().lower()
            if key == "sector":
                r["sectors"] = [clean(strings[i+1])]
            elif key == "location" and not r.get("location"):
                r["location"] = clean(strings[i+1])
            elif key == "status":
                val = clean(strings[i+1])
                if val:
                    r["site_status"] = val
                    if val.lower() in ("exited", "acquired"):
                        r["status"] = "acquired"
                    elif val.lower() == "active":
                        r["status"] = "active"
        r["company_url"] = clean_url(first_external_link(ds, ("standupvc.com", "webflow.io", "twitter.com", "linkedin.com", "x.com")))
        # sometimes labeled Company Website
        for a in ds.select("a[href^=http]"):
            if "website" in (a.get_text(" ") or "").lower() or "company website" in (a.get_text(" ") or "").lower():
                u = clean_url(a["href"])
                if u:
                    r["company_url"] = u
                    break
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"), r.get("sectors"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
