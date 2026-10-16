#!/usr/bin/env python3
"""Teamworthy Ventures portfolio scraper -> teamworthy_companies.json
Source: https://www.teamworthy.com/portfolio — static cards: logo, description,
website link, optional exit link ("Acquired by ..."). The site prints no company
name as text, so the name is the lead subject of the firm's own description when
it opens with "<Name> is/helps/..." and otherwise the website domain.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.teamworthy.com/portfolio"
PRIMARY = "Teamworthy Ventures"
VERB = re.compile(r"^(.{2,40}?)(?:,|\s)\s*(?:is|are|was|helps|provides|offers|builds|makes|enables|develops|has|lets|allows|connects|creates|delivers|empowers|uses|gives)\b")


def name_of(desc, site):
    m = VERB.match(desc or "")
    if m and len(m.group(1).split()) <= 4:
        return clean(re.sub(r"[’']s mission$", "", m.group(1).strip(" ,")))
    dom = urlparse(site or "").netloc.replace("www.", "")
    return dom or None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".portfolio-card"):
        d = c.select_one(".portfolio-text-block")
        desc = clean(d.get_text(" ", strip=True)) if d else None
        links = c.select(".portfolio-link-block:not(.exit) a[href^=http]")
        site = None
        for a in links:
            if not re.search(r"open positions|acquired|ipo\b|public|merged", a.get_text(" ", strip=True), re.I):
                site = a["href"]
                break
        exit_note = None
        for a in c.select("a[href]"):
            t = clean(a.get_text(" ", strip=True)) or ""
            if re.search(r"acquired|ipo\b|public|merged", t, re.I):
                exit_note = t
                break
        status = "active"
        if exit_note and "acquir" in exit_note.lower():
            status = "acquired"
        elif exit_note and ("ipo" in exit_note.lower() or "public" in exit_note.lower()):
            status = "ipo"
        acq = None
        if exit_note:
            m = re.search(r"acquired by (.+)", exit_note, re.I)
            acq = clean(m.group(1)) if m else None
        out.append(rec(name_of(desc, site), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       status=status, exit_note=exit_note, acquirer=acq))
    finish(out, "teamworthy", ("description", "company_url", "acquirer", "everywhere_tags"))


if __name__ == "__main__":
    main()
