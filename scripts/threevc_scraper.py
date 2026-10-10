#!/usr/bin/env python3
"""3VC portfolio scraper -> threevc_companies.json
Source: https://three.vc/portfolio/ — server-rendered grid of company cards
(one-line description, name, "Alumni" badge for former holdings) linking to
/portfolio/<slug>/ pages whose rich text links the company website.
status: "Acquired by X in YYYY" in 3VC's copy -> acquired (+acquirer,
exit_year); other alumni kept as site_status only; current -> active.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, is_social, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://three.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "threevc_companies.json")
PRIMARY = "3VC"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed against 3VC's copy (no LLM)
    "Aderis": ["FinTech / Insurance"],
    "Ahead Health": ["Health"],
    "Ordio": ["Future of Work"],
    "Emmi AI": ["Deeptech / Robotics / AR/VR"],
    "Stelia": ["Dev Tools / Cloud"],
    "fundcraft": ["FinTech / Insurance"],
    "Fynk": ["RegTech/Gov/Legal", "Future of Work"],
    "simpleclub": ["Future of Work"],
    "The Brief": ["Gaming / Media / Entertainment"],
    "Circeus": ["Dev Tools / Cloud"],
    "Pactum": ["Future of Work", "Logistics / Supply Chain"],
    "Avi Medical": ["Health"],
    "Picsart": ["Gaming / Media / Entertainment", "Consumer"],
    "Lokalise": ["Dev Tools / Cloud"],
    "Storyblok": ["Dev Tools / Cloud"],
    "Assaia": ["Transportation / Mobility"],
    "Kaia Health": ["Health"],
    "DGG": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Jodel": ["Consumer", "Gaming / Media / Entertainment"],
    "Tatum": ["Web3 / Crypto", "Dev Tools / Cloud"],
    "Nethone": ["Cybersecurity", "FinTech / Insurance"],
    "DeepCode": ["Dev Tools / Cloud"],
    "Gamee": ["Gaming / Media / Entertainment"],
    "Authenteq": ["Cybersecurity", "RegTech/Gov/Legal"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards, seen = [], set()
    for a in soup.select('a[href^="/portfolio/"]'):
        href = urljoin(SOURCE_URL, a["href"])
        if href.rstrip("/") == SOURCE_URL.rstrip("/") or href in seen:
            continue
        card = a.find_parent("div", class_="group")
        if not card:
            continue
        seen.add(href)
        strs = [clean(x) for x in card.stripped_strings if clean(x)]
        alumni = "Alumni" in strs
        strs = [x for x in strs if x != "Alumni"]
        name = strs[-1] if strs else None
        blurb = strs[0] if len(strs) > 1 else None
        cards.append((href, name, blurb, alumni))
    if limit:
        cards = cards[:limit]
    pages = fetch_many([c[0] for c in cards], workers=6)
    out = []
    for href, name, blurb, alumni in cards:
        body = site = None
        html = pages.get(href)
        if html:
            d = BeautifulSoup(html, "html.parser")
            rt = d.select(".body-element-richtext")
            if rt:
                body = clean(" ".join(p.get_text(" ") for p in rt[0].select("p"))) or None
                for a in rt[0].select("a[href^=http]"):
                    if not is_social(a["href"]) and "three.vc" not in urlparse(a["href"]).netloc:
                        site = a["href"]
                        break
        m = re.search(r"Acquired by (.+?) in ((?:19|20)\d{2})", blurb or "")
        desc = body or blurb
        # keep the linked site only when its domain carries the company name
        norm = lambda x: re.sub(r"[^a-z0-9]", "", (x or "").lower())
        link_on_site = site
        if site and norm(name)[:4] not in norm(urlparse(site).netloc):
            site = None
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": blurb,
            "company_url": clean_url(site),
            "link_on_site": link_on_site if link_on_site != site else None,
            "site_status": "Alumni" if alumni else "Current",
            "acquirer": clean(m.group(1)) if m else None,
            "exit_year": int(m.group(2)) if m else None,
            "status": "acquired" if m else (None if alumni else "active"),
            "everywhere_tags": tags_for(name, blurb or desc or "", [], SECTOR_TAG_MAP),
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
