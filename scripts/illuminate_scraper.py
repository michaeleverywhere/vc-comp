#!/usr/bin/env python3
"""Illuminate Ventures portfolio scraper -> illuminate_companies.json
Source: https://illuminate.com/portfolio-2/ — WordPress isotope grid of
/projects/<slug>/ links; each card's CSS class says `current` or `exited`.
Each project page has the company copy (the first link in the copy is the
company website, its text the current company name) and, for exits, an
"Acquired by <X> <Month, Year>" line. status: "Acquired by" -> acquired,
other exits kept as site_status only; current -> active.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://illuminate.com/portfolio-2/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "illuminate_companies.json")
PRIMARY = "Illuminate Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed against the firm's copy (no LLM)
    "Allocadia": ["Data & Analytics", "Future of Work"],
    "Arkestro": ["Logistics / Supply Chain", "Data & Analytics"],
    "Bedrock Analytics": ["Data & Analytics", "CPG"],
    "Birdie": ["Data & Analytics", "Consumer"],
    "Brevity": ["Future of Work"],
    "BrightEdge": ["Data & Analytics", "Gaming / Media / Entertainment"],
    "CafeX": ["Future of Work", "RegTech/Gov/Legal"],
    "Contentstack": ["Dev Tools / Cloud", "Gaming / Media / Entertainment"],
    "Continual AI": ["Dev Tools / Cloud", "Data & Analytics"],
    "Hoopla.net": ["Future of Work"],
    "Influitive": ["Gaming / Media / Entertainment", "Future of Work"],
    "Intelo.ai": ["Data & Analytics", "Logistics / Supply Chain"],
    "IP Author": ["RegTech/Gov/Legal"],
    "Jacobi": ["FinTech / Insurance", "Data & Analytics"],
    "JetStream Software": ["Dev Tools / Cloud"],
    "Joinder": ["RegTech/Gov/Legal", "Future of Work"],
    "Labra": ["Dev Tools / Cloud"],
    "mpathic": ["Dev Tools / Cloud", "Data & Analytics"],
    "Opsmatic": ["Dev Tools / Cloud"],
    "Perceptive Panda": ["Data & Analytics", "Future of Work"],
    "Perceptix": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "PEX": ["Gaming / Media / Entertainment", "RegTech/Gov/Legal"],
    "Provarity": ["Future of Work", "Data & Analytics"],
    "Pyze": ["Data & Analytics", "Dev Tools / Cloud"],
    "Red Aril": ["Data & Analytics", "Gaming / Media / Entertainment"],
    "Sense Platform": ["Data & Analytics", "Dev Tools / Cloud"],
    "TAZI.AI": ["Data & Analytics", "Dev Tools / Cloud"],
    "Wild Pockets": ["Gaming / Media / Entertainment", "Deeptech / Robotics / AR/VR"],
    "Xactly": ["Future of Work", "Data & Analytics"],
    "CalmSea": ["Consumer", "Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = {}
    for it in soup.select(".project-item"):
        a = it.select_one('a[href*="/projects/"]')
        if not a:
            continue
        cls = it.get("class") or []
        cards.setdefault(a["href"], "Exited" if "exited" in cls else ("Current" if "current" in cls else None))
    hrefs = list(cards)[:limit] if limit else list(cards)
    pages = fetch_many(hrefs, workers=6)
    out = []
    for href in hrefs:
        html = pages.get(href)
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        title = clean(d.title.get_text(" ")) if d.title else None
        title_name = clean(title.split("|")[0]) if title else None
        c = d.select_one(".entry-content")
        paras = [clean(p.get_text(" ")) for p in c.select("p")] if c else []
        paras = [p for p in paras if p]
        first_a = c.select_one("p a[href^=http]") if c else None
        link_name = clean(re.sub(r"[’‘']s?$", "", first_a.get_text(" ").strip())) if first_a else None
        site = first_a["href"] if first_a else None
        norm = lambda x: re.sub(r"[^a-z0-9]", "", (x or "").lower())
        first_para = paras[0] if paras else ""
        # the copy opens with the company's own (linked) name; page titles sometimes
        # carry the acquirer's or a shortened name instead
        name = link_name if link_name and len(link_name) < 40 and first_para.startswith(link_name) else (title_name or link_name)
        # the linked site is the company's own only when its domain carries the name
        # (on some exited pages it points at the acquirer instead)
        if site and norm(name)[:4] not in norm(re.sub(r"^https?://(www\.)?", "", site).split("/")[0]):
            site = None
        acq_line = next((p for p in paras if re.search(r"(^acquired by|[–-] acquired)", p, re.I)), None)
        acquirer = acq_year = acquirer_ticker = None
        if acq_line:
            m = re.match(r"Acquired by (.+?)(?:\s+\(.*?\))?(?:\s+in)?\s*(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*)?((?:19|20)\d{2})?\.?$", acq_line)
            if m:
                acquirer, acq_year = clean(m.group(1)), m.group(2)
            else:
                m = re.search(r"[–-] Acquired \((.+?)\)", acq_line)
                if m:
                    acquirer_ticker = clean(m.group(1))  # site gives the acquirer's ticker only
        MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
        m2 = re.search(r"([A-Z][\w.]+(?: [A-Z][\w.]+)?) acquired by (.+?) (?:%s),?\s*((?:19|20)\d{2})" % MONTHS, " ".join(paras))
        if m2 and not acquirer and title_name and clean(m2.group(2)) == title_name:
            # page is titled after the acquirer (e.g. CalmSea -> Coupang)
            name, acquirer, acq_year = clean(m2.group(1)), clean(m2.group(2)), m2.group(3)
            acq_line = clean(m2.group(0))
            site = None
            paras = [clean(p.replace(m2.group(0), "")) for p in paras]
            paras = [p for p in paras if p and not re.match(r"%s IPO" % re.escape(title_name), p)]
        desc_paras = [p for p in paras if p != acq_line and not re.match(r"(Acquired by|Learn more|Interested in|Read more|Merged with|IPO)", p, re.I)]
        desc = " ".join(desc_paras) or None
        site_status = cards[href]
        out.append({
            "company_name": name,
            "former_name": None if acquirer == title_name else title_name if title_name and name and title_name.lower() != name.lower() else None,
            "description": desc,
            "company_url": clean_url(site),
            "site_status": site_status,
            "exit_note": acq_line,
            "acquirer": acquirer,
            "exit_year": int(acq_year) if acq_year else None,
            "acquirer_ticker": acquirer_ticker,
            "status": "acquired" if (acquirer or acquirer_ticker) else ("active" if site_status == "Current" else None),
            "everywhere_tags": tags_for(name, desc or "", [], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": href,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "site_status", "status", "acquirer", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
