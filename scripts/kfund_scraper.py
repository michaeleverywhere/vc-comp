#!/usr/bin/env python3
"""K Fund portfolio scraper -> kfund_companies.json
Source: https://www.kfund.vc/ — homepage investment lists (name + year of
investment as <sup>, linking to the company site), grouped under mono-type
headings (FEATURED INVESTMENTS / MORE INVESTMENTS / WE TRIED = closed);
"<name> → <acquirer>" entries are exits.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.kfund.vc/"
PRIMARY = "K Fund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for ul in soup.select("ul"):
        label = None
        for li in ul.find_all("li", recursive=False):
            sup = li.find("sup")
            if not sup:
                t = clean(li.get_text(" ", strip=True))
                if t:
                    label = t
                continue
            a = li.find("a", href=re.compile(r"^http"))
            sp = sup.find_previous_sibling("span") or li.find("span")
            yr = clean(sup.get_text())
            name = clean(sp.get_text(" ", strip=True)) if sp else None
            if yr and name and name.endswith(yr) and name != yr:
                name = clean(name[: -len(yr)])
            arrows = [clean(x.parent.parent.get_text(" ", strip=True).replace("→", "")) for x in li.find_all(string="→")]
            acquirer = arrows[0] if arrows else None
            lab = (label or "").lower()
            status = "closed" if "tried" in lab else ("acquired" if acquirer else "active")
            out.append(rec(name, None, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at,
                           first_invested_year=int(yr) if yr and yr.isdigit() else None,
                           list_label=label, status=status, acquirer=acquirer))
    finish(out, "kfund", ("company_url", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
