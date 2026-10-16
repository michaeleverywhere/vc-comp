#!/usr/bin/env python3
"""Knife Capital portfolio scraper -> knife_companies.json
Sources: https://knifecap.com/portfolio/ (name, description, website, fund:
KNF I / KNF II / KNIFE III) and https://knifecap.com/exits/ (notable exits:
company, acquirer, year + note). Fund-of-fund/partner entries are skipped.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://knifecap.com/portfolio/"
EXITS_URL = "https://knifecap.com/exits/"
PRIMARY = "Knife Capital"
FUNDS = {"KNF I", "KNF II", "KNIFE III"}
SKIP = {"Grindstone Ventures"}  # Knife's own fund-of-fund commitment, not an operating company


def strings(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for x in s(["script", "style", "svg", "header", "footer", "nav"]):
        x.decompose()
    return [clean(t) for t in s.stripped_strings if clean(t)]


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    st = strings(SOURCE_URL)
    out = []
    i = st.index("Capital filters") + 1
    while i < len(st) and (st[i] in FUNDS or st[i] == "All"):
        i += 1
    while i + 3 < len(st) and st[i] != "See Our Notable Exits":
        name, desc, url, fund = st[i:i + 4]
        if fund not in FUNDS:
            break
        if name not in SKIP:
            out.append(rec(name, desc, url if url.startswith("http") else "https://" + url, PRIMARY, SOURCE_URL, scraped_at,
                           fund=fund, status="active"))
        i += 4
    ex = strings(EXITS_URL)
    j = ex.index("NOTABLE KNIFE CAPITAL") + 2 if "NOTABLE KNIFE CAPITAL" in ex else len(ex)
    while j + 2 < len(ex):
        name, acq, note = ex[j:j + 3]
        m = re.match(r"^((?:19|20)\d\d)\s*[–-]", note)
        if not m:
            break
        mbo = acq.upper() == "MBO"
        out.append(rec(name, note, None, PRIMARY, EXITS_URL, scraped_at,
                       status="exited" if mbo else "acquired", acquirer=None if mbo else acq, exit_type="MBO" if mbo else "acquisition",
                       exit_year=int(m.group(1)), exit_note=note))
        j += 3
    finish(out, "knife", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
