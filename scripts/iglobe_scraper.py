#!/usr/bin/env python3
"""iGlobe Partners portfolio scraper -> iglobe_companies.json
Source: https://www.iglobepartners.com/portfolio/ — Portfolio cards: company name, exit note (acquired /
listed), one-line description and website (omitted when it points to an acquirer)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.iglobepartners.com/portfolio/"
PRIMARY = "iGlobe Partners"


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
    for c in s.select("div.col-inner.portfolio"):
        p = [clean(x) for x in c.stripped_strings if clean(x)]
        if not p or p[0].lower() in seen:
            continue
        nm = p[0]
        seen.add(nm.lower())
        notes = [x for x in p[1:] if re.match(r"\(?[A-Z]{3,6}:\s*\w+", x) or re.match(r"(acquired|listed|merge|exited|secondary sale)", x, re.I)]
        note = "; ".join(notes) or None
        desc = next((x for x in p[1:] if x not in notes), None)
        a = c.select_one("a[href^=http]")
        acq = bool(note and re.match(r"(acquired|merge)", note, re.I))
        out.append(rec(nm, desc, None if acq else (site(a) if a else None), PRIMARY, SOURCE_URL, scraped_at, exit_note=note,
                       status="exited" if note else None))
    finish(out, "iglobe", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
