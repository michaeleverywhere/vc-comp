#!/usr/bin/env python3
"""MATH Venture Partners portfolio scraper -> mathvp_companies.json
Source: https://mathventurepartners.com/portfolio — portfolio cards (`li.pf-card`):
company name (site-authored logo alt), founder, description, MATH fund and
active/exited section."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://mathventurepartners.com/portfolio"
PRIMARY = "MATH Venture Partners"


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
    for li in s.select("li.pf-card"):
        img = li.select_one("img[alt]")
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in li.stripped_strings if clean(x)]
        d = next((x for x in ss if len(x) > 30), None)
        fund = next((x for x in ss if re.match(r"^MATH\b", x)), None)
        fd = ss[0] if ss and ss[0] not in (d, fund) else None
        sec = li.find_previous("h2")
        hold = txt(sec)
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, founders=fd, fund=fund,
                       status="exited" if hold and hold.lower().startswith("exited") else None))
    finish(out, "mathvp", ("description", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
