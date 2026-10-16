#!/usr/bin/env python3
"""Algebra Ventures portfolio scraper -> algebra_companies.json
Source: https://www.algebraventures.com/ — project cards (logo alt name,
tagline, Fund I / Fund II tab) and offcanvas details (website, story, team).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.algebraventures.com/"
PRIMARY = "Algebra Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    funds = {}
    for tab, label in (("fund-i-tab", "Fund I"), ("fund-ii-tab", "Fund II")):
        for c in soup.select(f"#{tab} [data-bs-toggle=offcanvas]"):
            pid = re.sub(r"^#offcanvas-(\d+)-.*$", r"\1", c.get("data-bs-target", ""))
            funds.setdefault(pid, []).append(label)
    out = []
    for c in soup.select("#all [data-bs-toggle=offcanvas]"):
        tgt = c.get("data-bs-target", "").lstrip("#")
        pid = re.sub(r"^offcanvas-(\d+)-.*$", r"\1", tgt)
        img = c.select_one("img[alt]")
        name = re.sub(r"\s+logo$", "", clean(img["alt"]) or "", flags=re.I) if img else None
        tag = c.select_one(".card-text")
        oc = soup.find(id=tgt)
        site = desc = None
        team = []
        if oc:
            for a in oc.select(".project-links a[href^=http]"):
                if not is_social(a["href"]):
                    site = a["href"]; break
            ab = oc.select_one(".about")
            desc = clean(ab.get_text(" ", strip=True)) if ab else None
            strs = [clean(x) for x in oc.stripped_strings]
            if "Team" in strs:
                i = strs.index("Team") + 1
                while i < len(strs) and strs[i] not in ("Latest News", "Milestones"):
                    team.append(strs[i]); i += 1
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       tagline=clean(tag.get_text(" ", strip=True)) if tag else None,
                       fund=", ".join(funds.get(pid, [])) or None, team=team))
    finish(out, "algebra", ("description", "company_url", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
