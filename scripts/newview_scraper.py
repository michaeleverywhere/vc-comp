#!/usr/bin/env python3
"""NewView Capital portfolio scraper -> newview_companies.json
Source: https://www.nvc.vc/portfolio — Webflow logo index (name, exit tag) plus each
/portfolio/<slug> page: description, founded year, CEO/founders, focus and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.nvc.vc/portfolio"
PRIMARY = "NewView Capital"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    items, seen = [], set()
    for li in s.select(".logo-index-list-item"):
        a = li.select_one("a.logo-index-link[href^='/portfolio/']")
        if not a:
            continue
        u = urljoin(SOURCE_URL, a["href"])
        if u in seen:
            continue
        seen.add(u)
        img = a.find("img")
        items.append((clean(img.get("alt")) if img else None, u, txt(li.select_one(".logo-index-exit-tag"))))
    pages = fetch_many([u for _, u, _ in items])
    for nm, u, ex in items:
        d = BeautifulSoup(pages.get(u) or "", "html.parser")
        for e in d.select("style, script"):
            e.decompose()
        nm = txt(d.select_one("h2.portfolio-detail-header")) or nm
        if not nm:
            continue
        f, web = {}, None
        for it in d.select(".portfolio-detail-item"):
            cells = it.select(".w-layout-cell")
            if len(cells) >= 2:
                k, v = txt(cells[0]), txt(cells[1])
                f[k] = v
                if k == "Website":
                    web = cells[1].find("a")
        lead = next((v for k, v in f.items() if k and re.search(r"CEO|Founder", k)), None)
        exl = (ex or "").lower()
        out.append(rec(nm, txt(d.select_one(".portfolio-detail-description")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       year_founded=year_of(f.get("Milestones")), ceo=lead, focus=f.get("Focus"), exit_note=ex,
                       status="acquired" if "acquired" in exl else ("public" if re.search(r"\b(nyse|nasdaq|aim|lse|tsx)\b", exl) else None), detail_url=u))
    finish(out, "newview", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
