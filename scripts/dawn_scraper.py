#!/usr/bin/env python3
"""Dawn Capital portfolio scraper -> dawn_companies.json
Source: https://www.dawncapital.com/companies — Next.js (Sanity) server-rendered
list of company links (/companies/<slug>), with one-line taglines (featured
cards also carry "Acquired by X" / "Listed on X"). Each company page has the
name, a headline, Website link, Founders, Founded, Invested (year Dawn
invested), HQ (city), Sector, Status (only "Exited" when exited) and long-form
copy. status: Status "Exited" -> acquired only when the site's text says
"Acquired by"; a listing ("Listed on NASDAQ") is kept in exit_note; otherwise
current portfolio -> active. Dawn is B2B-only (sector labels are Dawn's).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, year_of, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.dawncapital.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "dawn_companies.json")
PRIMARY = "Dawn Capital"
LABELS = ("Founders", "Founded", "Invested", "HQ", "Sector", "Sectors", "Status")
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "security & privacy": ["Cybersecurity"], "data & analytics": ["Data & Analytics"], "insurtech": ["FinTech / Insurance"], "security": ["Cybersecurity"],
    "cybersecurity": ["Cybersecurity"], "dev ops & infrastructure": ["Dev Tools / Cloud"], "data & ai": ["Data & Analytics"],
    "data": ["Data & Analytics"], "legaltech": ["RegTech/Gov/Legal"], "regtech": ["RegTech/Gov/Legal"],
    "future of work": ["Future of Work"],
}
TAG_OVERRIDES = {  # hand-reviewed against Dawn's own copy (no LLM)
    "Eigen Technologies": ["Data & Analytics", "Future of Work"],
    "Gelato": ["Logistics / Supply Chain", "Consumer"],
    "Templafy": ["Future of Work"],
    "Qogita": ["Logistics / Supply Chain"],
    "Quantilope": ["Data & Analytics"],
    "Harbr": ["Data & Analytics"],
    "inforcer": ["Cybersecurity", "Dev Tools / Cloud"],
    "Brite Payments": ["FinTech / Insurance"],
    "Mimecast": ["Cybersecurity"],
    "Omi": ["Gaming / Media / Entertainment"],
    "Runware": ["Dev Tools / Cloud", "Gaming / Media / Entertainment"],
    "Showpad": ["Future of Work"],
    "Onum": ["Cybersecurity", "Data & Analytics"],
    "Fonoa": ["FinTech / Insurance", "RegTech/Gov/Legal"],
    "Cortea": ["FinTech / Insurance", "Future of Work"],
    "LeadDesk": ["Dev Tools / Cloud", "Future of Work"],
    "Kraaft": ["PropTech", "Future of Work"],
    "FlowX.AI": ["Dev Tools / Cloud", "FinTech / Insurance"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = {}
    for a in soup.select('a[href^="/companies/"]'):
        href = urljoin(SOURCE_URL, a["href"])
        strs = [clean(x) for x in a.stripped_strings if clean(x)]
        prev = cards.get(href) or []
        if len(" ".join(strs)) > len(" ".join(prev)):
            cards[href] = strs
    hrefs = list(cards)
    if limit:
        hrefs = hrefs[:limit]
    pages = fetch_many(hrefs, workers=6)
    out = []
    for href in hrefs:
        html = pages.get(href)
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        site = next((a["href"] for a in d.select("a[href^=http]") if clean(a.get_text(" ")).startswith("Website") and "dawncapital.com" not in a["href"]), None)
        main_el = d.body or d
        for t in main_el.select("nav, header, footer, script, style"):
            t.decompose()
        strs = [clean(x) for x in main_el.stripped_strings if clean(x)]
        title = clean(d.title.get_text(" ")) if d.title else None
        name = clean(title.split("|")[0]) if title else (cards[href][0] if cards[href] else None)
        if not name:
            continue
        if "Our Companies" in strs:
            strs = strs[strs.index("Our Companies") + 1:]
        f, i, first_label = {}, 0, None
        while i < len(strs):
            s = strs[i]
            if s in LABELS and i + 1 < len(strs) and s not in f:
                if first_label is None:
                    first_label = i
                f[s] = strs[i + 1]
                i += 2
                continue
            if s == "Founders" and s in f:
                break
            i += 1
        # headline sits between the name and the first label; long copy after the label block
        try:
            name_idx = strs.index(name)
        except ValueError:
            name_idx = 0
        head = [x for x in strs[name_idx + 1:first_label or name_idx + 1] if x != "Website"]
        tagline = head[0] if head else None
        body, j = [], (first_label or 0)
        while j < len(strs) and (strs[j] in LABELS or (j > 0 and strs[j - 1] in LABELS)):
            j += 1
        for s in strs[j:]:
            if s == "Founders" or s == "Related":
                break
            if len(s) > 40:
                body.append(s)
        sectors = [x.strip() for x in (f.get("Sector") or f.get("Sectors") or "").split(",") if x.strip()]
        if body and sectors and body[0] == ", ".join(sectors):
            body = body[1:]
        desc = " ".join(body) or tagline
        card_txt = " | ".join(cards[href][1:]) if len(cards[href]) > 1 else None
        exit_note = None
        m = re.search(r"(Acquired by [^|.]+|Listed on [^|.]+|IPO[^|.]*)", card_txt or "")
        if m:
            exit_note = clean(m.group(1))
        acq = re.match(r"Acquired by (.+)", exit_note or "")
        exited = (f.get("Status") or "").lower() == "exited" or bool(exit_note)
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": tagline,
            "company_url": clean_url(site) if site else None,
            "founders": [x.strip() for x in (f.get("Founders") or "").split(",") if x.strip()],
            "founded_year": year_of(f.get("Founded")),
            "first_invested": year_of(f.get("Invested")),
            "location": f.get("HQ"),
            "sectors": sectors,
            "site_status": f.get("Status") or ("Exited" if exited else "Current"),
            "exit_note": exit_note,
            "acquirer": clean(acq.group(1)) if acq else None,
            "status": "acquired" if acq else (None if exited else "active"),
            "everywhere_tags": tags_for(name, tagline or "", sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "tagline", "company_url", "founders", "first_invested", "location", "sectors", "status", "acquirer", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
