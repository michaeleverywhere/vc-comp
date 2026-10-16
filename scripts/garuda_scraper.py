#!/usr/bin/env python3
"""Garuda Ventures portfolio scraper -> garuda_companies.json
Source: https://www.garuda.vc/portfolio — Webflow CMS `.company_info_line`
rows: company name (data-company-slug, as published), category
(data-filter="category"), tagline, status (Exited/Active), exit note
("Acq. X") and website. Placeholder "Unannounced" rows are skipped.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.garuda.vc/portfolio"
PRIMARY = "Garuda Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".company_info_line[data-company-slug]"):
        name = clean(it["data-company-slug"])
        if not name or name.lower().startswith("unannounced"):
            continue
        cat = it.select_one("[data-filter='category']")
        st = it.select_one("[data-filter='status']")
        logo_tag = it.select_one(".logo_wrap .company_tag")
        tagline = None
        for t in it.select(".company_tag"):
            if t is cat or t is logo_tag or "display-none" in (t.get("class") or []):
                continue
            tagline = clean(t.get_text(" ", strip=True))
        a = it.select_one("a.absolute_clickable[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        stt = clean(st.get_text(" ", strip=True)) if st else None
        exit_note = clean(logo_tag.get_text(" ", strip=True)) if logo_tag else None
        out.append(rec(name, tagline, href, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[clean(cat.get_text(" ", strip=True))] if cat else [], portfolio_status=stt,
                       status={"exited": "exited", "active": "active"}.get((stt or "").lower()), exit_note=exit_note))
    finish(out, "garuda", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
