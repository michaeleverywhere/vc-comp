#!/usr/bin/env python3
"""Amadeus Capital Partners portfolio scraper -> amadeus_companies.json
Source: https://www.amadeuscapital.com/our-companies/ — WordPress; the
`company` post type is exposed at /wp-json/wp/v2/company (66 at first
scrape) with taxonomy classes situation-current / situation-success-stories
and area-intelligence / area-human / area-planet (Amadeus's three themes).
Each /company/<slug>/ page has the name (h1), a one-line headline, the
company Website link and an About section; exits are described in the About
copy ("... was acquired by X in April 2013", "listed on ...").
status: About copy says acquired/merged into -> acquired; other success
stories kept as site_status only; current -> active.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, is_social, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.amadeuscapital.com/our-companies/"
API = "https://www.amadeuscapital.com/wp-json/wp/v2/company?per_page=100&_fields=id,slug,title,link,class_list"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "amadeus_companies.json")
PRIMARY = "Amadeus Capital Partners"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed against Amadeus's copy (no LLM)
    "Vertus Energy": ["Climate / Sustainability"],
    "HyperHeat": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "enaDyne": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Recurvia": ["Dev Tools / Cloud"],
    "Ciphergen Biosystems": ["BioTech", "Health"],
    "Entropic": ["Deeptech / Robotics / AR/VR"],
    "VocalIQ": ["Consumer", "Deeptech / Robotics / AR/VR"],
    "Transmode": ["Deeptech / Robotics / AR/VR"],
    "Optos": ["Health"],
    "Bellco": ["Health"],
    "Aepona": ["Dev Tools / Cloud"],
    "OrganOx": ["Health"],
    "Tobii": ["Deeptech / Robotics / AR/VR", "Consumer"],
    "Ravelin": ["Cybersecurity", "FinTech / Insurance"],
    "Paragraf": ["Deeptech / Robotics / AR/VR"],
    "Openbravo": ["Dev Tools / Cloud", "Consumer"],
    "Igenomix": ["Health", "BioTech"],
    "ContactEngine": ["Future of Work"],
    "SandboxAQ": ["Deeptech / Robotics / AR/VR", "Cybersecurity"],
    "Unlikely AI": ["Deeptech / Robotics / AR/VR"],
    "Creditas": ["FinTech / Insurance"],
    "Secondmind": ["Transportation / Mobility", "Data & Analytics"],
    "Gemesys": ["Deeptech / Robotics / AR/VR"],
    "iPronics": ["Deeptech / Robotics / AR/VR"],
    "Photonic": ["Deeptech / Robotics / AR/VR"],
    "planqc": ["Deeptech / Robotics / AR/VR"],
    "Nu Quantum": ["Deeptech / Robotics / AR/VR"],
    "Riverlane": ["Deeptech / Robotics / AR/VR"],
    "Safe Intelligence": ["Dev Tools / Cloud", "Cybersecurity"],
    "RoboK": ["Transportation / Mobility", "Deeptech / Robotics / AR/VR"],
    "Pimloc": ["Cybersecurity", "RegTech/Gov/Legal"],
    "Quibim": ["Health", "Data & Analytics"],
    "Xampla": ["Climate / Sustainability", "CPG"],
    "XYZ Reality": ["PropTech", "Deeptech / Robotics / AR/VR"],
    "UniSieve": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Stateful Robotics": ["Deeptech / Robotics / AR/VR"],
    "Natrox": ["Health"],
    "Doctify": ["Health"],
    "Charco Neurotech": ["Health"],
    "Oxford Nanopore Technologies": ["BioTech", "Health"],
}
# exit sentences about the company itself ("X was acquired by Y in May 2011",
# "It was acquired by Y for $400m in 2015", "they were acquired by Y");
# descriptors before the acquirer's name ("US-based", "French enterprise
# software company") are skipped. A start-up "acquired by" without was/were
# (e.g. a founder's earlier company) is ignored.
ACQ = re.compile(r"\b(?:was|were)\s+(?:later\s+)?acquired by\s+(?:[\w\-]+-based\s+)?(?:(?:[a-z][\w\-]*\s+)*?(?:[A-Z][a-z]+\s+)?(?:enterprise\s+)?(?:software\s+)?company\s+)?((?:[A-Z][\w&.\-]*)(?:\s+(?:[A-Z][\w&.\-]*|&))*)")
YEAR_IN = re.compile(r"\b[Ii]n\s+(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+)?((?:19|20)\d{2})")
IPO = re.compile(r"\b(?:floated on|went public|completed its IPO|listed on|was listed)\b")


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    rows = fetch(API, as_json=True)
    if limit:
        rows = rows[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = fetch_many([r["link"] for r in rows], workers=6)
    out = []
    for r in rows:
        cls = r.get("class_list") or []
        situation = next((c.split("situation-", 1)[1] for c in cls if c.startswith("situation-")), None)
        areas = [c.split("area-", 1)[1].title() for c in cls if c.startswith("area-")]
        html = pages.get(r["link"])
        name = clean(BeautifulSoup(r["title"]["rendered"], "html.parser").get_text(" "))
        tagline = about = site = None
        if html:
            d = BeautifulSoup(html, "html.parser")
            h1 = d.select_one("h1")
            if h1:
                name = clean(h1.get_text(" ")) or name
                nxt = h1.find_next("p")
                tagline = clean(nxt.get_text(" ")) if nxt else None
            ab = d.find(lambda t: t.name in ("h2", "h3") and clean(t.get_text(" ")) == "About")
            if ab:
                p = ab.find_next("p")
                about = clean(p.get_text(" ")) if p else None
                # website link sits in the header block above "About"
                for a in ab.find_all_previous("a", href=True):
                    href = a["href"]
                    host = urlparse(href).netloc.lower()
                    if href.startswith("http") and "amadeuscapital.com" not in host and not is_social(href):
                        site = href
                        break
        text = " ".join(x for x in (about, tagline) if x)
        acquirer = exit_year = None
        ipo = False
        for sent in re.split(r"(?<=[.!?])\s+", " ".join(x for x in (tagline, about) if x)):
            m = ACQ.search(sent)
            if m and not acquirer:
                acquirer = clean(re.sub(r"\.$", "", m.group(1)))
                y = YEAR_IN.search(sent[m.start():]) or YEAR_IN.search(sent)
                exit_year = int(y.group(1)) if y else None
            if IPO.search(sent):
                ipo = True
        site_status = {"current": "Current", "success-stories": "Success Stories"}.get(situation, situation)
        out.append({
            "company_name": name,
            "description": about or tagline,
            "tagline": tagline,
            "company_url": clean_url(site),
            "areas": areas,
            "site_status": site_status,
            "acquirer": acquirer,
            "exit_year": exit_year,
            "ipo_listed": ipo or None,
            "status": "acquired" if acquirer else ("active" if situation == "current" else None),
            "everywhere_tags": tags_for(name, tagline or about or "", [], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": r["link"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "tagline", "company_url", "areas", "site_status", "status", "acquirer", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
