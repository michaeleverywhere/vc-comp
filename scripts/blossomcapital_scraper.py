#!/usr/bin/env python3
"""Blossom Capital portfolio scraper -> blossomcapital_companies.json
Source: https://www.blossomcap.com/portfolio — Webflow, one page. Each card
carries the logo (alt "<Name> logo"), one-liner, sector line, Country, Sector,
"Date of partnership" (month + year), a Fundraising sentence written by Blossom
(e.g. "Blossom led api.video's $5.5M Seed round. They've since raised a $12M
Series A.") and an exited flag. Each /portfolio/<slug> page adds the name (h1)
and long description. `last_financing` is the LAST round-with-amount the
Fundraising sentence names; `stage` is the round Blossom itself invested in.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, round_label, year_of

BASE = "https://www.blossomcap.com"
SOURCE_URL = BASE + "/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "blossomcapital_companies.json")
PRIMARY = "Blossom Capital"
SECTOR_TAG_MAP = {
    "financial services": ["FinTech / Insurance"], "developer tools": ["Dev Tools / Cloud"],
    "infrastructure": ["Dev Tools / Cloud"], "security": ["Cybersecurity"], "cybersecurity": ["Cybersecurity"],
    "real estate": ["PropTech"], "data": ["Data & Analytics"], "healthcare": ["Health"],
}
ROUND = r"(Pre-?Seed|Seed|Series [A-H]\+?|Growth)"
AMT_ROUND = re.compile(r"([$€£]\s?\d[\d.,]*\s?(?:[mMbBkK]n?|million|billion)?)\s+" + ROUND, re.I)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for card in soup.select(".portfolio-card-wrap"):
        a = card.select_one("a[href^='/portfolio/']")
        if not a:
            continue
        url = urljoin(BASE, a["href"])
        if url in seen:
            continue
        seen.add(url)
        logo = card.select_one("img.portfolio-card-logo[alt]")
        alt = clean(logo.get("alt")) if logo else None
        specs = {}
        for li in card.select("li.list-details"):
            v = [clean(x.get_text()) for x in li.select(".portfolio-card-specs")]
            if len(v) >= 2 and v[0]:
                specs[v[0].rstrip(":").lower()] = v[1]
        fr = card.select_one(".follow-on-funding")
        fund_txt = clean(fr.find_next_sibling(class_="p1").get_text(" ")) if fr and fr.find_next_sibling(class_="p1") else None
        blurb = card.select_one(".portfolio-card-text")
        line = card.select_one(".p2-caps")
        flag = card.select_one(".exited-flag")
        exited = bool(flag) and "w-condition-invisible" not in (flag.get("class") or [])
        rows.append({"profile": url, "alt": re.sub(r"\s+logo$", "", alt or "", flags=re.I) or None,
                     "blurb": clean(blurb.get_text(" ")) if blurb else None,
                     "sector_line": clean(line.get_text()) if line else None,
                     "specs": specs, "fundraising": fund_txt, "exited": exited})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        h1 = d.find("h1")
        name = clean(h1.get_text()) if h1 else r["alt"]
        if not name:
            continue
        intro = d.select_one("p.portfolio-intro")
        rich = d.select_one(".w-richtext")
        paras = [clean(intro.get_text(" "))] if intro and clean(intro.get_text(" ")) else []
        if rich:
            paras += [clean(p.get_text(" ")) for p in rich.select("p") if clean(p.get_text(" ")) and clean(p.get_text(" ")) != "\u200d"]
        desc = paras[0] if paras else r["blurb"]
        long_desc = " ".join(paras[1:]) or None
        fund = r["fundraising"]
        rounds = AMT_ROUND.findall(fund or "")
        own = re.search(r"Blossom (?:led|co-led|invested in|participated in)[^.]*?" + ROUND, fund or "", re.I)
        sectors = [s for s in [r["specs"].get("sector")] if s]
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": r["blurb"],
            "long_description": long_desc,
            "company_url": None,
            "company_profile_url": r["profile"],
            "status": None,
            "site_status": "Exited" if r["exited"] else None,
            "stage": round_label(own.group(1)) if own else None,
            "first_invested": year_of(r["specs"].get("date of partnership")),
            "partnership_date": r["specs"].get("date of partnership"),
            "last_financing": f"{rounds[-1][0]} {rounds[-1][1]}" if rounds else None,
            "fundraising_note": fund,
            "location": r["specs"].get("country"),
            "sectors": sectors,
            "sector_line": r["sector_line"],
            "everywhere_tags": tags_for(name, " ".join([desc or "", r["blurb"] or ""]), sectors + ([r["sector_line"]] if r["sector_line"] else []), SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "site_status", "stage", "first_invested", "last_financing", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
