#!/usr/bin/env python3
"""Lavrock Ventures portfolio scraper -> lavrockventures_companies.json
Source: https://www.lavrockvc.com/portfolio/ — Lavrock's Squarespace portfolio cards: status
(active / acquired / exited), company name, description, leadership, location and website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.lavrockvc.com/portfolio/"
PRIMARY = "Lavrock Ventures"


def _na(v):
    return None if not v or v.strip().lower() in ("n/a", "na", "-") else v


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for t in s(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    st = [clean(x) for x in s.stripped_strings]
    st = [x for x in st if x]
    out, i = [], 0
    while i < len(st):
        if st[i].lower() == "status:" and i + 3 < len(st):
            status = st[i + 1].lower()
            name, j, desc = st[i + 2], i + 3, []
            while j < len(st) and not st[j].startswith("//") and st[j].lower() != "status:":
                desc.append(st[j]); j += 1
            f = {}
            while j < len(st) and st[j].startswith("//"):
                k = st[j].strip("/ :").lower()
                v = st[j + 1] if j + 1 < len(st) and not st[j + 1].startswith("//") and st[j + 1].lower() != "status:" else None
                f[k] = _na(v)
                j += 2 if v is not None else 1
            web = f.get("website")
            if web and not web.startswith("http"):
                web = "https://" + web
            if web and is_social(web):
                web = None
            lead = f.get("leadership")
            out.append(rec(name, " ".join(desc) or None, web, PRIMARY, SOURCE_URL, scraped_at,
                           status={"exited": "acquired"}.get(status, status), status_label=st[i + 1],
                           leadership=[clean(x) for x in re.split(r";|\s{2,}", lead) if clean(x)] if lead else [],
                           location=f.get("location")))
            i = j
        else:
            i += 1
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Lavrock companies")
    finish(out, "lavrockventures", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
