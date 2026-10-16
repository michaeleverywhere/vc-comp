#!/usr/bin/env python3
"""Glasswing Ventures portfolio scraper -> glasswing_companies.json
Source: https://glasswing.vc/our-companies/ — portfolio cards with modal:
name, one-line summary, website, partner, long description.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://glasswing.vc/our-companies/"
PRIMARY = "Glasswing Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".portfolio-card"):
        nm = c.select_one(".portfolio-modal .name")
        if not nm:
            continue
        g = lambda sel: (lambda e: clean(e.get_text(" ", strip=True)) if e else None)(c.select_one(sel))
        a = c.select_one(".portfolio-modal .website a[href^=http]")
        d = c.select_one(".portfolio-modal .description")
        if d:
            for x in d.select(".mobile-contact-info"):
                x.decompose()
        desc = clean(d.get_text(" ", strip=True)) if d else None
        summary = g(".content > p")
        partner = g(".portfolio-modal .title")
        if partner and partner.lower().startswith("partner"):
            partner = partner.split(":", 1)[-1].strip()
        text = (summary or "") + " " + (desc or "")
        status = acquirer = exit_year = None
        m = re.search(r"\bwas acquired by ([A-Z][\w&.' -]+?)(?: in ((?:19|20)\d\d))?[.,]", text)
        if m:
            status, acquirer, exit_year = "acquired", m.group(1).strip(), int(m.group(2)) if m.group(2) else None
        out.append(rec(nm.get_text(" ", strip=True), desc or summary, a["href"] if a else None, PRIMARY, SOURCE_URL,
                       scraped_at, summary=summary, lead_partner=partner, status=status,
                       acquirer=acquirer, exit_year=exit_year))
    finish(out, "glasswing", ("description", "company_url", "lead_partner", "everywhere_tags"))


if __name__ == "__main__":
    main()
