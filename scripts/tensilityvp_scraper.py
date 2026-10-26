#!/usr/bin/env python3
"""Tensility Venture Partners portfolio scraper -> tensilityvp_companies.json
Source: https://tensilityvc.com/portfolio — Tensility Venture Partners (Chicago), seed / early-stage venture firm
investing in AI, data and enterprise software. The Squarespace portfolio gallery shows one logo per company linking to
its website with a one-line caption; the Exits gallery captions give the
acquirer or IPO. Tiles carry no plain-text name, so the name is taken from the caption or the
site-authored logo file label when it spells the website domain; other tiles are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://tensilityvc.com/portfolio"
PRIMARY = "Tensility Venture Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for fig in s.select("figure"):
        a = fig.select_one("a.gallery-grid-image-link[href]")
        if not a:
            continue
        hd = fig.find_previous(string=re.compile(r"^\s*(Active Investments:|Exits\s*$)"))
        hd = clean(hd.find_parent(["h1", "h2", "h3", "h4", "p"]).get_text(" ", strip=True)) if hd and hd.find_parent(["h1", "h2", "h3", "h4", "p"]) else (clean(hd) or "")
        cap = fig.select_one(".gallery-caption-content")
        desc = clean(cap.get_text(" ", strip=True)) if cap else None
        img = a.find("img")
        lab = file_label(img.get("data-src") or img.get("src")) if img else None
        href = a["href"] if a["href"].startswith("http") and not is_social(a["href"]) else None
        if hd == "Exits":
            if not lab or re.match(r"(?i)screenshot", lab):
                continue
            own = label_name(lab, href) if href else None
            name = own or lab
            acq = None
            m = re.search(r"Sold to (.+)$", desc or "")
            if m:
                acq = clean(m.group(1))
            ipo = desc if re.match(r"IPO", desc or "") else None
            extra = dict(status="exited", exit_note=desc, acquirer=acq)
            if ipo:
                extra["status"] = "IPO"
            url, d = (href if own else None), None
        else:
            if not href or "tensility" in href:
                continue
            name = phrase_in([desc or ""], href) or label_name(lab, href)
            m = re.match(r"Active Investments:\s*(.+)", hd)
            extra = dict(status="active")
            url, d = href, desc
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(nice(name), d, url, PRIMARY, SOURCE_URL, scraped_at, **extra))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Tensility companies")
    finish(out, "tensilityvp", ("description", "company_url", "status", "exit_note", "everywhere_tags"))


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
