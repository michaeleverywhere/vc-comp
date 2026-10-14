#!/usr/bin/env python3
"""Ten Eleven Ventures portfolio scraper -> teneleven_companies.json
Source: https://www.1011vc.com/portfolio — Webflow .companies-list_item cards
(name, Active / Acquired / IPO status tag) + detail pages (Venture/Growth tag,
description, team, Founded, Partnered year, Headquarters, website).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, label_after, year_of,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.1011vc.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "teneleven_companies.json")
PRIMARY = "Ten Eleven Ventures"
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "IQM": ["Deeptech / Robotics / AR/VR"], "Anchorage Digital": ["Web3 / Crypto", "FinTech / Insurance"],
    "Feedzai": ["FinTech / Insurance", "Cybersecurity"], "Darkhive": ["Deeptech / Robotics / AR/VR", "RegTech/Gov/Legal"],
    "BlackHorse": ["Cybersecurity", "RegTech/Gov/Legal"], "Blackbird.AI": ["Cybersecurity", "Data & Analytics"],
    "Ordr": ["Cybersecurity", "Health"], "Fivecast": ["Data & Analytics", "RegTech/Gov/Legal"],
    "Variance": ["FinTech / Insurance", "Cybersecurity"], "Caspia": ["Cybersecurity", "Deeptech / Robotics / AR/VR"],
    "Aura": ["Cybersecurity", "Consumer"], "Hypernative": ["Cybersecurity", "Web3 / Crypto"],
}
# Cybersecurity specialist: every company leads with Cybersecurity; keep at most one
# other keyword tag (drops the keyword tagger's long-tail over-tags).
SECOND_OK = ("FinTech / Insurance", "Web3 / Crypto", "Health", "Deeptech / Robotics / AR/VR", "Dev Tools / Cloud",
             "Data & Analytics", "RegTech/Gov/Legal")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".companies-list_item"):
        nm = it.select_one("[fs-list-field=name] .plain-text") or it.select_one("[fs-list-field=name]")
        name = clean(nm.get_text(" ")) if nm else None
        a = it.select_one("a[href*='/portfolio/']")
        if not name or name.lower() in seen or not a:
            continue
        seen.add(name.lower())
        st = it.select_one("[fs-list-field=status]")
        out.append({"company_name": name, "detail_url": urljoin(SOURCE_URL, a["href"]),
                    "site_status": clean(st.get_text(" ")) if st else None})
    pages = fetch_many([r["detail_url"] for r in out], workers=5, pause=0.15)
    for r in out:
        html = pages.get(r["detail_url"])
        desc = url = hq = None
        founded = partnered = None
        fund_type = None
        founders = []
        if html:
            ds = BeautifulSoup(html, "html.parser")
            m = ds.select_one("main") or ds
            tags = [clean(t.get_text()) for t in m.select(".tag-text")][:2]
            fund_type = next((t for t in tags if t in ("Venture", "Growth")), None)
            strings = list(m.stripped_strings)
            founded = year_of(label_after(strings, "Founded"))
            partnered = year_of(label_after(strings, "Partnered"))
            hq = clean(label_after(strings, "Headquarters"))
            u = m.select_one(".clip-board-link_text .plain-text")
            url = clean_url(clean(u.get_text())) if u else None
            for s in strings:
                s = clean(s)
                if s and len(s) > 80 and r["company_name"].split()[0].lower() in s.lower():
                    desc = s
                    break
        st = (r["site_status"] or "").lower()
        r.update({
            "description": desc,
            "company_url": url,
            "location": hq,
            "year_founded": founded,
            "first_invested": partnered,
            "fund_type": fund_type,
            "status": "active" if st == "active" else ("acquired" if st == "acquired" else None),
            "exit_detail": "IPO" if st == "ipo" else None,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "profile_url": r.pop("detail_url"),
            "scraped_at": scraped_at,
        })
        r["everywhere_tags"] = tags_for(r["company_name"], desc)
    prune_substring_tags(out)
    for r in out:
        rest = [t for t in r["everywhere_tags"] if t != "Cybersecurity" and t in SECOND_OK]
        r["everywhere_tags"] = ["Cybersecurity"] + rest[:1]
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
