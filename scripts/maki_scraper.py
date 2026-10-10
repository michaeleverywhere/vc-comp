#!/usr/bin/env python3
"""Maki.vc portfolio scraper -> maki_companies.json
Source: https://maki.vc/portfolio/ — WordPress; the company list comes from the
site's own public WP REST collection (/wp-json/wp/v2/case, the "case" post type
behind the portfolio grid). Each case page (/case/<slug>/) has a hero with
Maki's stage label (Pre-Seed / Seed / Series A+), industry, status (Active /
Exited), name, tagline, and "Latest round: €XM", "Invested in: YYYY",
"Investors: ..." lines, followed by long-form copy.
last_financing = "Latest round" amount; stage = Maki's stage label (verbatim
round label); first_invested = "Invested in". No websites / locations on-site.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, html_text, tags_for, year_of, stage_label, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://maki.vc/portfolio/"
API = "https://maki.vc/wp-json/wp/v2/case?per_page=100&page={page}&_fields=id,slug,title,link"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "maki_companies.json")
PRIMARY = "Maki.vc"
SECTOR_TAG_MAP = {"quantum": ["Deeptech / Robotics / AR/VR"], "foodtech": ["CPG"], "fintech": ["FinTech / Insurance"], "consumer": ["Consumer"]}
TAG_OVERRIDES = {}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    items, page = [], 1
    while True:
        batch = fetch(API.format(page=page), as_json=True)
        if not batch:
            break
        items += batch
        if len(batch) < 100:
            break
        page += 1
    if limit:
        items = items[:limit]
    pages = fetch_many([i["link"] for i in items], workers=6)
    out, seen = [], set()
    for i in items:
        html = pages.get(i["link"])
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        hero = d.select_one("section.hero")
        if not hero:
            continue
        h1 = hero.select_one("h1")
        name = clean(h1.get_text(" ")) if h1 else html_text(i["title"]["rendered"])
        if not name or name.lower() in seen:
            continue  # e.g. a "-duplicate" case page
        seen.add(name.lower())
        cats = [clean(x.get_text(" ")) for x in hero.select(".hero__meta .categories__text")]
        cats = [c for c in cats if c]
        status_raw = next((c for c in cats if c.lower() in ("active", "exited", "exit", "acquired")), None)
        stage_raw = next((c for c in cats if re.search(r"(?i)seed|series", c)), None)
        industry = [c for c in cats if c not in (status_raw, stage_raw)]
        tl = hero.select_one(".hero__text:not(.is-small) p")
        tagline = clean(tl.get_text(" ")) if tl else None
        small = hero.select_one(".hero__text.is-small")
        f = {}
        if small:
            txt = small.get_text("\n")
            for k in ("Latest round", "Invested in", "Investors", "Acquired by", "Founders"):
                m = re.search(re.escape(k) + r":\s*(.+)", txt)
                if m and clean(m.group(1)) not in ("–", "-", None):
                    f[k] = clean(m.group(1))
        body = []
        for p in d.select("main p, .entry-content p"):
            if hero in p.parents:
                continue
            t = clean(p.get_text(" "))
            if t and len(t) > 60 and not t.startswith("“"):
                body.append(t)
            if len(" ".join(body)) > 400:
                break
        desc = " ".join(body) or tagline
        st = (status_raw or "").lower()
        latest = f.get("Latest round")
        ipo = None
        if latest and latest.upper().startswith("IPO"):
            ipo, latest = latest, None
        if "IPO" in industry:
            industry = [x for x in industry if x != "IPO"]
            ipo = ipo or "IPO"
        if latest and not re.search(r"\d", latest):
            stage_raw = stage_raw or latest   # a round label, not an amount
            latest = None
        acquirer = f.get("Acquired by")
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": tagline,
            "industry": industry,
            "maki_stage": stage_raw,
            "stage": stage_label(stage_raw),
            "site_status": status_raw,
            "status": "active" if st == "active" else ("acquired" if st in ("exited", "exit", "acquired") or acquirer else None),
            "acquirer": acquirer,
            "ipo": ipo,
            "founders": [x.strip() for x in re.split(r",| and ", f.get("Founders") or "") if x.strip()],
            "last_financing": latest,
            "first_invested": year_of(f.get("Invested in")),
            "co_investors": [x.strip() for x in (f.get("Investors") or "").split(",") if x.strip()],
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x), industry, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": i["link"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    # the site occasionally reuses another company's body copy (e.g. Disior's page
    # carries Ultimate.ai's text) -> fall back to the page's own tagline
    names = {r["company_name"].lower() for r in out}
    for r in out:
        d0 = (r["description"] or "").lower()
        if r["company_name"].lower().split()[0] not in d0 and any(d0.startswith(n) for n in names if n != r["company_name"].lower()):
            r["description"] = r["tagline"]
            r["everywhere_tags"] = tags_for(r["company_name"], r["tagline"], r["industry"], SECTOR_TAG_MAP)
    for r in out:
        r["sectors"] = r["industry"]
    prune_substring_tags(out, SECTOR_TAG_MAP)
    for r in out:
        r.pop("sectors", None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "stage", "status", "last_financing", "first_invested", "industry", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
