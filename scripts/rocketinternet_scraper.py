#!/usr/bin/env python3
"""Rocket Internet portfolio scraper -> rocketinternet_companies.json
Source: https://www.rocket-internet.com/companies — Webflow company tiles + modals.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.rocket-internet.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "rocketinternet_companies.json")
PRIMARY = "Rocket Internet"

# Known display names for modal ids (site uses short ids)
ID_NAMES = {
    "agencasa": "AgenCasa",
    "everstox": "Everstox",
    "expertlead": "ExpertLead",
    "flashcoffee": "FlashCoffee",
    "gfg": "Global Fashion Group",
    "gsg": "Global Savings Group",
    "helpling": "Helpling",
    "home24": "Home24",
    "instafreight": "InstaFreight",
    "jeeny": "Jeeny",
    "katoo": "Katoo",
    "loadsmile": "Loadsmile",
    "nestpick": "Nestpick",
    "payflow": "Payflow",
    "spenmo": "Spenmo",
    "spotcap": "Spotcap",
    "tinvio": "Tinvio",
    "vitable": "Vitable",
    "bluenest": "Bluenest",
    "grosenia": "Grosenia",
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    # Map modal id -> vertical / founded from modal-info blocks adjacent in DOM
    # Structure: company-item has data-modal-id; matching modal elsewhere
    modal_meta = {}
    for mod in soup.select("[id], .w-modal, .modal, [data-modal], .company-modal"):
        mid = mod.get("id") or mod.get("data-modal") or mod.get("data-modal-id")
        if not mid:
            continue
        text = clean(mod.get_text(" ", strip=True)) or ""
        vertical = None
        m = re.search(r"VERTICAL\s+(.+?)(?:\s+FOUNDED|\s+WEBSITE|$)", text, re.I)
        if m:
            vertical = clean(m.group(1))
        founded = None
        m = re.search(r"FOUNDED\s+(\d{4})", text, re.I)
        if m:
            founded = m.group(1)
        website = None
        for a in mod.select("a[href^='http']"):
            href = a["href"]
            if "rocket-internet" in href:
                continue
            website = clean(href)
            break
        modal_meta[mid.lower()] = {"vertical": vertical, "founded": founded, "website": website}

    # Also parse standalone company-modal-info + preceding siblings — pair via nearby ids
    for a in soup.select("a.company-link[data-modal-id], a[data-modal-id]"):
        mid = (a.get("data-modal-id") or "").lower()
        if not mid:
            continue
        name = ID_NAMES.get(mid) or mid.replace("-", " ").title()
        # Try img filename as name hint
        for img in a.select("img[src]"):
            src = img.get("src") or ""
            base = src.split("/")[-1].split("_")[0].split(".")[0]
            if base and len(base) > 2 and mid not in ID_NAMES:
                name = base
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        meta = modal_meta.get(mid) or {}
        # Find matching modal by id containing mid
        if not meta:
            for sel in (f"#{mid}", f"[id*='{mid}']", f"[data-modal-id='{mid}']"):
                mod = soup.select_one(sel)
                if not mod:
                    continue
                text = clean(mod.get_text(" ", strip=True)) or ""
                m = re.search(r"VERTICAL\s+(.+?)(?:\s+FOUNDED|\s+WEBSITE|$)", text, re.I)
                vertical = clean(m.group(1)) if m else None
                m = re.search(r"FOUNDED\s+(\d{4})", text, re.I)
                founded = m.group(1) if m else None
                website = None
                for aa in mod.select("a[href^='http']"):
                    if "rocket-internet" not in aa["href"]:
                        website = clean(aa["href"])
                        break
                meta = {"vertical": vertical, "founded": founded, "website": website}
                break
        # Website from page-level external links matching name
        website = meta.get("website")
        if not website:
            for aa in soup.select("a[href^='http']"):
                href = aa["href"]
                if "rocket-internet" in href or "webflow" in href:
                    continue
                host = re.sub(r"^https?://(www\.)?", "", href).split("/")[0].lower()
                token = re.sub(r"[^a-z0-9]", "", name.lower())
                if token and token[:4] in host.replace("-", ""):
                    website = clean(href)
                    break
        sectors = [meta["vertical"]] if meta.get("vertical") else None
        rec = {
            "company_name": name,
            "description": None,
            "company_url": website,
            "status": "active",
            "stage": None,
            "sectors": sectors,
            "founded_year": meta.get("founded"),
            "everywhere_tags": classify(name, None, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
