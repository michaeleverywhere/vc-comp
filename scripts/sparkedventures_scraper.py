#!/usr/bin/env python3
"""Sparked Ventures portfolio scraper -> sparkedventures_companies.json
Source: https://www.sparked.vc/portfolio — static HTML heading/table extract; company name + website where published."""
import os, re, sys, requests
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://www.sparked.vc/portfolio"
PRIMARY = "Sparked Ventures"
SKIP_NAME = re.compile(r"(?i)^(portfolio|companies|investments?|our companies|active|exited|team|about|news|blog|contact|home|careers|privacy|terms|all|filters?|sectors?|learn more|read more|view|see all|load more|menu|login|apply|subscribe|cookie)$")
BAD = re.compile(r"(?i)(cookie|trustpilot|logo with|logo design|wordmark|privacy policy)")

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    host = urlparse(r.url).netloc.replace("www.", "")
    s = BeautifulSoup(r.text, "html.parser")
    for t in s(["script", "style", "noscript", "nav", "footer", "header"]):
        t.decompose()
    out = []; seen = set()
    for h in s.select("h1,h2,h3,h4,h5,[class*=company],[class*=portfolio-title],[class*=card-title]"):
        nm = clean(h.get_text(" ", strip=True))
        if not nm or len(nm) > 45 or len(nm.split()) > 6: continue
        if SKIP_NAME.search(nm) or BAD.search(nm): continue
        if nm.lower() in seen: continue
        seen.add(nm.lower())
        url = None
        card = h
        for _ in range(4):
            if card.parent: card = card.parent
        for a in card.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("/") and not href.startswith("//"):
                href = f"https://{host}{href}"
            if href.startswith("http") and not is_social(href) and host.split(".")[-2] not in urlparse(href).netloc:
                url = href; break
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    for tr in s.select("table tr"):
        tds = tr.find_all(["td", "th"])
        if not tds: continue
        nm = clean(tds[0].get_text(" ", strip=True))
        if not nm or len(nm) > 45 or SKIP_NAME.search(nm) or BAD.search(nm): continue
        if nm.lower() in seen: continue
        seen.add(nm.lower())
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "sparkedventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
