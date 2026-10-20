#!/usr/bin/env python3
"""Grit Road portfolio scraper -> gritroad_companies.json
Source: https://gritrd.com/portfolio — portfolio page: one card per external company link — company name (site-authored
logo alt text), website where published."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://gritrd.com/portfolio"
PRIMARY = "Grit Road"


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
    s = soup_of(SOURCE_URL)
    for t in s(["script", "style", "noscript", "header", "nav", "footer"]):
        t.decompose()
    dom = lambda u: re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0].lower())
    ok = lambda u: u.startswith("http") and 'gritrd' not in dom(u) and not is_social(u) and not re.search(r'google|wix|webflow|squarespace|wordpress|hubspot|typeform|calendly|bit\\.ly|goo\\.gl|cookiebot|onetrust|vimeo|spotify|substack|notion\\.site|docs\\.|forms\\.|mailchimp|eepurl|techcrunch|forbes|bloomberg|reuters|wsj|businesswire|prnewswire|ft\\.com|cnbc|axios|nytimes|fortune|sifted|eu-startups|crunchbase|carta|anglehq|wikipedia', dom(u))
    links = [a for a in s.find_all("a", href=True) if ok(a["href"].strip())]
    byd = {}
    for a in links:
        byd.setdefault(dom(a["href"].strip()), []).append(a)
    for d, al in byd.items():
        a = al[0]
        card = a
        while card.parent is not None and card.parent.name not in ("body", "html", "[document]"):
            ds = {dom(x["href"].strip()) for x in card.parent.find_all("a", href=True) if ok(x["href"].strip())}
            if ds - {d}:
                break
            card = card.parent
        nm = None
        if 'alt' == "head":
            h = card.select_one("h1, h2, h3, h4, h5, h6, [class*=title], [class*=name], strong")
            nm = txt(h)
        elif 'alt' == "alt":
            for i in card.find_all("img", alt=True):
                v = clean(re.sub(r"(?i)[\s_-]*(logo|logotype|icon)(\.\w+)?\s*$", "", i.get("alt") or ""))
                if v:
                    nm = v
                    break
        else:
            nm = clean(max((x.get_text(" ", strip=True) for x in al), key=len))
        if not nm or len(nm) > 50 or len(nm.split()) > 6 or re.compile(r'(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|lp login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|acquired|ipo)\\b|^\\W+$|https?://|\\.(com|io|ai|co|vc)$').search(nm):
            continue
        desc = None
        if False:
            cands = [clean(x.get_text(" ", strip=True)) for x in card.find_all(["p", "div", "span"]) if not x.find(["p", "div"])]
            cands = [c for c in cands if c and c != nm and 25 <= len(c) <= 400 and not re.match(r"(?i)^(visit|website|learn more|read more)", c)]
            desc = max(cands, key=len) if cands else None
        out.append(rec(nm, desc, a["href"].strip(), PRIMARY, SOURCE_URL, scraped_at))

    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    out = [r for r in out if r["company_name"] and not re.search('(?i)^(https?://|ps://|www\\.)', r["company_name"])]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]
    finish(out, "gritroad", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
