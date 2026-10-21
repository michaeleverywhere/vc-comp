#!/usr/bin/env python3
"""TVM Capital Life Science portfolio scraper -> tvmcapitallifescience_companies.json
Source: https://tvm-capital.com/portfolio-companies — portfolio list linking one detail page per company; each detail page gives the company name
(page heading), its website (the outbound link matching the company name) and a one-line description where published."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://tvm-capital.com/portfolio-companies"
PRIMARY = "TVM Capital Life Science"


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
    pat = re.compile(r'^/portfolio/[^/]+$', re.I)
    dom = lambda u: re.sub(r"^www\.", "", u.split("/")[2].lower()) if u.count("/") >= 2 else ""
    links = {}
    for a in s.find_all("a", href=True):
        u = urljoin(SOURCE_URL, a["href"].strip()).split("#")[0].split("?")[0].rstrip("/")
        if not u.startswith("http") or 'tvm-capital' not in dom(u):
            continue
        if pat.search("/" + u.split("/", 3)[3] if u.count("/") >= 3 else "/"):
            links.setdefault(u, txt(a))
    pages = fetch_many(list(links), workers=6)
    skipdom = re.compile(r'google|wix|webflow|squarespace|wordpress|hubspot|typeform|calendly|bit\\.ly|goo\\.gl|cookiebot|onetrust|vimeo|spotify|substack|notion\\.site|docs\\.|forms\\.|mailchimp|eepurl|techcrunch|forbes|bloomberg|reuters|wsj|businesswire|prnewswire|ft\\.com|cnbc|axios|nytimes|fortune|sifted|eu-startups|crunchbase|carta|anglehq|wikipedia')
    rows = []
    for u, atext in links.items():
        h = pages.get(u)
        if not h:
            continue
        d = BeautifulSoup(h, "html.parser")
        md = d.find("meta", attrs={"name": "description"}) or d.find("meta", attrs={"property": "og:description"})
        mdv = clean(md.get("content")) if md and md.get("content") else None
        og = d.find("meta", attrs={"property": "og:title"})
        ogv = clean(og.get("content")) if og and og.get("content") else None
        for t in d(["script", "style", "noscript", "header", "nav", "footer"]):
            t.decompose()
        sl = re.sub(r"[^a-z0-9]", "", re.sub(r"-\d+$", "", u.rstrip("/").split("/")[-1].lower()))
        nm = None
        for c in [txt(x) for x in d.find_all(["h1", "h2", "h3", "h4", "strong"])] + [clean(re.split(r"\s+[|–—-]\s+", ogv)[0]) if ogv else None, clean(re.split(r"\s+[|–—-]\s+", d.title.get_text())[0]) if d.title else None, atext]:
            cn = re.sub(r"[^a-z0-9]", "", (c or "").lower())
            if c and len(c) <= 60 and len(c.split()) <= 7 and len(cn) > 1 and c.lower() not in PRIMARY.lower() and (cn[:4] == sl[:4] or cn in sl or sl in cn):
                nm = c
                break
        if not nm:
            nm = txt(d.find("h1"))
        if nm and (nm.lower() in PRIMARY.lower() or re.match(r"(?i)^(led |pre-?seed|seed|series [a-z]|exited|active|portfolio|our portfolio)\b", nm)):
            nm = None
        if not nm or len(nm) > 60 or len(nm.split()) > 7:
            nm = atext if atext and len(atext) <= 50 and len(atext.split()) <= 6 and not re.compile(r'(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|lp login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|acquired|ipo|details?|open project|project insights|profile|discover more|know more|page not found|404|our portfolio|portfolio companies|companies|investments|seed|series [a-z]|pre-seed|led|company logo|portfolio company logo)\\b|^\\W+$|https?://').search(atext) else None
        if not nm and ogv:
            nm = clean(re.split(r"\s+[|–—-]\s+", ogv)[0])
        if not nm or len(nm) > 60 or re.compile(r'(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|lp login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|acquired|ipo|details?|open project|project insights|profile|discover more|know more|page not found|404|our portfolio|portfolio companies|companies|investments|seed|series [a-z]|pre-seed|led|company logo|portfolio company logo)\\b|^\\W+$|https?://').search(nm):
            continue
        core = re.sub(r"[^a-z0-9]", "", nm.lower())
        ext = [a["href"].strip() for a in d.find_all("a", href=True) if a["href"].strip().startswith("http")
               and 'tvm-capital' not in dom(a["href"].strip()) and not is_social(a["href"]) and not skipdom.search(dom(a["href"].strip()))]
        web = None
        for e in ext:
            b = re.sub(r"[^a-z0-9]", "", dom(e).split(".")[0])
            if len(core) > 1 and len(b) > 1 and (core[:5] in b or b[:5] in core):
                web = e
                break
        paras = [txt(p) for p in d.find_all("p")]
        paras = [p for p in paras if p and 40 <= len(p) <= 600]
        rows.append([nm, mdv, paras, web])
    from collections import Counter
    mc = Counter(r[1] for r in rows if r[1])
    pc = Counter(p for r in rows for p in set(r[2]))
    nc = Counter(r[0].lower() for r in rows)
    for nm, mdv, paras, web in rows:
        if nc[nm.lower()] > 2:
            continue
        desc = mdv if mdv and mc[mdv] == 1 and 25 <= len(mdv) <= 600 else None
        if not desc:
            uniq = [p for p in paras if pc[p] == 1]
            desc = uniq[0] if uniq else None
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at))

    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    out = [r for r in out if r["company_name"] and not re.search('(?i)^(https?://|ps://|www\\.)', r["company_name"])]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]
    finish(out, "tvmcapitallifescience", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
