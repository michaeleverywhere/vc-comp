#!/usr/bin/env python3
"""CincyTech portfolio scraper -> cincytech_companies.json
Source: https://cincytechusa.com/portfolio — CincyTech (Cincinnati, OH), seed-stage venture investor in Southwest Ohio
technology and life-science companies. The portfolio page lists every company as a logo card linking to its website
with a one-line description, split into Tech / Life Sciences and Active / Acquired-IPO tabs. Cards carry no plain-text
name, so the name is the site-authored logo file label, kept only when it spells the website domain."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://cincytechusa.com/portfolio"
PRIMARY = "CincyTech"
SECT = {"Tech": "Tech", "LS": "Life Sciences"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    info = {}
    for lst in s.select(".w-dyn-list"):
        tab = lst.find_parent(attrs={"data-w-tab": True})
        t = tab.get("data-w-tab") if tab else ""
        grp, _, sub = t.partition("_")
        for a in lst.select(".w-dyn-item a[href^=http]"):
            h = a["href"]
            if is_social(h):
                continue
            d = info.setdefault(h, {"a": a, "sect": set(), "st": None})
            if grp in SECT:
                d["sect"].add(SECT[grp])
            if sub == "active":
                d["st"] = "active"
            elif sub == "AcquiredIPO":
                d["st"] = "acquired/IPO"
    out, seen = [], set()
    for h, d in info.items():
        a = d["a"]
        img = a.find("img")
        name = label_name(file_label(img.get("src")) if img else None, h)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        ht = a.select_one(".hover_text_about")
        desc = clean(ht.get_text(" ", strip=True)) if ht else None
        out.append(rec(nice(name), desc, h, PRIMARY, SOURCE_URL, scraped_at, sectors=sorted(d["sect"]),
                       status=d["st"]))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} CincyTech companies")
    finish(out, "cincytech", ("description", "company_url", "status", "sectors", "everywhere_tags"))


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
