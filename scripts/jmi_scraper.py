#!/usr/bin/env python3
"""JMI Equity portfolio scraper -> jmi_companies.json
Source: https://jmi.com/portfolio/ — WP page: #results .item logo tiles whose CSS
classes carry current/prior + sector filters, each followed by a popup with name,
description, "Status:" (Acquired by / IPO), website and JMI deal team.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://jmi.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "jmi_companies.json")
PRIMARY = "JMI Equity"
SECTOR_LABELS = {
    "government-nonprofit": "Government & Nonprofit", "sales-marketing": "Sales & Marketing",
    "education": "Education", "healthcare-information-technology": "Healthcare IT",
    "security-compliance": "Security & Compliance", "energy-utilities": "Energy, Utilities, & Real Estate",
    "human-resources": "Human Resources", "workforce-management": "Workforce Management",
    "financial-services-insurance": "Finance, Insurance, & Legal", "it-infrastructure": "IT & Infrastructure",
    "field-service-management": "Field Service Management", "cloud": "Cloud",
}
SECTOR_TAG_MAP = {
    "government & nonprofit": ["RegTech/Gov/Legal"], "healthcare it": ["Health"],
    "security & compliance": ["Cybersecurity"], "human resources": ["Future of Work"],
    "workforce management": ["Future of Work"], "finance, insurance, & legal": ["FinTech / Insurance"],
    "it & infrastructure": ["Dev Tools / Cloud"], "sales & marketing": [], "education": [], "cloud": [],
    "energy, utilities, & real estate": [], "field service management": [],
}
TAG_OVERRIDES = {"CompanyCam": ["PropTech", "Future of Work"]}  # judgment pass (no LLM)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    root = soup.select_one("#results") or soup
    out, seen = [], set()
    for it in root.select(".item"):
        box = it.find_next_sibling(class_="popup-content-box")
        if not box:
            continue
        h2 = box.select_one("h2")
        img = it.select_one("img[alt]")
        name = clean(h2.get_text(" ")) if h2 else clean(img.get("alt") if img else None)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        txt = box.select_one(".text") or box
        desc = None
        for p in txt.find_all("p", recursive=False):
            if "jmi-team" in (p.get("class") or []) or p.find("a"):
                continue
            if clean(p.get_text(" ")):
                desc = clean(p.get_text(" "))
                break
        st = box.select_one(".status")
        status_txt = clean(re.sub(r"(?i)^\s*status:\s*", "", st.get_text(" "))) if st else None
        link = next((a["href"].strip() for a in txt.select("p a[href]") if "jmi.com" not in a["href"]), None)
        team = [clean(a.get_text(" ")) for a in box.select(".jmi-team a")]
        cls = it.get("class") or []
        sectors = [SECTOR_LABELS[c] for c in cls if c in SECTOR_LABELS]
        acquired = bool(status_txt and status_txt.lower().startswith("acquired"))
        acquirer = None
        if acquired:
            m = re.match(r"(?i)acquired by\s+(.+)", status_txt)
            acquirer = clean(m.group(1)) if m else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(link if link.startswith("http") else "http://" + link) if link else None,
            "sectors": sectors,
            "portfolio_group": "current" if "current" in cls else ("prior" if "prior" in cls else None),
            "status": "active" if "current" in cls and not status_txt else ("acquired" if acquired else None),
            "acquirer": acquirer,
            "exit_detail": status_txt,
            "partners": team,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
