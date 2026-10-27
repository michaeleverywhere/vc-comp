#!/usr/bin/env python3
"""Deciens Capital portfolio scraper -> decienscapital_companies.json
Source: https://deciens.com/companies — chrome-dom smart link-harvest; company name + website where published."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://deciens.com/companies"
PRIMARY = "Deciens Capital"
HOST = "deciens.com"
MODE = "alt"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    html = dom(SOURCE_URL, 18000, min_len=2000)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript", "header", "nav", "footer"]):
        t.decompose()
    skipdom = re.compile(r"google|wix|webflow|squarespace|wordpress|hubspot|typeform|calendly|bit\.ly|goo\.gl|cookiebot|onetrust|vimeo|spotify|substack|notion\.site|docs\.|forms\.|mailchimp|eepurl|techcrunch|forbes|bloomberg|reuters|wsj|businesswire|prnewswire|ft\.com|cnbc|axios|nytimes|fortune|sifted|eu-startups|crunchbase|carta|anglehq|wikipedia|junipersquare|arkpes|altareturn|getproven|sec\.gov|trustpilot|jotform|medium\.com")
    skipre = re.compile(r"(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|lp login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|acquired|ipo)\b|^\W+$|https?://|\.(com|io|ai|co|vc)$")
    bad_first = re.compile(r"(?i)^(learn|visit|website|read|view|more|here|click|see|explore|open|login|apply|contact|home|about|news|blog|jobs|careers|menu|privacy|terms|portfolio|company|companies)$")
    domn = lambda u: re.sub(r"^www\.", "", re.sub(r"^https?://", "", u).split("/")[0].lower())
    ok = lambda u: u.startswith("http") and HOST not in domn(u) and not is_social(u) and not skipdom.search(domn(u))
    links = [a for a in s.find_all("a", href=True) if ok(a["href"].strip())]
    byd = {}
    for a in links:
        byd.setdefault(domn(a["href"].strip()), []).append(a)
    for d, al in byd.items():
        a = al[0]
        card = a
        while card.parent is not None and card.parent.name not in ("body", "html", "[document]"):
            ds = {domn(x["href"].strip()) for x in card.parent.find_all("a", href=True) if ok(x["href"].strip())}
            if ds - {d}:
                break
            card = card.parent
        nm = None
        if MODE == "alt":
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
                if 1 < len(t) <= 40 and len(t.split()) <= 5 and not skipre.search(t) and not bad_first.search(t):
                    nm = t
                    break
        if not nm:
            continue
        desc = None
        cands = [clean(x.get_text(" ", strip=True)) for x in card.find_all(["p", "div", "span"]) if not x.find(["p", "div"])]
        cands = [c for c in cands if c and c != nm and 25 <= len(c) <= 400 and not re.match(r"(?i)^(visit|website|learn more|read more)", c)]
        desc = max(cands, key=len) if cands else None
        out.append(rec(nm, desc, a["href"].strip(), PRIMARY, SOURCE_URL, scraped_at))
    # dedupe
    seen = set(); uniq = []
    for r in out:
        k = (r.get("company_name") or "").lower()
        if not k or k in seen:
            continue
        seen.add(k); uniq.append(r)
    finish(uniq, "decienscapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
