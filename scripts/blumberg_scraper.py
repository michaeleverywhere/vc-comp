#!/usr/bin/env python3
"""Blumberg Capital portfolio scraper -> blumberg_companies.json
Source: https://blumbergcapital.com/portfolio-companies/ — WordPress (Beaver
Builder post grid of the `avada_portfolio` type, 114 at first scrape). Each
card carries the name, an "Acquired" or "IPO" badge when exited, and a
fund_type class (early-stage / venture-growth). Each company page has the
name (h1), a one-line description (h4.short-description), long copy and
the company website / social links.
status: "Acquired" badge -> acquired; "IPO" kept in exit_type (the site does
not say whether the company is still listed); otherwise active.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, is_social, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://blumbergcapital.com/portfolio-companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "blumberg_companies.json")
PRIMARY = "Blumberg Capital"
INTRO = "We are proud to be among the first investors"
SKIP_HOSTS = ("blumbergcapital.com", "addtoany.com")
FOOTER = re.compile(r"Collins Avenue|Sunny Isles|Bryant Street|^Miami\b|All rights reserved|Privacy Policy", re.I)
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed against Blumberg's copy (no LLM)
    "AiStrike": ["Cybersecurity"],
    "Hunters.AI": ["Cybersecurity"],
    "Prescient AI": ["Data & Analytics", "Consumer"],
    "Anchor Browser": ["Dev Tools / Cloud"],
    "Any.Do": ["Consumer", "Future of Work"],
    "FirmPilot": ["RegTech/Gov/Legal", "Future of Work"],
    "Fundbox": ["FinTech / Insurance"],
    "FundGuard": ["FinTech / Insurance"],
    "Hydrolix": ["Data & Analytics", "Dev Tools / Cloud"],
    "Nexla": ["Data & Analytics", "Dev Tools / Cloud"],
    "Snorkel AI": ["Data & Analytics", "Dev Tools / Cloud"],
    "SigOpt": ["Dev Tools / Cloud", "Data & Analytics"],
    "Sealights": ["Dev Tools / Cloud"],
    "Panoply": ["Data & Analytics", "Dev Tools / Cloud"],
    "Databand": ["Data & Analytics", "Dev Tools / Cloud"],
    "Passage AI": ["Future of Work"],
    "Zone7": ["Health", "Data & Analytics"],
    "Saucey": ["Consumer", "CPG"],
    "Cyvera": ["Cybersecurity"],
    "Insightix": ["Cybersecurity"],
    "Go Networks": ["Deeptech / Robotics / AR/VR"],
    "IP Infusion": ["Dev Tools / Cloud"],
    "Nolio": ["Dev Tools / Cloud"],
    "eVoice": ["Future of Work"],
    "iCast": ["Gaming / Media / Entertainment"],
    "MentAd": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Mertado": ["Consumer"],
    "MobSmith": ["Gaming / Media / Entertainment"],
    "Mariana": ["Data & Analytics", "Future of Work"],
    "NavTrac": ["Logistics / Supply Chain"],
    "Tagado": ["Consumer", "Data & Analytics"],
    "CREO": ["Gaming / Media / Entertainment"],
    "EFI": ["Gaming / Media / Entertainment"],
    "DSP Group": ["Deeptech / Robotics / AR/VR"],
    "Upfront Digital Media": ["Gaming / Media / Entertainment"],
    "Braze": ["Consumer", "Data & Analytics"],
    "Trulioo": ["RegTech/Gov/Legal", "Cybersecurity"],
    "Segmed": ["Health", "Data & Analytics"],
    "CaseStack": ["Logistics / Supply Chain"],
    "Upstream": ["Web3 / Crypto"],
    "Mytaverse": ["Deeptech / Robotics / AR/VR"],
    "Overview": ["Deeptech / Robotics / AR/VR"],
    "Shabodi": ["Dev Tools / Cloud"],
    "VerAI": ["Climate / Sustainability", "Data & Analytics"],
    "ChiselStrike": ["Dev Tools / Cloud"],
    "Dorian Therapeutics": ["BioTech"],
    "Grips": ["Data & Analytics", "Consumer"],
    "Pipe17": ["Consumer", "Logistics / Supply Chain"],
    "Partful, a SamsonVT company": ["Consumer"],
    "Konfyd": ["FinTech / Insurance"],
    "Joshu": ["FinTech / Insurance"],
    "Flex": ["Logistics / Supply Chain"],
    "Field Materials": ["PropTech"],
    "Vista Research": ["FinTech / Insurance", "Data & Analytics"],
    "AbirNet": ["Cybersecurity"],
    "Allerez": ["Data & Analytics"],
    "Conduct Software": ["Future of Work"],
    "Oversee (formerly FairFly)": ["Transportation / Mobility", "Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = []
    for post in soup.select(".fl-post-grid-post"):
        meta = post.select_one('meta[itemprop="mainEntityOfPage"]')
        href = meta.get("itemid") if meta else None
        if not href:
            a = post.select_one('a[href*="/portfolio-companies/"]')
            href = a["href"] if a else None
        if not href:
            continue
        strs = [clean(x) for x in post.stripped_strings if clean(x)]
        badge = next((x for x in strs if x in ("Acquired", "IPO")), None)
        fund = next((c.split("fund_type-", 1)[1] for c in post.get("class", []) if c.startswith("fund_type-")), None)
        name = clean(meta.get("content")) if meta and meta.get("content") else (strs[-1] if strs else None)
        cards.append((href, name, badge, fund))
    if limit:
        cards = cards[:limit]
    pages = fetch_many([c[0] for c in cards], workers=6)
    out = []
    for href, name, badge, fund in cards:
        html = pages.get(href)
        tagline = desc = site = None
        if html:
            d = BeautifulSoup(html, "html.parser")
            h1 = d.select_one("h1.fl-heading")
            name = clean(h1.get_text(" ")) if h1 else name
            sd = d.select_one(".short-description")
            tagline = clean(sd.get_text(" ")) if sd else None
            paras = []
            # company copy lives in the page's content-box column (the footer's
            # office addresses are separate rich-text modules)
            for blk in d.select(".content-box .fl-rich-text"):
                ps = blk.select("p") or [blk]
                for p in ps:
                    t = clean(p.get_text(" "))
                    if t and INTRO not in t and t not in paras and not FOOTER.search(t):
                        paras.append(t)
            desc = " ".join(paras) or None
            for a in d.select("a[href^=http]"):
                h = a["href"]
                host = urlparse(h).netloc.lower()
                if any(s in host for s in SKIP_HOSTS) or is_social(h):
                    continue
                site = h
                break
        # keep the linked site only when its domain carries the company name
        # (some exited companies link to their acquirer instead)
        norm = lambda x: re.sub(r"[^a-z0-9]", "", (x or "").lower())
        link_on_site = site
        if site and norm(name)[:4] not in norm(urlparse(site).netloc):
            site = None
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(site),
            "link_on_site": link_on_site if link_on_site != site else None,
            "fund_type": fund.replace("-", " ") if fund else None,
            "exit_type": badge,
            "status": "acquired" if badge == "Acquired" else (None if badge else "active"),
            "everywhere_tags": tags_for(name, tagline or desc or "", [], SECTOR_TAG_MAP),
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
    for k in ("description", "tagline", "company_url", "fund_type", "exit_type", "status", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
