#!/usr/bin/env python3
"""Blackbird Ventures portfolio scraper -> blackbird_companies.json
Source: https://www.blackbird.vc/portfolio — Webflow CMS grid, paginated via
?<hash>_page=N; cards carry only name + /portfolio/<slug> link. Each profile
page's "Company Details" block adds Year Invested, Current Stage, Category,
"About the Company" (description), the founding-team caption and a "Visit
website" link. Hidden Webflow blocks (w-condition-invisible) are dropped.
"Current Stage" is Seed / Early / Growth, or Acquired / IPO for realized
companies: Seed -> stage; Acquired -> status acquired; IPO -> status active
(listed); otherwise status null (not published).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, tags_for, label_after, year_of, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.blackbird.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "blackbird_companies.json")
PRIMARY = "Blackbird Ventures"
SECTOR_TAG_MAP = {
    "deep tech": ["Deeptech / Robotics / AR/VR"], "healthcare": ["Health"], "hardware": ["Deeptech / Robotics / AR/VR"],
    "education": ["Future of Work"], "consumer": ["Consumer"], "fintech": ["FinTech / Insurance"],
    "climate": ["Climate / Sustainability"], "web3": ["Web3 / Crypto"], "crypto": ["Web3 / Crypto"],
}
OWN = ("blackbird.vc", "thesunrise.live", "startmate.com", "youtube.com", "website-files.com")


def founders_from(caption, name):
    m = re.search(r"(?i)\bfounders?\b\s*(?:are|is|:)?\s*(.+)$", caption or "")
    if not m:
        return []
    parts = re.split(r",\s*|\s+and\s+|\s*&\s*", m.group(1).strip(" ."))
    return [clean(p) for p in parts if clean(p) and len(p.split()) <= 4 and not re.search(r"\d", p)]


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Applied": ["Data & Analytics", "Future of Work"],
    "Culture Amp": ["Future of Work"],
    "Cyble": ["Cybersecurity"],
    "EnergyBank": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Instant": ["Consumer", "Future of Work"],
    "Nura": ["Consumer", "Deeptech / Robotics / AR/VR"],
    "OpenStar": ["Deeptech / Robotics / AR/VR", "Climate / Sustainability"],
    "Spice AI": ["Dev Tools / Cloud", "Data & Analytics"],
    "Vexev": ["Health"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".portfolio-item_block"):
            a = it.select_one("a.portfolio-item_wrapper[href]")
            nm = it.select_one(".text-colour-white")
            name = clean(nm.get_text(" ")) if nm else None
            if not a or not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            rows.append((name, urljoin(SOURCE_URL, a["href"])))
    if limit:
        rows = rows[:limit]
    details = fetch_many([h for _, h in rows])
    out = []
    for name, href in rows:
        url = desc = year = stage_raw = cat = caption = None
        html = details.get(href)
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for inv in ds.select(".w-condition-invisible"):
                inv.decompose()
            st = [s.strip() for s in ds.stripped_strings]
            try:
                i = st.index("Back To Portfolio")
            except ValueError:
                i = 0
            st = st[i:]
            year = year_of(label_after(st, "Year Invested"))
            stage_raw = label_after(st, "Current Stage")
            cat = label_after(st, "Category")
            desc = clean(label_after(st, "About the Company"))
            caption = label_after(st, "Founding Team")
            for x in ds.select("a[href^=http]"):
                if "website" in x.get_text(" ").lower():
                    u = clean_url(x["href"])
                    if u and not any(o in u for o in OWN):
                        url = u
                        break
        sectors = [cat] if cat else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "company_profile_url": href,
            "first_invested": year,
            "current_stage": stage_raw,
            "stage": stage_label(stage_raw),
            "status": {"acquired": "acquired", "ipo": "active"}.get((stage_raw or "").lower()),
            "founders": founders_from(caption, name),
            "founding_team_caption": caption,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "first_invested", "stage", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
