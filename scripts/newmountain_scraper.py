#!/usr/bin/env python3
"""New Mountain Capital portfolio scraper -> newmountain_companies.json
Source: https://www.newmountaincapital.com/our-strategies/private-equity/portfolio/
— WP REST `nmc-portfolio` post type (name, content = company description and
website link) with the `portfolio-status` taxonomy (Current Private Equity
Flagship Control / Current Strategic Equity / Legacy continuation / Fully Realized).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, is_social, clean
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://www.newmountaincapital.com"
SOURCE_URL = ORIGIN + "/our-strategies/private-equity/portfolio/"
PRIMARY = "New Mountain Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    st = {k: clean((v or "").replace("\\n", " ")) for k, v in wp_terms(ORIGIN, "portfolio-status").items()}
    out = []
    for p in wp_all(ORIGIN, "nmc-portfolio"):
        html = p.get("content", {}).get("rendered") or ""
        soup = BeautifulSoup(html, "html.parser")
        site = next((a["href"] for a in soup.select("a[href^=http]")
                     if "newmountaincapital.com" not in a["href"] and not is_social(a["href"])), None)
        for a in soup.select("a[href^=http]"):
            if a.get_text(" ", strip=True).lower().startswith(("http", "www", "visit")):
                a.decompose()
        status = next((st[i] for i in p.get("portfolio-status") or [] if i in st), None)
        norm = None
        if status:
            norm = "realized" if status.lower().startswith("fully realized") else "active" if status.lower().startswith("current") else None
        out.append(rec(html_text(p["title"]["rendered"]), html_text(str(soup)), site, PRIMARY, SOURCE_URL, scraped_at,
                       portfolio_status=status, status=norm, detail_url=p.get("link")))
    finish(out, "newmountain", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
