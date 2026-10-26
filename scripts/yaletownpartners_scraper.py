#!/usr/bin/env python3
"""Yaletown Partners portfolio scraper -> yaletownpartners_companies.json
Source: https://www.yaletown.com/portfolio — Yaletown Partners (Vancouver / Calgary / Toronto), Canadian venture firm
investing in industrial-tech, data and climate software. The Webflow portfolio list shows one card per company with a
logo, a one-line description, the Yaletown fund and an exit callout ("Acquired by X"); each card links to a detail page
whose "Visit website" button gives the company website. Cards carry no name text, so the company name is the
site-authored logo file label, else the detail-page slug, kept only when it spells the website domain."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote, urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.yaletown.com/portfolio"
PRIMARY = "Yaletown Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for a in s.select("a.portfolio-link-block[href]"):
        href = urljoin(SOURCE_URL, a["href"])
        img = a.find("img")
        desc = a.select_one(".text-size-medium")
        fund = [clean(x.get_text()) for x in a.select('[fs-cmsfilter-field="fund"]') if clean(x.get_text())]
        call = a.select_one(".callout-text")
        cards.append((href, img.get("src") if img else None, clean(desc.get_text(" ", strip=True)) if desc else None,
                      fund, clean(call.get_text(" ", strip=True)) if call else None))
    pages = fetch_many([c[0] for c in cards]) if cards else {}
    out = []
    for href, src, desc, fund, call in cards:
        h = pages.get(href) if isinstance(pages, dict) else None
        web = None
        if h:
            d = BeautifulSoup(h, "html.parser")
            for b in d.select("a[href^=http]"):
                if "visit website" in b.get_text(" ", strip=True).lower() and not is_social(b["href"]):
                    web = b["href"]
                    break
            if not web:
                for b in d.select("a[href^=http]"):
                    if "yaletown" not in b["href"] and not is_social(b["href"]) and "webflow" not in b["href"]:
                        web = b["href"]
                        break
        lab = file_label(src)
        sl = href.rstrip("/").rsplit("/", 1)[-1].replace("-", " ")
        name = (nice(label_name(lab, web)) if label_name(lab, web) else None) or (nice(label_name(sl, web)) if label_name(sl, web) else None)
        if not name:
            continue
        acq = re.match(r"(?i)acquired by (.+)", call or "")
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, yaletown_fund=", ".join(fund) or None,
                       status="exited" if call and re.search(r"acquired|ipo|exit|merged", call, re.I) else "active",
                       exit_note=call, acquirer=acq.group(1) if acq else None, company_profile_url=href))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Yaletown companies")
    finish(out, "yaletownpartners", ("description", "company_url", "status", "everywhere_tags"))


norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
AFFIX_PRE = ("my", "run", "get", "try", "use", "join", "go", "hello", "the", "meet", "with", "hey")
AFFIX_SUF = ("hq", "app", "ai", "labs", "lab", "inc", "co", "io", "bio", "health", "tech", "hub", "official", "therapeutics", "group")


def domain_keys(url):
    """Domain label variants: full host, label, and label minus one common marketing prefix/suffix."""
    if not url:
        return set()
    host = urlparse(url if "//" in url else "http://" + url).netloc.lower().split(":")[0]
    host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
    lab = norm(host.split(".")[0])
    k = {norm(host), lab}
    for p in AFFIX_PRE:
        if lab.startswith(p) and len(lab) - len(p) >= 3:
            k.add(lab[len(p):])
    for s_ in AFFIX_SUF:
        if lab.endswith(s_) and len(lab) - len(s_) >= 3:
            k.add(lab[: -len(s_)])
    return {x for x in k if len(x) >= 2}


def spells(name, url):
    """True when the site-authored name spells the company's website domain (or its label)."""
    n, keys = norm(name), domain_keys(url)
    if not n or not keys:
        return False
    lab = max(keys, key=len)
    return n in keys or any(len(n) >= 4 and (k.startswith(n) or n.startswith(k)) and min(len(n), len(k)) >= 4 for k in keys)


def phrase_in(texts, url):
    """The phrase of the site's own text that spells the company's domain."""
    keys = domain_keys(url)
    for t in texts:
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.&+'’-]*", t or "")
        for i in range(len(toks)):
            for j in range(i + 1, min(i + 5, len(toks)) + 1):
                ph = re.sub(r"(['’]s|[.,:;'’-])+$", "", " ".join(toks[i:j]))
                if norm(ph) in keys:
                    return ph
    return None


def file_label(src):
    """Site-authored logo file name with size/format/colour suffixes removed."""
    f = unquote((src or "").split("?")[0].rsplit("/", 1)[-1]).replace("+", " ")
    f = re.sub(r"^[0-9a-f]{20,}[_-]", "", f)
    f = re.sub(r"^\d{10,}-[A-Z0-9]{16,}/?", "", f)
    f = re.sub(r"(-p-\d+)?(-\d+x\d+)?(-scaled)?\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    f = re.sub(r"\s*[\(\[].*?[\)\]]", "", f)
    f = re.sub(r"(?i)[\s_.-]*(logo|logotype|wordmark|white|black|color|colour|transparent|rgb|cmyk|horizontal|full|dark|light|primary|scaled|final|new|copy)\b.*$", "", f)
    f = re.sub(r"[_-]\d+$", "", f)
    return clean(re.sub(r"[_]+", " ", f).replace("-", " ").strip()) or None


def label_name(lab, url):
    """Shortest leading phrase of a site-authored label that spells the website domain (None if none does)."""
    if not lab or not url:
        return None
    keys = domain_keys(url)
    raw = [t for t in re.split(r"[\s+:]+", lab) if t]
    tk = lambda sd: [x for x in (re.sub(r"(?i)(?<=[a-z])logo\w*$" + (r"|\d+$" if sd else ""), "", t) for t in raw) if x]
    exact = lambda ph: norm(ph) in keys
    name_pre = lambda ph: len(norm(ph)) >= 4 and any(k.startswith(norm(ph)) and len(norm(ph)) >= 0.75 * len(k) for k in keys)
    dom_pre = lambda ph: any(len(k) >= 4 and norm(ph).startswith(k) and norm(ph)[len(k):].isdigit() for k in keys)
    for toks, test, rev in ((tk(False), exact, True), (tk(True), exact, True),
                            (tk(False), dom_pre, False)):
        order = range(len(toks), 0, -1) if rev else range(1, len(toks) + 1)
        for j in order:
            if test(" ".join(toks[:j])):
                return " ".join(toks[:j])
    return None


def nice(label):
    return " ".join(w[:1].upper() + w[1:] for w in label.split()) if label == label.lower() else label


if __name__ == "__main__":
    main()
