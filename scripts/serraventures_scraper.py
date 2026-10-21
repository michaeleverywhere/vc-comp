#!/usr/bin/env python3
"""Serra Ventures portfolio scraper -> serraventures_companies.json
Source: https://www.serraventures.com/serra-capital-iii — Champaign, IL venture firm; Squarespace site with one
portfolio page per fund (Serra Capital I/II/II Follow-On/III/III SBIC, Ag Tech Fund, Ag & Food Tech Fund II,
Opportunities Fund) plus an "Exited Companies" page: company names from each company block heading (with its "Learn about <company>" link) (the
fund(s) it is listed under kept), and each company page adds the description, website, location, sector and CEO."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.serraventures.com/serra-capital-iii"
BASE = "https://www.serraventures.com"
PRIMARY = "Serra Ventures"
FUNDS = {"/serra-capital-i": "Serra Capital I", "/serra-capital-ii": "Serra Capital II",
         "/serra-capital-ii-1": "Serra Capital II Follow-On Fund", "/serra-capital-iii": "Serra Capital III",
         "/serra-capital-iii-sbic": "Serra Capital III SBIC", "/serra-capital-ag-tech-fund": "Serra Capital Ag Tech Fund",
         "/serra-ag-and-food-tech-fund-ii": "Serra Ag & Food Tech Fund II",
         "/serra-capital-opportunities-fund": "Serra Capital Opportunities Fund", "/exited-companies": "Exited"}
key = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cos = {}  # key -> dict(name, url, funds)
    for path, fund in FUNDS.items():
        m = BeautifulSoup(fetch(BASE + path), "html.parser").find("main")
        for a in m.find_all("a", href=True):
            t = clean(a.get_text(" ", strip=True)) or ""
            if not t.lower().startswith("learn about"):
                continue
            h2 = a.find_previous("h2")
            hn = clean(h2.get_text(" ", strip=True)) if h2 else None
            name = hn if hn and not hn.upper().startswith("SERRA") else clean(t[len("learn about"):])
            if not name:
                continue
            c = cos.setdefault(key(name), dict(name=name, url=urljoin(BASE, a["href"]), funds=[]))
            if fund not in c["funds"]:
                c["funds"].append(fund)
    pages = fetch_many([c["url"] for c in cos.values()], workers=3, pause=0.3)
    out = []
    for c in cos.values():
        desc = web = loc = sector = ceo = None
        h = pages.get(c["url"])
        if h:
            m = BeautifulSoup(h, "html.parser").find("main")
            strs = [x for x in (clean(z) for z in m.stripped_strings) if x] if m else []
            strs = [x for x in strs if key(x) != key(c["name"]) and x != "Website"]
            longs = [x for x in strs if len(x) > 60]
            desc = longs[0] if longs else None
            for x in strs:
                if x == desc:
                    continue
                if not loc and re.search(r",\s*[A-Z]{2}$|,\s*[A-Z][a-z]+$", x) and len(x) < 40:
                    loc = x
                elif not ceo and re.search(r"\bCEO\b", x) and len(x) < 80:
                    ceo = re.sub(r",?\s*CEO.*$", "", x).strip() or None
                elif loc and not sector and len(x) < 50 and not re.search(r"\bCEO\b", x):
                    sector = x
            for a in (m.select("a[href^=http]") if m else []):
                href = a["href"].strip()
                if "serraventures.com" not in href and not is_social(href):
                    web = href
                    break
        exited = "Exited" in c["funds"]
        out.append(rec(c["name"], desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else [],
                       location=loc, ceo=ceo, serra_funds=[f for f in c["funds"] if f != "Exited"],
                       profile_url=c["url"], status="exited" if exited else "active"))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Serra companies")
    finish(out, "serraventures", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
