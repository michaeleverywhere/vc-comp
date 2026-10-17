#!/usr/bin/env python3
"""CoVentures portfolio scraper -> coventures_companies.json
Source: https://www.coventures.vc/founders-we-work-for — 'founders we work for' cards
(`div.founder-card`): company name (site-authored 'Try X' link text), tagline,
founders line, website and status (Closed / Pivot / Acquired)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.coventures.vc/founders-we-work-for"
PRIMARY = "CoVentures"


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
    seen = set()
    for c in s.select("div.founder-card"):
        nm, url = None, None
        for a in c.select("a[href^='http']"):
            m = re.match(r"^Try (.+)$", txt(a) or "")
            if m:
                nm, url = clean(m.group(1)), site(a); break
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in c.stripped_strings if clean(x)]
        tag = txt(c.select_one("h3"))
        fd = next((x for x in ss if x.endswith(", " + nm)), None)
        out.append(rec(nm, tag, url, PRIMARY, SOURCE_URL, scraped_at,
                       founders=fd[: -len(", " + nm)] if fd else None))
    finish(out, "coventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
