#!/usr/bin/env python3
"""TFX Capital portfolio scraper -> tfxcapital_companies.json
Source: https://tfxcap.com/tfxportfolio/companies/ — server-rendered WordPress page
with Active / Exited / Inactive sections. Each logo tile carries its exit note and
each paired biography panel gives name, headquarters, founders/leadership (name +
title), description and website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://tfxcap.com/tfxportfolio/companies/"
PRIMARY = "TFX Capital"
STATUS = {"active": "active", "inactive": "inactive"}


def tidy_loc(x):
    x = re.sub(r"\s*\((?:acquired|secondary)[^)]*\)\s*$", "", x or "", flags=re.I).strip()
    if x and x == x.upper():
        x = re.sub(r"\b([A-Za-z]{2})$", lambda m: m.group(1).upper(), x.title())
    return x or None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], {}
    for pi in s.select(".portfolio-items"):
        h = pi.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
        section = clean(h.get_text(" ", strip=True)).lower() if h else ""
        tiles = pi.select(".portfolio-item-container")
        bios = pi.select(".biography")
        for tile, bio in zip(tiles, bios):
            h4 = bio.find("h4")
            name = clean(h4.get_text(" ", strip=True)) if h4 else None
            if not name:
                continue
            note = clean(tile.get_text(" ", strip=True)) or None
            note = re.sub(r"^\((.*)\)$", r"\1", note) if note else None
            hq = None
            for item in bio.select(".info-item"):
                t = item.select_one(".info-title")
                if t and "headquarters" in t.get_text().lower():
                    t.extract(); hq = clean(item.get_text(" ", strip=True))
            founders = []
            for li in bio.select("ul.founder_info li"):
                ps = li.find_all("p")
                txt = [clean(x) for x in (ps[-1].stripped_strings if ps else [])]
                txt = [x for x in txt if x]
                if txt:
                    founders.append(f"{txt[0]} ({', '.join(txt[1:])})" if len(txt) > 1 else txt[0])
            dd = bio.select_one(".text-cover")
            desc = clean(dd.get_text(" ", strip=True)) if dd else None
            a = next((x["href"] for x in bio.select(".right-side a[href^=http]") if not is_social(x["href"])), None)
            if section.startswith("exit"):
                status = "acquired" if note and re.search(r"\bacq", note, re.I) else "exited"
            else:
                status = STATUS.get(section, "active")
            if name.lower() in seen:  # listed in Active and Exited (partial exit): keep one row
                r = seen[name.lower()]
                r["exit_note"] = r.get("exit_note") or note
                continue
            r = rec(name, desc, a, PRIMARY, SOURCE_URL, scraped_at, location=tidy_loc(hq),
                    founders=founders, status=status, exit_note=note, portfolio_section=section.title() or None)
            seen[name.lower()] = r
            out.append(r)
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} TFX companies")
    finish(out, "tfxcapital", ("description", "company_url", "location", "founders", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
