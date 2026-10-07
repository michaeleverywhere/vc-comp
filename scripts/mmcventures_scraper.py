#!/usr/bin/env python3
"""MMC Ventures portfolio scraper -> mmcventures_companies.json
Source: https://mmc.vc/portfolio/ — WordPress, one server-rendered grid. Each
card: name, MMC sector category, one-line description and a stage line —
either the entry round + year ("Series A" / "2024") or, for realized
investments, "Exited to <buyer>". Each /portfolio/<slug>/ page adds Year of
Investment, Investment Status (Current / Exited), Website and Investment Lead.
Status: Current -> active; Exited / "Exited to X" -> acquired (buyer kept).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, year_of, stage_label, apply_tag_overrides

SOURCE_URL = "https://mmc.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "mmcventures_companies.json")
PRIMARY = "MMC Ventures"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "data-driven health": ["Health", "Data & Analytics"],
    "cloud & data infrastructure": ["Dev Tools / Cloud", "Data & Analytics"], "consumer & product": ["Consumer"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Brightpearl": ["Dev Tools / Cloud", "Consumer"],
    "Current Health": ["Health", "Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for it in soup.select(".default-portfolio-item"):
        h = it.select_one(".default-portfolio-item__meta h4") or it.select_one("h4")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        a = it.select_one("a[href*='/portfolio/']")
        cats = it.select_one(".meta-tag__cats")
        sectors = [clean(x) for x in (cats.get_text(" ") if cats else "").split(",") if clean(x)]
        p = it.select_one(".default-portfolio-item__meta > p")
        stage_ps = [clean(x.get_text(" ")) for x in it.select(".default-portfolio-item__stage p")]
        rows.append((name, a["href"].strip() if a else None, sectors, clean(p.get_text(" ")) if p else None, stage_ps))
        if limit and len(rows) >= limit:
            break
    details = fetch_many([r[1] for r in rows if r[1]])
    out = []
    for name, href, sectors, desc, stage_ps in rows:
        first = stage_ps[0] if stage_ps else None
        exit_m = re.match(r"(?i)exited(?: to (.+))?$", first or "")
        stage = None if exit_m else stage_label(re.sub(r"(?i)^pre seed$", "Pre-Seed", first or ""))
        year = next((year_of(x) for x in stage_ps if year_of(x)), None)
        url, site_status, lead = None, None, None
        html = details.get(href) if href else None
        if html:
            ds = BeautifulSoup(html, "html.parser")
            st = list(ds.stripped_strings)
            year = year or year_of(label_after(st, "Year of Investment"))
            site_status = label_after(st, "Investment Status")
            lead = label_after(st, "Investment Lead")
            if not desc:  # card left it out: use the profile page's own summary
                for x in ds.select("main p, article p, .entry-content p"):
                    t = clean(x.get_text(" "))
                    if t and len(t) > 40 and "read more" not in t.lower() and "cookie" not in t.lower():
                        desc = t
                        break
            w = label_after(st, "Website")
            for x in ds.select("a[href^=http]"):
                if w and clean(x.get_text()) == w:
                    url = x["href"].strip()
                    break
            if not url and w and "." in w and " " not in w:
                url = "https://" + w.removeprefix("https://").removeprefix("http://")
        if exit_m or (site_status or "").lower().startswith("exit"):
            status = "acquired"
        elif (site_status or "").lower() == "current":
            status = "active"
        else:
            status = None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "company_profile_url": href,
            "stage": stage,
            "first_invested": year,
            "status": status,
            "site_status": site_status or first if exit_m else site_status,
            "acquirer": clean(exit_m.group(1)) if exit_m and exit_m.group(1) else None,
            "investment_lead": lead,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "stage", "first_invested", "status", "acquirer", "investment_lead", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
