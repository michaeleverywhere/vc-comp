#!/usr/bin/env python3
"""Cowboy Ventures portfolio scraper -> cowboyventures_companies.json
Source: https://www.cowboy.vc/portfolio (Webflow founder cards; dedupe by /portfolio/<slug>).
"""
import json, os, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

PORTFOLIO_URL = "https://www.cowboy.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "cowboyventures_companies.json")
PRIMARY = "Cowboy Ventures"
SKIP_FILTERS = {
    "active", "exited", "exit", "enterprise", "consumer", "fintech", "health",
    "security", "security, enterprise", "vertical ai", "ai", "marketplace",
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()

    by_slug = {}
    for it in soup.select(".collection-list > .w-dyn-item, .founderlinkwrapper.w-dyn-item"):
        a = it.select_one("a[href*='/portfolio/']")
        if not a:
            continue
        href = a["href"].split("?")[0]
        slug = href.rstrip("/").split("/")[-1]
        if not slug or slug == "portfolio":
            continue
        filters = [clean(x.get_text()) for x in it.select(".founderfilter")]
        filters = [f for f in filters if f]
        status = "Active"
        company = None
        sectors = []
        for f in filters:
            fl = f.lower()
            if fl in ("active",):
                status = "Active"
            elif fl in ("exited", "exit"):
                status = "Exited"
            elif fl in SKIP_FILTERS or fl.startswith("security"):
                if fl not in ("active", "exited", "exit"):
                    sectors.append(f)
            else:
                # likely company name (Positron) or stealth title
                company = f
        if not company:
            # stealth titles often in founders_role
            role = it.select_one(".founders_role")
            company = clean(role.get_text()) if role else slug.replace("--", " — ").replace("-", " ").title()
        founders = []
        fn = it.select_one(".founders_name")
        if fn:
            nm = clean(fn.get_text())
            if nm and nm.lower() != "stealth founder":
                founders.append(nm)
        profile = urljoin(PORTFOLIO_URL, href)
        rec = by_slug.get(slug) or {
            "company_name": company,
            "description": None,
            "company_url": None,
            "status": status,
            "stage": None,
            "sectors": [],
            "founders": [],
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": profile,
            "scraped_at": scraped_at,
        }
        if company and (not rec["company_name"] or rec["company_name"].startswith("Stealth") is False):
            rec["company_name"] = company
        if status == "Exited":
            rec["status"] = "Exited"
        for s in sectors:
            if s not in rec["sectors"]:
                rec["sectors"].append(s)
        for f in founders:
            if f not in rec["founders"]:
                rec["founders"].append(f)
        by_slug[slug] = rec

    # Optionally enrich from detail pages (description + website)
    import time
    from _scraper_common import fetch as fetch2
    out = []
    for i, (slug, rec) in enumerate(by_slug.items()):
        if limit and i >= limit:
            break
        try:
            dhtml = fetch2(rec["source_url"])
            dsoup = BeautifulSoup(dhtml, "html.parser")
            md = dsoup.select_one('meta[name="description"], meta[property="og:description"]')
            if md and md.get("content"):
                rec["description"] = clean(md["content"])
            for p in dsoup.find_all("p"):
                t = clean(p.get_text())
                if t and len(t) >= 80 and "cowboy" not in t.lower()[:20]:
                    rec["description"] = t
                    break
            for a in dsoup.select("a[href^='http']"):
                href = a["href"]
                if any(x in href for x in ("cowboy.vc", "linkedin", "twitter", "x.com", "facebook", "instagram")):
                    continue
                rec["company_url"] = clean(href)
                break
            time.sleep(0.15)
        except SystemExit:
            pass
        rec["everywhere_tags"] = classify(rec["company_name"], rec.get("description"), rec.get("sectors"))[:4]
        out.append(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged")


if __name__ == "__main__":
    main()
