#!/usr/bin/env python3
"""Grove Ventures portfolio scraper -> grove_companies.json
Source: https://www.grovevc.com/grove-portfolio-companies/ — server-rendered
WordPress grid. Each `div.portfolio-box` carries the company name as its extra
CSS class tokens (logos have empty alts), a one-line description, category ids
(data-category, resolved through the filter list's data-term labels), and an
"Acquired" badge; the acquirer is usually only a logo, so it is kept only when
written as text ("Acquired (by Itamar Medical)").
"Stealth" cards are skipped: their class tokens are placeholder labels such as
"Energy Tech" or "Edge & IoT", not company names. The per-company
/portfolio/<slug>/ pages sit behind a WAF block, so no websites, stages or
dates are captured.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.grovevc.com/grove-portfolio-companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "grove_companies.json")
PRIMARY = "Grove Ventures"
SKIP_CLASSES = {"portfolio-box", "no-hover-text"}
SECTOR_TAG_MAP = {
    "infra & dev tools": ["Dev Tools / Cloud"], "data center & compute": ["Deeptech / Robotics / AR/VR"],
    "energy": ["Climate / Sustainability"], "bio & healthcare": ["Health"], "semiconductors": ["Deeptech / Robotics / AR/VR"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Wiliot": [
        "Deeptech / Robotics / AR/VR",
        "Logistics / Supply Chain"
    ],
    "Alice": [
        "Cybersecurity",
        "Gaming / Media / Entertainment"
    ],
    "Teramount": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Majestic Labs": [
        "Deeptech / Robotics / AR/VR"
    ],
    "NeuroBlade": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "Mirato": [
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "Quantum Source": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Limitless Labs": [
        "Deeptech / Robotics / AR/VR",
        "Future of Work"
    ],
    "Lava": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "FormX": [
        "PropTech"
    ],
    "Niv-AI": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Enzymit": [
        "BioTech"
    ],
    "Unifabrix": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Particula": [
        "Deeptech / Robotics / AR/VR"
    ],
    "3d Signals": [
        "Deeptech / Robotics / AR/VR",
        "Data & Analytics"
    ],
    "Scala Biodesign": [
        "BioTech"
    ],
    "Protai": [
        "BioTech"
    ],
    "Nucleai": [
        "Health",
        "BioTech"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    terms = {a["data-term"]: clean(a.get_text(" ")) for a in soup.select("a[data-term]")}
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for b in soup.select("div.portfolio-box"):
        badge = clean(b.select_one(".portfolio-badge").get_text(" ")) if b.select_one(".portfolio-badge") else None
        if badge and badge.lower().startswith("stealth"):
            continue
        name = clean(" ".join(c for c in b.get("class", []) if c not in SKIP_CLASSES))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        dd = b.select_one(".portfolio-short-desc")
        desc = clean(dd.get_text(" ")) if dd else None
        sectors = [terms[t] for t in (b.get("data-category") or "").split(",") if t.strip() in terms]
        acq_txt = clean(b.select_one(".acquired-by").get_text(" ")) if b.select_one(".acquired-by") else None
        m = re.search(r"(?i)by\s+([^)]+)\)?", acq_txt or "")
        acquired = bool(badge and "acquired" in badge.lower())
        a = b.find("a", href=True)
        out.append({
            "company_name": name,
            "description": desc,
            "company_profile_url": urljoin(SOURCE_URL, a["href"]) if a else None,
            "status": "acquired" if acquired else None,
            "site_status": badge,
            "acquirer": clean(m.group(1)) if (acquired and m and clean(m.group(1))) else None,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc or "", sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "status", "acquirer", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
