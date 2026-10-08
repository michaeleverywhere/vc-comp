#!/usr/bin/env python3
"""Pitango portfolio scraper -> pitango_companies.json
Source: https://www.pitango.com/portfolio/ — WordPress. The grid renders one
card per company with data-slug, data-domains (sector slugs), data-funds
(Pitango First / Growth / HealthTech) and data-status (ipo / acquired / blank),
plus the company name as the logo alt text. Each card's detail drawer is
loaded from the site's own front-end AJAX action (admin-ajax.php,
action=get_popup, slug=<slug>), which returns tagline, founders, "Founded in",
"Partnered in" (-> first_invested), Pitango partners, About text and the
company website.
Status: Acquired -> acquired; IPO -> left blank (raw kept in site_status /
exit_type); no status shown -> blank (the site does not label active cos).
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, fetch, clean, tags_for, clean_url, is_social, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.pitango.com/portfolio/"
AJAX = "https://www.pitango.com/wp-admin/admin-ajax.php"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "pitango_companies.json")
PRIMARY = "Pitango"
DOMAINS = {
    "bioconvergence": "BioConvergence", "climatech": "Climatech", "cloud-infrastructure": "Cloud & Infrastructure",
    "cyber-security": "Cyber Security", "devops": "DevOps", "digital-health": "Digital Health", "edtech": "EdTech",
    "fintech-insure-tech": "Fintech & Insure Tech", "food-tech": "Food Tech", "generative-ai": "Generative AI",
    "industry-4-0": "Industry 4.0", "legal-tech": "Legal Tech", "media-gaming": "Media & Gaming",
    "medical-devices": "Medical Devices", "mobility-smart-city": "Mobility & Smart City", "proptech": "PropTech",
    "quantum-computing": "Quantum Computing", "retail-e-commerce": "Retail & e-Commerce",
    "sales-marketing": "Sales & Marketing", "web-3": "Web 3", "wellness": "Wellness",
}
FUNDS = {"first": "Pitango First", "growth": "Pitango Growth", "healthtech": "Pitango HealthTech"}
SECTOR_TAG_MAP = {
    "bioconvergence": ["BioTech"], "climatech": ["Climate / Sustainability"],
    "cloud & infrastructure": ["Dev Tools / Cloud"], "cyber security": ["Cybersecurity"], "devops": ["Dev Tools / Cloud"],
    "digital health": ["Health"], "fintech & insure tech": ["FinTech / Insurance"], "food tech": ["CPG"],
    "industry 4.0": ["Deeptech / Robotics / AR/VR"], "legal tech": ["RegTech/Gov/Legal"],
    "media & gaming": ["Gaming / Media / Entertainment"], "medical devices": ["Health"],
    "mobility & smart city": ["Transportation / Mobility"], "proptech": ["PropTech"],
    "quantum computing": ["Deeptech / Robotics / AR/VR"], "retail & e-commerce": ["Consumer"],
    "web 3": ["Web3 / Crypto"], "wellness": ["Health"],
}
STATUS = {"acquired": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "3DV Systems": ["Deeptech / Robotics / AR/VR", "Gaming / Media / Entertainment"],
    "Altesa Biosciences": ["BioTech", "Health"],
    "AppsFlyer": ["Data & Analytics", "Gaming / Media / Entertainment"],
    "Aquant": ["Data & Analytics", "Future of Work"],
    "Borderfree": ["Consumer", "FinTech / Insurance", "Logistics / Supply Chain"],
    "Browsi": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Catch AI": ["Future of Work"],
    "Celeno Communications": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Convergin": ["Dev Tools / Cloud"],
    "ConvertMedia": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "D-ID": ["Gaming / Media / Entertainment", "Dev Tools / Cloud"],
    "Gteko": ["Future of Work"],
    "Iguazio": ["Dev Tools / Cloud", "Data & Analytics"],
    "Jinko Solar": ["Climate / Sustainability"],
    "Komodor": ["Dev Tools / Cloud"],
    "LeaFix Medical": ["Health"],
    "Mend": ["Cybersecurity", "Dev Tools / Cloud"],
    "Mobile Access": ["Deeptech / Robotics / AR/VR"],
    "Neebula Systems": ["Dev Tools / Cloud", "Data & Analytics"],
    "PayEm": ["FinTech / Insurance"],
    "RedBend": ["Dev Tools / Cloud"],
    "Retalix": ["Consumer", "Data & Analytics"],
    "Skycure": ["Cybersecurity"],
    "Tailor Brands": ["Future of Work"],
    "Timeful": ["Future of Work"],
    "UniPaaS": ["FinTech / Insurance"],
    "Ventor Technologies": ["Health"],
    "Vertos Medical": ["Health"],
    "Zerto": ["Dev Tools / Cloud"],
    "Zorro": ["Health", "FinTech / Insurance", "Future of Work"],
}


def popup(slug):
    for attempt in range(1, 4):
        try:
            r = requests.post(AJAX, data={"action": "get_popup", "slug": slug, "paging": "show"},
                              headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            time.sleep(1.5 * attempt)
    return ""


def fact(soup, label):
    for item in soup.select(".facts-item"):
        spans = item.find_all("span", recursive=False)
        if spans and clean(spans[0].get_text(" ", strip=True)).rstrip(":").lower() == label.lower():
            return clean(" ".join(s.get_text(" ", strip=True) for s in spans[1:]))
    return None


def parse_popup(html):
    s = BeautifulSoup(html or "", "html.parser")
    d = {}
    p = s.find("p")
    d["tagline"] = clean(p.get_text(" ", strip=True)) if p else None
    web = s.select_one('a[aria-label="website"]')
    d["company_url"] = clean_url(web["href"]) if web and web.get("href") and not is_social(web["href"]) else None
    founders = []
    for h in s.find_all("h3"):
        if clean(h.get_text()) == "Founders":
            box = h.find_next_sibling("div")
            founders = [clean(y) for x in (box.find_all("div", recursive=False) if box else [])
                        for y in re.split(r"\s\|\s", x.get_text(" ", strip=True)) if clean(y)]
    d["founders"] = [clean(re.sub(r",\s*(CEO|CTO|COO|CPO|CFO|Co-?Founder|President|Chairman).*$", "", f, flags=re.I))
                     for f in founders if f]
    d["year_founded"] = year_of(fact(s, "Founded in"))
    d["first_invested"] = year_of(fact(s, "Partnered in"))
    partners = fact(s, "Partners")
    d["partners"] = [clean(x) for x in re.split(r",|\s&\s", partners)] if partners else []
    about = s.select_one(".about-content")
    d["description"] = clean(about.get_text(" ", strip=True)) if about else None
    return d


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards, seen = [], set()
    for c in soup.select("#portfolio-grid .company-card[data-slug]"):
        slug = c["data-slug"]
        if slug in seen:
            continue
        seen.add(slug)
        cards.append(c)
    if limit:
        cards = cards[:limit]
    with ThreadPoolExecutor(4) as ex:
        pops = dict(zip([c["data-slug"] for c in cards], ex.map(popup, [c["data-slug"] for c in cards])))
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for c in cards:
        img = c.find("img")
        name = clean(img.get("alt")) if img else None
        if not name:
            continue
        slug = c["data-slug"]
        d = parse_popup(pops.get(slug))
        sectors = [DOMAINS.get(x, x) for x in json.loads(c.get("data-domains") or "[]")]
        funds = [FUNDS[x] for x in json.loads(c.get("data-funds") or "[]") if x in FUNDS]
        raw = clean(c.get("data-status"))
        out.append({
            "company_name": name,
            "description": d.get("description") or d.get("tagline"),
            "tagline": d.get("tagline"),
            "company_url": d.get("company_url"),
            "company_profile_url": f"{SOURCE_URL}#{slug}",
            "status": STATUS.get((raw or "").lower()),
            "site_status": {"ipo": "IPO", "acquired": "Acquired"}.get((raw or "").lower(), raw),
            "exit_type": {"ipo": "IPO", "acquired": "Acquisition"}.get((raw or "").lower()),
            "first_invested": d.get("first_invested"),
            "year_founded": d.get("year_founded"),
            "founders": d.get("founders") or [],
            "partners": d.get("partners") or [],
            "funds": funds,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, d.get("description") or d.get("tagline"), sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "tagline", "company_url", "status", "site_status", "first_invested", "year_founded",
              "founders", "partners", "funds", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
