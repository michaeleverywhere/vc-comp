#!/usr/bin/env python3
"""Clarevia Capital portfolio scraper -> clareviacapital_companies.json
Source: https://www.clarevia.com/our-portfolio/ — Clarevia Capital (Madison, WI; formerly Venture Investors), healthcare
venture firm investing in pharma, diagnostics, medical devices and digital health. The portfolio gallery has one link
per company carrying the company name (data-name), category (pharma / diagnostics / devices / digital), status
(active / exit), a one-line description with the company's city in parentheses, and the company website."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.clarevia.com/our-portfolio/"
PRIMARY = "Clarevia Capital"
CATS = {"pharma": "Pharma", "diagnostics": "Diagnostics", "devices": "Devices", "digital": "Digital Health"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in s.select("a.galleryItemLink[data-name]"):
        name = clean(a.get("data-name"))
        if not name:
            continue
        if name == name.lower():
            name = clean(name.replace("-", " ")).title()
        p = a.select_one(".hoverInfo p")
        txt = clean(p.get_text(" ", strip=True)) if p else None
        loc = exit_note = acquirer = None
        m = re.search(r"\(([^()]+)\)\s*$", txt or "")
        if m:
            par = clean(m.group(1))
            txt = clean(txt[: m.start()])
            if re.match(r"(?i)a(c)?quired|ipo\b", par):
                exit_note = par
                am = re.match(r"(?i)a(c)?quired by\s+(.+)", par)
                if am and am.group(2).lower() != "undisclosed":
                    acquirer = clean(am.group(2))
            else:
                loc = par
        st = (a.get("data-status") or "").lower()
        cats = [CATS.get(c.strip(), c.strip().title()) for c in (a.get("data-category") or "").split(",") if c.strip()]
        href = a.get("href") if (a.get("href") or "").startswith("http") else None
        if href and "sante.com" in href:
            href = None
        out.append(rec(name, txt, href, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, location=loc, exit_note=exit_note, acquirer=acquirer,
                       status="exited" if st.startswith("exit") else ("active" if st == "active" else None)))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Clarevia companies")
    finish(out, "clareviacapital", ("description", "company_url", "status", "location", "exit_note", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
