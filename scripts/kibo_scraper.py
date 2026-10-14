#!/usr/bin/env python3
"""Kibo Ventures portfolio scraper -> kibo_companies.json
Source: https://kiboventures.com/portfolio/ — Webflow CMS .porfolio-item (hidden
data fields: name, fund [Kibo Ventures / Kibo Nzyme], acquirer, date; visible
"Acquired by" / "We tried" badges; website link). Descriptions are not on the index.
The per-company date is unlabeled on the site; it tracks investment timing (e.g.
Sorare / Belvo 2021, Job&Talent 2012) and is kept as `first_invested`.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides,
                             carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://kiboventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kibo_companies.json")
PRIMARY = "Kibo Ventures"
TAG_OVERRIDES = {
    "Dental Iberica": ["Health", "Consumer"],
    "Equinvest": ["Health"],
    "RB soluciones": ["RegTech/Gov/Legal"],
    "Azenea": ["RegTech/Gov/Legal", "FinTech / Insurance"],
    "Fermat": ["Consumer", "Dev Tools / Cloud"],
    "Fossa Systems": ["Deeptech / Robotics / AR/VR"],
    "Bipi": ["Transportation / Mobility", "Consumer"],
    "Frenetic": ["Deeptech / Robotics / AR/VR"],
    "Exoticca": ["Consumer"],
    "Evernest": ["PropTech"],
    "Worldsensing": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Tappx": ["Gaming / Media / Entertainment"],
    "Rewardsweb": ["Consumer", "FinTech / Insurance"],
    "Qustodio": ["Consumer", "Cybersecurity"],
    "Qida": ["Health"],
    "PromoFarma": ["Health", "Consumer"],
    "Sorare": ["Gaming / Media / Entertainment", "Web3 / Crypto"],
    "Game Strategies": ["Future of Work", "Gaming / Media / Entertainment"],
    "Apartum": ["PropTech", "Consumer"],
    "KD": ["Deeptech / Robotics / AR/VR"],
    "HyperSpectral": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Hole19": ["Consumer"],
    "Green Eagle": ["Climate / Sustainability"],
    "GoTrade": ["FinTech / Insurance", "Consumer"],
    "Defined AI": ["Data & Analytics"],
    "Clarity AI": ["FinTech / Insurance", "Climate / Sustainability", "Data & Analytics"],
    "Captio": ["FinTech / Insurance", "Future of Work"],
    "Billin": ["FinTech / Insurance"],
    "Plenit": ["Dev Tools / Cloud"],
    "Cala": ["Data & Analytics"],
    "Theker Robotics": ["Deeptech / Robotics / AR/VR"],
    "Anyformat": ["Dev Tools / Cloud", "Data & Analytics"],
    "Gamestry": [],
}


def iso_date(s):
    try:
        return datetime.strptime(clean(s), "%B %d, %Y").date().isoformat()
    except (TypeError, ValueError):
        return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".porfolio-item"):
        def g(k):
            el = it.select_one(f'[porfolio="{k}"]')
            return clean(el.get_text(" ")) if el else None
        name = g("dataname")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        badges = [clean(t.get_text(" ")) for t in it.select(".acquired-tag")
                  if "w-condition-invisible" not in (t.get("class") or [])]
        badges = [b for b in badges if b]
        acq_txt = g("datastatus")
        ipo = any("ipo" in b.lower() for b in badges)
        acquired = (not ipo) and any("acquired by" in b.lower() for b in badges)
        tried = any(b.lower() == "we tried" for b in badges)
        acquirer = re.sub(r"(?i)^acquired by\s*", "", acq_txt).strip() if acquired and acq_txt else None
        a = it.select_one("a[href]")
        href = a["href"] if a else None
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href) if href and href.startswith("http") else None,
            "fund": g("dataproject"),
            "first_invested": iso_date(g("date")),
            "status": "acquired" if acquired else None,
            "acquirer": acquirer or None,
            "exit_detail": "Nasdaq IPO" if ipo else None,
            "site_status": "We tried" if tried else None,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"])
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
