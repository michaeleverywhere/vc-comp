#!/usr/bin/env python3
"""S3 Ventures portfolio scraper -> s3ventures_companies.json
Source: https://www.s3vc.com/companies-all — S3 Ventures, Austin-based venture capital firm (Texas's largest native
VC) investing in healthcare technology and B2B software. The listing links each company's profile page, which gives
the company name, status tag, tagline, description, website, HQ, sector, S3 investment stages, leadership/founders,
S3 investment team and co-investors."""
import os, sys, re, html as _h
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.s3vc.com/companies-all"
PRIMARY = "S3 Ventures"
ORIGIN = "https://www.s3vc.com"
LABELS = ("Web:", "HQ:", "Sector:", "S3 Investments:", "Leadership & Founders", "Investment Team",
          "Co-Investors", "Company News", "Resources")


def strings(soup):
    for t in soup.select("header, footer, script, style, noscript"):
        t.decompose()
    return [c for c in (clean(s) for s in soup.stripped_strings) if c]


def after(ss, label):
    if label not in ss:
        return []
    i = ss.index(label) + 1
    vals = []
    while i < len(ss) and ss[i] not in LABELS:
        vals.append(ss[i])
        i += 1
    return vals


def parse(url, html):
    soup = BeautifulSoup(html, "html.parser")
    t = soup.find("title")
    name = clean(_h.unescape(t.get_text()).split(" | ")[0].split(" \u2014 ")[0]) if t else None
    if not name or " | " not in _h.unescape(t.get_text()):
        return None
    ss = strings(soup)
    if "Web:" not in ss:
        return None
    pre = ss[:ss.index("Web:")]
    desc = pre[-1] if pre else None
    tagline = pre[-2] if len(pre) >= 2 else None
    tag = pre[-3] if len(pre) >= 3 else None
    status = "Exited" if tag and re.search(r"\b(acq|ipo|nasdaq|nyse|merged|exit)", tag, re.I) else "Active"
    web = after(ss, "Web:")
    site = None
    if web:
        site = web[0] if web[0].startswith("http") else "https://" + web[0]
    sector = after(ss, "Sector:")
    return rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at_g,
               sectors=[x.strip() for s in sector for x in s.split(",") if x.strip()] or None,
               tagline=tagline, status=status, exit_note=tag if status == "Exited" else None,
               headquarters=(after(ss, "HQ:") or [None])[0],
               s3_investments=", ".join(after(ss, "S3 Investments:")) or None,
               founders=after(ss, "Leadership & Founders") or None,
               investment_team=after(ss, "Investment Team") or None,
               co_investors=after(ss, "Co-Investors") or None, profile_url=url)


def main():
    global scraped_at_g
    scraped_at_g = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    urls = []
    for a in soup.select("a.summary-title-link"):
        u = urljoin(ORIGIN + "/", a.get("href", ""))
        if u not in urls and "/portfolio-companies" not in u:
            urls.append(u)
    pages = fetch_many(urls)
    out, seen = [], set()
    for u in urls:
        if pages.get(u):
            r = parse(u, pages[u])
            if r and r["company_name"].lower() not in seen:
                seen.add(r["company_name"].lower())
                out.append(r)
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} S3 companies")
    finish(out, "s3ventures", ("description", "website", "headquarters", "everywhere_tags"))


if __name__ == "__main__":
    main()
