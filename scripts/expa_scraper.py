#!/usr/bin/env python3
"""Expa portfolio scraper -> expa_companies.json
Source: https://www.expa.com/companies — server-rendered page; one
<article class="portfolio__company"> per company with name (h3), tagline,
long description, and an info list (Founder(s) / CEO / Leadership, Website,
X, Location). No stage or investment year is published.
Status: Expa states exits in the description prose ("Acquired by X." /
"... was acquired by X in YYYY") -> status acquired + acquirer; everything
else is left blank (no active label on the site).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.expa.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "expa_companies.json")
PRIMARY = "Expa"
PEOPLE = {"founder", "founders", "co-founders", "founding team", "ceo", "leadership"}
ACQ_RX = re.compile(r"\b(?:was |were )?acquired by ([A-Z0-9][\w&.'’\- ]+?)(?: in ((?:19|20)\d{2}))?(?:[,.;]|$| and )")

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "ATC": [
        "PropTech",
        "Data & Analytics"
    ],
    "Airly": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Airwork": [
        "Future of Work"
    ],
    "Allosense": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
    "Aument": [
        "Data & Analytics"
    ],
    "Beacon": [
        "Logistics / Supply Chain",
        "FinTech / Insurance"
    ],
    "BlueCargo": [
        "Logistics / Supply Chain"
    ],
    "Bondaval": [
        "FinTech / Insurance"
    ],
    "Cascade": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Certification": [
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "Circus": [
        "Gaming / Media / Entertainment",
        "Future of Work"
    ],
    "Clau": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "Clyde": [
        "FinTech / Insurance",
        "Consumer"
    ],
    "Cmd": [
        "Cybersecurity",
        "Dev Tools / Cloud"
    ],
    "Collective": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Commons": [
        "Climate / Sustainability",
        "Consumer"
    ],
    "Convoy": [
        "Logistics / Supply Chain"
    ],
    "Dadi": [
        "Health",
        "Consumer"
    ],
    "Dovetale": [
        "Gaming / Media / Entertainment"
    ],
    "Every.org": [
        "FinTech / Insurance"
    ],
    "Fabric": [
        "Dev Tools / Cloud",
        "Consumer"
    ],
    "Felux": [
        "Logistics / Supply Chain"
    ],
    "Findigs": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "First": [
        "RegTech/Gov/Legal",
        "Consumer"
    ],
    "Gather AI": [
        "Logistics / Supply Chain",
        "Deeptech / Robotics / AR/VR"
    ],
    "Genie": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Hallo": [
        "Future of Work"
    ],
    "Iconic": [
        "FinTech / Insurance"
    ],
    "Katoo": [
        "Logistics / Supply Chain",
        "CPG"
    ],
    "Kickoff": [
        "Health",
        "Consumer"
    ],
    "Kit": [
        "Consumer"
    ],
    "Kit Health": [
        "Health"
    ],
    "Kolors": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Layer": [
        "Gaming / Media / Entertainment"
    ],
    "Loop": [
        "Logistics / Supply Chain",
        "FinTech / Insurance"
    ],
    "MainVest": [
        "FinTech / Insurance"
    ],
    "Merlin Guides": [
        "Future of Work"
    ],
    "Nibble Health": [
        "Health",
        "FinTech / Insurance"
    ],
    "Nitra": [
        "FinTech / Insurance",
        "Health"
    ],
    "Norm": [
        "RegTech/Gov/Legal"
    ],
    "OYE": [
        "Health",
        "Consumer"
    ],
    "Oliver Space": [
        "Consumer",
        "PropTech"
    ],
    "Operator": [
        "Consumer"
    ],
    "Primer": [
        "Consumer",
        "Deeptech / Robotics / AR/VR"
    ],
    "Prometheus": [
        "Climate / Sustainability"
    ],
    "Radar": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Reserve": [
        "Consumer"
    ],
    "Seven Starling": [
        "Health"
    ],
    "ShareWillow": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Sleeper": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Smartrr": [
        "Consumer"
    ],
    "Solo": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Spatial": [
        "Deeptech / Robotics / AR/VR",
        "Future of Work"
    ],
    "Spot": [
        "Consumer"
    ],
    "Statespace": [
        "Gaming / Media / Entertainment"
    ],
    "SuperHi": [
        "Future of Work"
    ],
    "Torch": [
        "Health",
        "Data & Analytics"
    ],
    "Trackd": [
        "Cybersecurity"
    ],
    "Twelve Labs": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "Wingcopter": [
        "Logistics / Supply Chain",
        "Deeptech / Robotics / AR/VR",
        "Health"
    ],
    "zeroheight": [
        "Dev Tools / Cloud"
    ],
    "Atro": [
        "Cybersecurity"
    ],
    "Mix": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Aero": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Current": [
        "FinTech / Insurance"
    ],
    "Detect": [
        "Health",
        "BioTech"
    ],
    "Consider": [
        "Future of Work"
    ],
    "Knock": [
        "Dev Tools / Cloud"
    ],
    "Pin": [
        "Future of Work"
    ],
    "Proper": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "Range": [
        "FinTech / Insurance"
    ],
    "Supermassiv": [
        "Web3 / Crypto",
        "Gaming / Media / Entertainment"
    ],
    "Yumi": [
        "CPG",
        "Consumer"
    ],
    "Shift": [
        "Future of Work"
    ],
    "Physera": [
        "Health"
    ],
    "Interseller": [
        "Future of Work"
    ],
    "Gitalytics": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for art in soup.select("article.portfolio__company"):
        h = art.select_one(".portfolio__company__title")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        tg = art.select_one(".portfolio__company__description")
        tagline = clean(tg.get_text(" ")) if tg else None
        paras = [clean(p.get_text(" ")) for p in art.select(".portfolio__company__content p")]
        paras = [p for p in paras if p]
        acquirer = exit_year = None
        body = []
        for p in paras:
            m = re.match(r"(?i)^acquired by (.+?)\.?$", p)
            if m:
                acquirer = clean(m.group(1))
                continue
            body.append(p)
        desc = " ".join(body) or None
        if not acquirer and desc:
            m = ACQ_RX.search(desc)
            if m:
                acquirer, exit_year = clean(m.group(1)), (int(m.group(2)) if m.group(2) else None)
        info, people = {}, []
        for li in art.select(".portfolio__company__information li"):
            st = li.select_one("strong")
            if not st:
                continue
            label = clean(st.get_text(" ")).lower()
            st.extract()
            val = clean(li.get_text(" "))
            a = li.select_one("a[href]")
            if label in PEOPLE and val:
                people += [clean(x) for x in re.split(r",| & | and ", val) if clean(x)]
            elif label == "website" and a:
                info["website"] = a["href"]
            elif label == "location":
                info["location"] = val
        rec = {
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(info.get("website")),
            "status": "acquired" if acquirer else None,
            "acquirer": acquirer,
            "exit_year": exit_year,
            "location": info.get("location"),
            "founders": people,
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x)),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
