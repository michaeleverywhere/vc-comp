#!/usr/bin/env python3
"""UA Venture Capital portfolio scraper -> uaventurecapital_companies.json
Source: https://uaventurecap.com/portfolio — portfolio page rendered client-side (read via headless Chrome): one element per company
(h2.fusion-title-heading.title-heading-left) — company name (site-authored card heading text), website where linked, and the card's one-line description where published."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://uaventurecap.com/portfolio"
PRIMARY = "UA Venture Capital"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=3000), "html.parser")
    for t in s(["script", "style", "noscript", "header", "nav", "footer"]):
        t.decompose()
    sel = 'h2.fusion-title-heading.title-heading-left'
    dom_of = lambda u: re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0].lower())
    ok = lambda u: u.startswith("http") and 'uaventurecap' not in dom_of(u) and not is_social(u) and not re.search(r'google|wix|webflow|squarespace|wordpress|hubspot|typeform|calendly|bit\\.ly|goo\\.gl|cookiebot|onetrust|vimeo|spotify|substack|notion\\.site|docs\\.|forms\\.|mailchimp|eepurl|techcrunch|forbes|bloomberg|reuters|wsj|businesswire|prnewswire|ft\\.com|cnbc|axios|nytimes|fortune|sifted|eu-startups|crunchbase|carta|anglehq|wikipedia', dom_of(u))
    for el in s.select(sel):
        if 'head' != "alt" and el.find(["div", "p", "h1", "h2", "h3", "h4", "h5", "h6"]):
            continue
        nm = clean(el.get("alt")) if 'head' == "alt" else txt(el)
        nm = clean(re.sub(r"(?i)[\s_-]*(logo|logotype|icon)(\.\w+)?\s*$", "", nm or ""))
        if not nm or len(nm) > 50 or len(nm.split()) > 6 or re.compile(r'(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|lp login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|exited|acquired|ipo|stealth)\\b|^\\W+$|https?://').search(nm):
            continue
        card = el
        while card.parent is not None and card.parent.name not in ("body", "html", "[document]") and len(card.parent.select(sel)) == 1:
            card = card.parent
        web = None
        for a in ([card] if card.name == "a" else []) + card.find_all("a", href=True):
            h = (a.get("href") or "").strip()
            if ok(h):
                web = h
                break
        desc = None
        if True:
            cands = [clean(x.get_text(" ", strip=True)) for x in card.find_all(["p", "div", "span"]) if not x.find(["p", "div"])]
            cands = [c for c in cands if c and c != nm and 25 <= len(c) <= 400 and not re.match(r"(?i)^(visit|website|learn more|read more)", c)]
            desc = max(cands, key=len) if cands else None
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at))

    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    out = [r for r in out if r["company_name"] and not re.search('(?i)^(https?://|ps://|www\\.)', r["company_name"])]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]
    finish(out, "uaventurecapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
