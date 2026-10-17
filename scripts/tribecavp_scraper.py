#!/usr/bin/env python3
"""Tribeca Venture Partners portfolio scraper -> tribecavp_companies.json
Source: https://tribecavp.com/companies/ — WordPress (WPGraphQL); the page embeds the
full company list as JSON in its Alpine.js companyList({companies: [...]}) block:
name, about text, website (display-icon social link), location, status (Active /
Exited, from the status taxonomy term or the IPO/Acquired badge), first-investment date
and round (funding round at entry), capital raised (when published), sectors,
leadership names and the Tribeca investment team."""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social, html_text
from _d50_common import rec, finish

SOURCE_URL = "https://tribecavp.com/companies/"
PRIMARY = "Tribeca Venture Partners"
SECTOR_MAP = {"digital health": ["Health"], "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
              "cybersecurity": ["Cybersecurity"], "proptech": ["PropTech"], "real estate": ["PropTech"],
              "marketplaces": ["Consumer"], "consumer": ["Consumer"], "edtech": ["Future of Work"],
              "media": ["Gaming / Media / Entertainment"], "adtech": ["Gaming / Media / Entertainment"],
              "saas": ["Dev Tools / Cloud"], "logistics": ["Logistics / Supply Chain"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8", "replace")
    i = html.find("companies: [")
    if i < 0:
        raise SystemExit("FATAL: embedded companies JSON not found")
    rows, _ = json.JSONDecoder().raw_decode(html, html.index("[", i))
    out = []
    for c in rows:
        name = html_text(c.get("title"))
        if not name:
            continue
        d = c.get("companyDetails") or {}
        site = next((l.get("url") for l in (d.get("socialLinks") or [])
                     if "display" in (l.get("type") or "") or "globe" in (l.get("type") or "")), None)
        if site and is_social(site):
            site = None
        terms = c.get("postTaxTerms") or []
        badge = html_text(d.get("status"))
        status = ("exited" if "exited" in terms else "active")
        if badge and re.search(r"\bacq", badge, re.I):
            status = "acquired"
        elif badge and re.search(r"ipo|public|nasdaq|nyse", badge, re.I):
            status = "public"
        fid = clean(d.get("firstInvestmentDate"))
        y = re.search(r"\b(19|20)\d{2}\b", fid or "")
        sectors = [html_text(n.get("name")) for n in ((c.get("companySectors") or {}).get("nodes") or [])]
        rounds = [html_text(n.get("name")) for n in ((c.get("companyFirstInvestments") or {}).get("nodes") or [])]
        team = [clean(f"{(t.get('teamMemberDetails') or {}).get('firstName') or ''} {(t.get('teamMemberDetails') or {}).get('lastName') or ''}")
                for t in (d.get("investmentTeam") or [])]
        out.append(rec(name, html_text(d.get("about")), site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[s for s in sectors if s], sector_map=SECTOR_MAP, location=clean(d.get("location")),
                       stage=", ".join(r for r in rounds if r) or None, first_investment_date=fid,
                       first_invested=int(y.group(0)) if y else None, capital_raised=clean(d.get("capitalRaised")),
                       exit_note=badge, status=status,
                       leadership=[clean(p.get("name")) for p in (d.get("companyLeadership") or []) if clean(p.get("name"))],
                       investment_team=[t for t in team if t]))
    finish(out, "tribecavp", ("description", "company_url", "stage", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
