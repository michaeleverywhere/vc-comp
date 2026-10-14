#!/usr/bin/env python3
"""Crosscut Ventures portfolio scraper -> crosscut_companies.json
Source: https://crosscut.vc/companies/ — first 24 cards are server-rendered;
the rest come from the page's own public infinite-scroll call
(admin-ajax `loadmorebutton`, page=1..N) returning the same card markup:
name, description, FOUNDER/CEO, LOCATION, Sector, website link.
"""
import os, re, sys, json, time
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, carry_forward_descriptions, HEADERS
from _d20_common import write_out

SOURCE_URL = "https://crosscut.vc/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "crosscut_companies.json")
PRIMARY = "Crosscut Ventures"
SECTOR_MAP = {
    "adtech": ["Gaming / Media / Entertainment"], "advanced manufacturing": ["Deeptech / Robotics / AR/VR"],
    "climate": ["Climate / Sustainability"], "consumer": ["Consumer"], "crypto": ["Web3 / Crypto"],
    "defense & security": ["Cybersecurity"], "ecommerce": ["Consumer"], "energy & power": ["Climate / Sustainability"],
    "enterprise saas": ["Dev Tools / Cloud"], "financial services": ["FinTech / Insurance"],
    "gaming & esports": ["Gaming / Media / Entertainment"], "healthcare & wellness": ["Health"],
    "media & entertainment": ["Gaming / Media / Entertainment"], "real estate": ["PropTech"],
    "social": ["Consumer"], "transportation": ["Transportation / Mobility"],
}
TAG_OVERRIDES = {
    "9 Count": ["Consumer"],
    "Avinew": ["FinTech / Insurance", "Transportation / Mobility"],
    "Circle Street": ["Gaming / Media / Entertainment", "Consumer"],
    "Comparably": ["Future of Work", "Data & Analytics"],
    "Docstoc": ["Future of Work"],
    "FastData": ["Data & Analytics", "Dev Tools / Cloud"],
    "Field Day": ["Gaming / Media / Entertainment"],
    "GumGum": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Haxion": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Heliux": ["Dev Tools / Cloud"],
    "HiveWatch": ["Cybersecurity"],
    "Intro": ["Consumer"],
    "Lettuce": ["Consumer", "Logistics / Supply Chain"],
    "Little Labs": ["Consumer"],
    "Loyal Foundry": ["Consumer"],
    "Narvar": ["Consumer", "Logistics / Supply Chain"],
    "Nostra": ["Consumer", "Dev Tools / Cloud"],
    "Omaze": ["Consumer"],
    "Pearl": ["Health"],
    "Proteus Space": ["Deeptech / Robotics / AR/VR"],
    "Radius Agent": ["PropTech"],
    "Rx Redefined": ["Health", "Logistics / Supply Chain"],
    "Science Inc.": [],
    "The Black Tux": ["Consumer"],
    "Unblocked": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
}


def name_matches_site(name, url):
    """Several cards link an acquirer's site (Docstoc -> intuit.com); such links
    are kept as linked_site, not company_url."""
    if not url:
        return False
    host = re.sub(r"^https?://(www\.)?", "", url.lower()).split("/")[0]
    label = host.split(".")[0] if not host.startswith("corp.") else host.split(".")[1]
    toks = [t for t in re.findall(r"[a-z0-9]+", name.lower()) if len(t) >= 3]
    joined = re.sub(r"[^a-z0-9]", "", name.lower())
    return joined in label or label in joined or any(t in label for t in toks)


def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for it in soup.select("div.item[data-postid]"):
        h = it.select_one(".item__overlay_header .title h3") or it.select_one("h3")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        body = it.select_one(".item__overlay_body")
        fields = {}
        for f in it.select(".col-f__item"):
            t, v = f.select_one(".title"), f.select_one(".text")
            if t and v:
                fields[clean(t.get_text()).upper()] = clean(v.get_text(" ", strip=True))
        web = it.select_one(".item__overlay_social .link a[href]")
        rows.append({"pid": it["data-postid"], "name": name,
                     "desc": clean(body.get_text(" ", strip=True)) if body else None,
                     "ceo": fields.get("FOUNDER/CEO"), "location": fields.get("LOCATION"),
                     "sector": fields.get("SECTOR"), "url": clean_url(web["href"]) if web else None,
                     "text": clean(it.get_text(" ", strip=True)) or ""})
    return rows


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    lp = json.loads(re.search(r"var loadmore_params\s*=\s*(\{.*?\});", html, re.S).group(1))
    cards = parse_cards(html)
    for page in range(1, 30):
        r = requests.post(lp["ajaxurl"], data={"action": "loadmorebutton", "query": lp["posts"], "page": page},
                          headers=HEADERS, timeout=45)
        more = parse_cards(r.text) if r.ok and r.text.strip() else []
        if not more:
            break
        cards += more
        time.sleep(0.4)
    out, seen = [], set()
    for c in cards:
        if c["pid"] in seen:
            continue
        seen.add(c["pid"])
        out.append({
            "company_name": c["name"],
            "description": c["desc"],
            "company_url": c["url"] if name_matches_site(c["name"], c["url"]) else None,
            "linked_site": None if name_matches_site(c["name"], c["url"]) else c["url"],
            "founders": [c["ceo"]] if c["ceo"] else [],
            "location": c["location"],
            "sectors": [c["sector"]] if c["sector"] else [],
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        mapped = SECTOR_MAP.get((r["sectors"] or [""])[0].lower(), [])
        kw = [t for t in tags_for(r["company_name"], r["description"]) if t not in mapped]
        r["everywhere_tags"] = (mapped + kw)[:3]
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "founders", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
