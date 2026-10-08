#!/usr/bin/env python3
"""Seaya portfolio scraper -> seaya_companies.json
Source: https://seaya.vc/portfolio/ — WordPress (Salient portfolio grid),
server-rendered. Each card: name, tagline and data-project-cat classes
(themes, active / exited, fund: Seaya Ventures / Seaya Andromeda). Each
/portfolio/<slug>/ page adds the description and a fact block: HQ, BORN IN
(country), FOUNDERS, WEBSITE, SECTOR, STATUS (Current / Exited ...).
No funding round or investment year is published.
Status: Current / Active -> active; "Acquired by X" / Exited -> acquired;
"Public company (...)" left blank (raw kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, first_external_link, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://seaya.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "seaya_companies.json")
PRIMARY = "Seaya"
OWN = ("seaya.vc", "legalsending.com", "wsc.design")
SECTOR_TAG_MAP = {
    "energy transition": ["Climate / Sustainability"], "sustainability": ["Climate / Sustainability"],
    "intelligent health": ["Health"], "autonomous finance": ["FinTech / Insurance"], "fintech": ["FinTech / Insurance"],
    "adaptive commerce": ["Consumer"], "supply chain": ["Logistics / Supply Chain"], "security": ["Cybersecurity"],
    "tech infrastructure": ["Dev Tools / Cloud"], "future of industry": ["Deeptech / Robotics / AR/VR"],
    "food": ["CPG"], "mobility": ["Transportation / Mobility"], "proptech": ["PropTech"], "health": ["Health"],
}
STATUS = {"current": "active", "active": "active", "exited": "acquired", "exit": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Clarity AI": ["Climate / Sustainability", "Data & Analytics"],
    "Movilia": ["Transportation / Mobility"],
    "RatedPower": ["Climate / Sustainability", "Dev Tools / Cloud"],
    "Robin Food": ["Consumer"],
    "Sensei": ["Consumer", "Deeptech / Robotics / AR/VR"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards, seen = [], set()
    for it in soup.select("div.element[data-project-cat]"):
        h = it.select_one(".work-meta h4")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        p = it.select_one(".work-meta p")
        a = it.select_one(".work-info a[href]")
        cats = (it.get("data-project-cat") or "").split()
        cards.append(dict(name=name, tagline=clean(p.get_text(" ")) if p else None, prof=a["href"] if a else None, cats=cats))
        if limit and len(cards) >= limit:
            break
    details = fetch_many([c["prof"] for c in cards if c["prof"]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for c in cards:
        desc = site = hq = born = sector = raw_status = None
        founders = []
        h = details.get(c["prof"])
        if h:
            s = BeautifulSoup(h, "html.parser")
            site = clean_url(first_external_link(s, OWN))
            for t in s(["script", "style", "svg", "nav", "footer", "header", "form"]):
                t.decompose()
            st = [clean(x) for x in s.body.stripped_strings if clean(x)]
            if "HQ" in st:
                pre = st[:st.index("HQ")]
                paras = [x for x in pre if len(x) > 40]
                desc = " ".join(paras[:2]) or None
            hq = label_after(st, "HQ")
            born = label_after(st, "BORN IN")
            sector = label_after(st, "SECTOR")
            raw_status = label_after(st, "STATUS")
            f = label_after(st, "FOUNDERS")
            founders = [clean(x) for x in re.split(r",| and | & | y ", f or "") if clean(x)]
        if not raw_status:
            raw_status = "Exited" if "exited" in c["cats"] else ("Active" if "active" in c["cats"] else None)
        loc = ", ".join(x for x in (hq, born) if x and x != hq or x == hq) if hq or born else None
        if hq and born and born.lower() not in hq.lower():
            loc = f"{hq}, {born}"
        else:
            loc = hq or born
        sectors = [sector] if sector else []
        acq = re.match(r"(?i)ac+quired by\s+(.+)", raw_status or "")
        status = "acquired" if acq else STATUS.get((raw_status or "").lower())
        out.append({
            "company_name": c["name"],
            "description": desc or c["tagline"],
            "tagline": c["tagline"],
            "company_url": site,
            "company_profile_url": c["prof"],
            "status": status,
            "site_status": raw_status,
            "acquirer": clean(re.sub(r"\s*\(.*\)$", "", acq.group(1))) if acq else None,
            "location": loc,
            "founders": founders,
            "sectors": sectors,
            "funds": [x for x in ("Seaya Ventures" if "2-seaya-ventures" in c["cats"] else None,
                                   "Seaya Andromeda" if "1-seaya-andromeda" in c["cats"] else None) if x],
            "everywhere_tags": tags_for(c["name"], " ".join(x for x in (c["tagline"], desc) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
