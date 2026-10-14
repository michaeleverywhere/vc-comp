#!/usr/bin/env python3
"""Castle Island Ventures portfolio scraper -> castleisland_companies.json
Sources: WP REST /wp-json/wp/v2/portfolios (name, one-line description,
portfolio-category) + the public /portfolio/ Elementor loop pages
(?jsf=epro-loop-builder&pagenum=N) for each company's "Website" link,
matched by WP post id. Castle Island invests only in public-blockchain /
crypto companies, so every company carries the Web3 / Crypto tag.
"""
import os, re, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, carry_forward_descriptions
from _d20_common import write_out

SOURCE_URL = "https://castleisland.vc/portfolio/"
REST = "https://castleisland.vc/wp-json/wp/v2/portfolios?per_page=100&page={}"
CATS = "https://castleisland.vc/wp-json/wp/v2/portfolio-category?per_page=100"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "castleisland_companies.json")
PRIMARY = "Castle Island Ventures"
SECTOR_MAP = {"cybersecurity": ["Cybersecurity"], "financial market infrastructure": ["FinTech / Insurance"],
              "payments & stablecoins": ["FinTech / Insurance"], "protocols": []}
TAG_OVERRIDES = {
    "Alkimiya": ["Web3 / Crypto"],
    "Andrena": ["Web3 / Crypto"],
    "Arch": ["Web3 / Crypto", "FinTech / Insurance"],
    "Atrium": ["FinTech / Insurance", "Data & Analytics"],
    "Attestiv": ["Cybersecurity", "Gaming / Media / Entertainment"],
    "CAT Labs": ["Web3 / Crypto", "Cybersecurity"],
    "Dust Identity": ["Cybersecurity", "Logistics / Supply Chain"],
    "Notabene": ["Web3 / Crypto", "RegTech/Gov/Legal"],
    "Beam": ["Web3 / Crypto", "FinTech / Insurance"],
}


def name_matches_site(name, url):
    """True when the linked domain plausibly belongs to the company itself.
    Several portfolio entries link to an acquirer's site (e.g. Beam ->
    moderntreasury.com); those links are kept as linked_site, not company_url."""
    if not url:
        return False
    host = re.sub(r"^https?://(www\.)?", "", url.lower()).split("/")[0]
    label = host.split(".")[0]
    toks = [t for t in re.findall(r"[a-z0-9]+", name.lower()) if len(t) >= 3]
    joined = re.sub(r"[^a-z0-9]", "", name.lower())
    return joined in label or any(t in label for t in toks)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cats = {c["id"]: clean(htmlmod.unescape(c["name"])) for c in fetch(CATS, as_json=True)}
    posts, page = [], 1
    while True:
        batch = fetch(REST.format(page), as_json=True)
        if not batch:
            break
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    sites = {}
    for n in range(1, 15):
        url = SOURCE_URL if n == 1 else f"{SOURCE_URL}?jsf=epro-loop-builder&pagenum={n}"
        soup = BeautifulSoup(fetch(url), "html.parser")
        found = 0
        for it in soup.select(".e-loop-item"):
            pid = next((c[5:] for c in it.get("class", []) if re.fullmatch(r"post-\d+", c)), None)
            a = next((a for a in it.find_all("a") if clean(a.get_text()) == "Website"), None)
            if pid and pid not in sites:
                sites[pid] = clean_url(a.get("href")) if a else None
                found += 1
        if not found:
            break
    out, seen = [], set()
    for p in posts:
        name = clean(htmlmod.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(BeautifulSoup(p.get("content", {}).get("rendered", ""), "html.parser").get_text(" ", strip=True))
        sectors = [cats[c] for c in p.get("portfolio-category", []) if c in cats]
        link = sites.get(str(p["id"]))
        ok = name_matches_site(name, link)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": link if ok else None,
            "linked_site": None if ok else link,
            "sectors": sectors,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        tags = ["Web3 / Crypto"]
        for s in r["sectors"]:
            for t in SECTOR_MAP.get(s.lower(), []):
                if t not in tags:
                    tags.append(t)
        for t in tags_for(r["company_name"], r["description"]):
            if t not in tags and len(tags) < 3:
                tags.append(t)
        r["everywhere_tags"] = tags[:3]
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
