#!/usr/bin/env python3
"""Prime Movers Lab portfolio scraper -> primemoverslab_companies.json
Source: https://www.primemoverslab.com/portfolio/ — server-rendered grid of
`figure.team-pml` cards: company name (strong.team-name), one-line
specialty (span.team-spec) and website link. The page also lists a
"Public Companies / Exits" section; companies there are marked exited.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.primemoverslab.com/portfolio/"
PRIMARY = "Prime Movers Lab"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for fig in soup.select("figure.team-pml"):
        nm = fig.select_one(".team-name")
        if not nm or not clean(nm.get_text()):
            continue
        sp = fig.select_one(".team-spec")
        a = fig.select_one("a[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        sec = fig.find_previous(lambda t: t.name in ("h2",) and "section-title" in (t.get("class") or []))
        exited = bool(sec and "exit" in sec.get_text().lower())
        out.append(rec(nm.get_text(" ", strip=True), sp.get_text(" ", strip=True) if sp else None, href,
                       PRIMARY, SOURCE_URL, scraped_at, status="exited" if exited else None))
    finish(out, "primemoverslab", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
