#!/usr/bin/env python3
"""Kickstart Fund portfolio scraper -> kickstartfund_companies.json
Source: https://kickstartfund.com/portfolio — chrome-dom Webflow CMS; company website + about."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://kickstartfund.com/portfolio"
PRIMARY = "Kickstart Fund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    html = dom(SOURCE_URL, 20000, min_len=20000)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    seen = set()
    for w in s.select("div.portfolio-link-wrapper"):
        site_a = w.select_one("a.portfolio-link_text-link")
        # website link is first a.portfolio-link_text-link whose text looks like a domain
        website = None
        for a in w.select("a.portfolio-link_text-link"):
            t = clean(a.get_text(" ", strip=True)) or ""
            href = (a.get("href") or "").strip()
            if re.search(r"\.[a-z]{2,}$", t) and " " not in t:
                website = href if href.startswith("http") else ("https://" + t)
                break
            if href.startswith("http") and not is_social(href) and "kickstart" not in href.lower():
                website = href
                break
        text = clean(w.get_text(" ", strip=True)) or ""
        about = None
        m = re.search(r"\bAbout\s+(.+)$", text)
        if m:
            about = clean(m.group(1))
            if about and len(about) > 300:
                about = about[:300].rsplit(" ", 1)[0]
        # name from domain stem
        nm = None
        if website:
            host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", website).split("/")[0].lower())
            stem = host.split(".")[0]
            if stem and 2 <= len(stem) <= 40:
                nm = stem[0].upper() + stem[1:] if stem.islower() else stem
        if not nm:
            continue
        k = nm.lower()
        if k in seen:
            continue
        seen.add(k)
        # industries
        inds = [clean(x.get_text(" ", strip=True)) for x in w.select(".portoflio-industries-cms-list-item .body, div.body")]
        inds = [i for i in inds if i and i.lower() not in ("seed", "pre-seed", "series a", "series b", "growth", "exited", "other")]
        out.append(rec(nm, about, website, PRIMARY, SOURCE_URL, scraped_at, sectors=inds[:3] or None))
    finish(out, "kickstartfund", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
