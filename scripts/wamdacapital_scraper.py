#!/usr/bin/env python3
"""Wamda Capital portfolio scraper -> wamdacapital_companies.json
Source: https://wamdacapital.com/ — portfolio page via chrome-dom; company name + website where published."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://wamdacapital.com/"
PRIMARY = "Wamda Capital"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(dom(url, 15000, min_len=3000), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []

    s = soup_of(SOURCE_URL)
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    host = 'wamdacapital'
    skipdom = re.compile(r"google|wix|webflow|squarespace|wordpress|hubspot|typeform|calendly|bit\.ly|goo\.gl|cookiebot|onetrust|vimeo|spotify|substack|notion\.site|docs\.|forms\.|mailchimp|eepurl|techcrunch|forbes|bloomberg|reuters|wsj|businesswire|prnewswire|ft\.com|cnbc|axios|nytimes|fortune|sifted|eu-startups|crunchbase|carta|anglehq|wikipedia|junipersquare|arkpes|altareturn|getproven|sec\.gov|trustpilot|jotform|medium\.com")
    bad_first = re.compile(r"(?i)^(learn|visit|website|read|view|more|here|click|see|explore|open|login|apply|contact|home|about|news|blog|jobs|careers|menu|privacy|terms|portfolio|company|companies)$")
    skipre = re.compile(r"(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|lp login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|acquired|ipo)\b|^\W+$|https?://|\.(com|io|ai|co|vc)$")
    dom = lambda u: re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0].lower())
    ok = lambda u: u.startswith("http") and host not in dom(u) and not is_social(u) and not skipdom.search(dom(u))
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
        for i in card.find_all("img", alt=True):
            v = clean(re.sub(r"(?i)[\s_-]*(logo|logotype|icon)(\.\w+)?\s*$", "", i.get("alt") or ""))
            if v and ":" in v:
                v = v.split(":", 1)[0].strip()
            if v and 1 < len(v) <= 40 and len(v.split()) <= 5 and not skipre.search(v) and not bad_first.search(v):
                nm = v
                break
        if not nm:
            h = card.select_one("h1, h2, h3, h4, h5, h6, [class*=title], [class*=name], strong")
            if h:
                t = txt(h)
                if t and len(t) <= 40 and len(t.split()) <= 5 and not skipre.search(t) and not bad_first.search(t):
                    nm = t
        if not nm:
            for x in al:
                t = clean(x.get_text(" ", strip=True))
                if not t:
                    continue
                first = re.sub(r"[^A-Za-z0-9+.&-]+$", "", t.split()[0])
                if 2 <= len(first) <= 30 and not bad_first.search(first) and not skipre.search(first):
                    nm = first
                    break
        if not nm:
            stem = d.split(".")[0]
            if stem and not re.search(r"^(www|app|web|home|login|careers|shop|store|blog|news|support|help|docs|go|get|try|join|use|hi|my|the)$", stem):
                nm = stem[0].upper() + stem[1:] if stem.islower() else stem
        if not nm or len(nm) > 50:
            continue
        desc = None
        cands = [clean(x.get_text(" ", strip=True)) for x in card.find_all(["p", "div", "span"]) if not x.find(["p", "div"])]
        cands = [c for c in cands if c and c != nm and 25 <= len(c) <= 400 and not re.match(r"(?i)^(visit|website|learn more|read more)", c)]
        if cands:
            desc = max(cands, key=len)
        out.append(rec(nm, desc, a["href"].strip().split("?")[0], PRIMARY, SOURCE_URL, scraped_at))
    out = [r for r in out if r["company_name"] and not re.search(r"(?i)^(https?://|ps://|www\.)", r["company_name"])]
    out = [r for r in out if host not in (r["company_name"] or "").lower().replace(" ", "")]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]

    finish(out, "wamdacapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
