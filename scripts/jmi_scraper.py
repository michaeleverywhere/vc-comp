#!/usr/bin/env python3
"""JMI Equity portfolio scraper -> jmi_companies.json
Source: https://www.jmi.com/companies/ — WordPress grid: each item div carries
status (current/prior) and sector slugs as classes and is followed by a popup with
name, description, website and JMI team.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.jmi.com/companies/"
PRIMARY = "JMI Equity"
SECTORS = {"cloud": "Cloud", "sales-marketing": "Sales & Marketing", "healthcare-information-technology": "Healthcare IT",
           "security-compliance": "Security & Compliance", "it-infrastructure": "IT Infrastructure",
           "financial-services-insurance": "Financial Services & Insurance", "education": "Education",
           "government-nonprofit": "Government & Nonprofit", "human-resources": "Human Resources",
           "energy-utilities": "Energy & Utilities", "workforce-management": "Workforce Management",
           "field-service-management": "Field Service Management"}
SECTOR_MAP = {"healthcare it": ["Health"], "security & compliance": ["Cybersecurity"], "it infrastructure": ["Dev Tools / Cloud"],
              "cloud": ["Dev Tools / Cloud"], "financial services & insurance": ["FinTech / Insurance"], "education": ["Future of Work"],
              "government & nonprofit": ["RegTech/Gov/Legal"], "human resources": ["Future of Work"],
              "workforce management": ["Future of Work"], "energy & utilities": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select("#results div.item"):
        cls = it.get("class") or []
        pop = it.find_next_sibling(class_="popup-content-box")
        h = pop.find("h2") if pop else None
        name = clean(h.get_text(" ", strip=True)) if h else (it.img.get("alt") if it.img else None)
        desc, site, team = None, None, None
        if pop:
            for p in pop.select(".text > p"):
                a = p.find("a", href=True)
                if "jmi-team" in (p.get("class") or []):
                    team = ", ".join(clean(x.get_text()) for x in p.find_all("a")) or None
                elif a and a["href"].startswith("http") and "jmi.com" not in a["href"]:
                    site = site or a["href"]
                elif not desc:
                    desc = clean(p.get_text(" ", strip=True))
        status = "current" if "current" in cls else "prior" if "prior" in cls else None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[SECTORS[c] for c in cls if c in SECTORS], sector_map=SECTOR_MAP,
                       portfolio_status=status, status={"current": "active", "prior": "realized"}.get(status),
                       lead_partner=team))
    finish(out, "jmi", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
