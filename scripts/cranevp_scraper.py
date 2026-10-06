#!/usr/bin/env python3
"""Crane Venture Partners portfolio scraper -> cranevp_companies.json
Source: https://crane.vc/portfolio — Craft CMS. Every company card is in the
server HTML but wrapped in <template> elements (revealed by JS), so the
template tags are unwrapped before parsing. Card: logo, name (h3), description,
stage label (Pre-Seed / Seed / Series A...), an "Exited" label, website link.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, round_label, is_social

SOURCE_URL = "https://crane.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "cranevp_companies.json")
PRIMARY = "Crane Venture Partners"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = re.sub(r"</?template[^>]*>", "", fetch(SOURCE_URL))
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for h in soup.select("h3.heading-s"):
        name = clean(h.get_text(" "))
        if not name or name.lower() in seen:
            continue
        card = h.find_parent(lambda t: t.name == "div" and "grid" in (t.get("class") or []))
        if not card:
            continue
        seen.add(name.lower())
        p = card.select_one("p.body, p[class*=body]")
        desc = clean(p.get_text(" ")) if p else None
        labels = [clean(l.get_text()) for l in card.select("p.label-s") if clean(l.get_text())]
        exited = "Exited" in labels
        stage_raw = next((l for l in labels if l != "Exited"), None)
        site = None
        for a in card.select("a[href^='http']"):
            if "website" in (a.get("aria-label") or "").lower() and not is_social(a["href"]):
                site = a["href"].strip()
                break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "status": None,
            "site_status": "Exited" if exited else None,
            "stage": round_label(stage_raw),
            "investment_stage_raw": stage_raw,
            "everywhere_tags": tags_for(name, desc, []),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "site_status", "stage", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
