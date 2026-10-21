#!/usr/bin/env python3
"""JAFCO Group portfolio scraper -> jafco_companies.json
Source: https://www.jafco.co.jp/english/portfolio/ — English portfolio list rendered client-side (read via
headless Chrome, pressing the page's own view-more button until the list is complete): one
card per company — English company name, JAFCO's status badge (IPO / M&A / ...), category and initial
investment year; each company page adds the business description, website and the IPO / M&A date
where published."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, fetch_many, is_social
from _d50_common import rec, finish
from _chrome_jsclick import dom_jsclick

SOURCE_URL = "https://www.jafco.co.jp/english/portfolio/"
PRIMARY = "JAFCO Group"
LABELS = ("Category", "Initial investment", "IPO Date", "M&A Date", "Investment Professional", "Back to the list", "Company website")


def after(strings, label):
    if label not in strings:
        return []
    i, vals = strings.index(label) + 1, []
    while i < len(strings) and strings[i] not in LABELS:
        vals.append(strings[i]); i += 1
    return vals


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = dom_jsclick(SOURCE_URL, "document.querySelector('button.PortfolioList-viewMore')",
                       "document.querySelectorAll('li.PortfolioItem').length")
    s = BeautifulSoup(html, "html.parser")
    items = []
    for li in s.select("li.PortfolioItem"):
        en = li.select_one(".PortfolioItem-title .-en")
        name = clean(en.get_text(" ", strip=True)) if en else None
        if not name:
            continue
        a = li.select_one("a.PortfolioItem-link[href]")
        st = li.select_one(".PortfolioItem-status")
        cat = li.select_one(".PortfolioItem-coverText.category")
        cats = [clean(x) for x in (cat.get_text("\n").split("\n") if cat else []) if clean(x)]
        yr = None
        for c in li.select(".PortfolioItem-coverCont"):
            t = c.select_one(".PortfolioItem-coverTitle")
            if t and clean(t.get_text()) == "Initial Investment":
                v = c.select_one(".PortfolioItem-coverText")
                yr = clean(v.get_text(" ", strip=True)) if v else None
        items.append((name, urljoin(SOURCE_URL, a["href"]) if a else None, clean(st.get_text(" ", strip=True)) if st else None, cats, yr))
    pages = fetch_many([u for _, u, _, _, _ in items if u], workers=4, pause=0.3)
    out = []
    for name, u, st, cats, yr in items:
        desc = web = exit_date = None
        h = pages.get(u) if u else None
        if h:
            d = BeautifulSoup(h, "html.parser")
            for t in d(["script", "style", "header", "footer", "nav"]):
                t.decompose()
            m = d.select_one("main") or d
            strs = [clean(x) for x in m.stripped_strings if clean(x)]
            cv = after(strs, "Category")
            cv = [x for x in cv if x not in cats]
            desc = cv[-1] if cv else None
            for lab in ("IPO Date", "M&A Date"):
                v = after(strs, lab)
                if v:
                    exit_date = v[0]
            for a in m.select("a[href^=http]"):
                if clean(a.get_text(" ", strip=True)) == "Company website" and not is_social(a["href"]):
                    web = a["href"].strip(); break
        status = "acquired" if st and re.search(r"IPO|M&A", st) else None
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, jafco_status=st,
                       exit_date=exit_date, first_invested=yr, status=status, profile_url=u))
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} JAFCO companies")
    finish(out, "jafco", ("description", "company_url", "sectors", "first_invested", "exit_date", "everywhere_tags"))


if __name__ == "__main__":
    main()
