#!/usr/bin/env python3
"""LiveOak Venture Partners portfolio scraper -> liveoakvp_companies.json
Source: https://www.liveoakvp.com/portfolio/ — LiveOak Venture Partners (Austin, TX), early-stage venture firm backing
Texas technology founders. The portfolio accordion (rendered with headless Chrome) shows, per company, the logo (alt
text carries the company name), a one-line description, status (Active / Acquired / IPO), stage, sector(s), key
dates, founders, the LiveOak partner(s) and a website link."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote, urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.liveoakvp.com/portfolio/"
PRIMARY = "LiveOak Venture Partners"


def box(item, title):
    for b in item.select(".box"):
        h = b.find("h3")
        if h and clean(h.get_text()).lower() == title.lower():
            return b
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=3000), "html.parser")
    out = []
    for it in s.select("#accordionPortfolio .accordion-item"):
        img = it.select_one(".header-accordion .logo img")
        name = clean(re.sub(r"(?i)\s*logo\s*$", "", (img.get("alt") or "") if img else ""))
        if not name:
            continue
        g = lambda sel: clean(it.select_one(sel).get_text(" ", strip=True)) if it.select_one(sel) else None
        desc = g(".header-accordion .desc p")
        status = g(".header-accordion .status p")
        stage = g(".header-accordion .stage p")
        partners = [clean(a.get_text()) for a in it.select(".header-accordion .partner a") if clean(a.get_text())]
        sb = box(it, "Sector(s)")
        sectors = [x for x in re.split(r"\s*[,/]\s*(?=[A-Z])|\n", sb.find("p").get_text("\n", strip=True)) if x] if sb and sb.find("p") else []
        fb = box(it, "Founder(S)")
        founders = [clean(x.get_text()) for x in fb.select("span")] if fb else []
        kb = box(it, "Key Dates")
        kd = [clean(x) for x in kb.find("p").get_text("\n", strip=True).split("\n")] if kb and kb.find("p") else []
        years = [int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", " ".join(kd))]
        web = None
        for a in it.select(".right-area .button-area a[href]"):
            if "website" in a.get_text(" ", strip=True).lower():
                web = a["href"]
                break
        st = (status or "").lower()
        out.append(rec(name if name != name.lower() else nice(name), desc, web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors,
                       status="exited" if re.search(r"acquired|ipo|exit|public", st) else ("active" if st.startswith("active") else None),
                       liveoak_status=status, investment_stage=stage, key_dates=kd or None,
                       first_invested_year=min(years) if years else None, founders=founders, source_team=partners))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} LiveOak companies")
    finish(out, "liveoakvp", ("description", "company_url", "status", "investment_stage", "sectors", "everywhere_tags"))


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
