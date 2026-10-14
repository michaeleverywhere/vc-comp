#!/usr/bin/env python3
"""Five Elms Capital portfolio scraper -> fiveelms_companies.json
Source: https://www.fiveelms.com/portfolio — WP grid of a.open-ajax-modal tiles
(name, Active/Exited status, HQ location, one-line product descriptor). Company
detail pages sit behind a bot-verification wall, so websites are not collected.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.fiveelms.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fiveelms_companies.json")
PRIMARY = "Five Elms Capital"
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "UrgentIQ": ["Health"], "360Player": ["Consumer", "Health"], "AskNicely": ["Data & Analytics"], "Barti": ["Health"],
    "Digitail": ["Health"], "Fable": ["Dev Tools / Cloud"], "FMX": ["PropTech", "Future of Work"], "Granum": ["Future of Work"],
    "Gymdesk": ["Consumer", "Health"], "IntelligenceBank": ["Gaming / Media / Entertainment", "Future of Work"],
    "Lumar": ["Data & Analytics"], "Magma Math": ["Consumer"], "Opiniion": ["PropTech"], "Opus1": ["Gaming / Media / Entertainment"],
    "Practice Better": ["Health"], "Prismatic": ["Dev Tools / Cloud"], "Prospyr": ["Health", "Consumer"],
    "Reachdesk": ["Future of Work"], "Rebrandly": ["Data & Analytics"], "Ritten": ["Health"], "RoomPriceGenie": ["Consumer", "Data & Analytics"],
    "Scilife": ["BioTech", "RegTech/Gov/Legal"], "Skedda": ["PropTech", "Future of Work"], "Spacelift": ["Dev Tools / Cloud"],
    "Trybe": ["Consumer"], "Userlane": ["Future of Work"], "Vajro": ["Consumer", "Dev Tools / Cloud"],
    "AuroraXMP": ["Climate / Sustainability", "Data & Analytics"], "Catapult": ["Logistics / Supply Chain"],
    "Flywheel": ["Dev Tools / Cloud"], "GoReact": ["Future of Work"], "Hubb": ["Gaming / Media / Entertainment"],
    "LaborChart": ["Future of Work", "PropTech"], "MemberClicks": ["Future of Work"], "OnBoard": ["Future of Work"],
    "Outfit": ["Gaming / Media / Entertainment"], "Proxyclick": ["PropTech", "Cybersecurity"], "RFP360": ["Future of Work"],
    "Service Fusion": ["Future of Work", "PropTech"], "Sherpa": ["Health"], "TeamDynamix": ["Dev Tools / Cloud"],
    "Covideo": ["Future of Work"], "Pathify": ["Consumer"], "Continu": ["Future of Work"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.open-ajax-modal"):
        def f(sel):
            el = a.select_one(sel)
            return clean(el.get_text(" ")) if el else None
        name = f(".item-name") or clean(a.get("data-name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        st = (f(".item-status") or "")
        out.append({
            "company_name": name,
            "description": f(".item-grid-text"),
            "company_url": None,
            "location": f(".item-location"),
            "site_status": st or None,
            "status": "active" if st.lower() == "active" else None,
            "exited": st.lower() == "exited",
            "profile_url": a.get("href"),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"])
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
