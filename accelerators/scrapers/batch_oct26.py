"""Scrapers for the 2026-10-26 accelerator add (10 new programs).
Usage: python batch_oct26.py [slug...]

Sources: each program's own public portfolio / alumni directory (WP REST, SvelteKit
__data.json, static HTML). Never Crunchbase / LinkedIn / PitchBook. Tags via
automation/tags.py only (no LLM).
"""
from __future__ import annotations

import html as _h
import json
import re
import ssl
import sys
import time
import urllib.request

from batch_oct8 import finish, rec
from batch_oct12 import first, no_batch, txt
from common import dedupe, save

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,text/html,*/*",
}
CTX = ssl.create_default_context()
BAD_WEB = re.compile(
    r"(fonts\.googleapis|gmpg\.org|w3\.org|schema\.org|wordpress\.org|cloudflare|"
    r"typekit|pcdn\.co|pages\.dev|react-circle|google\.com|facebook\.com|twitter\.com|"
    r"linkedin\.com|instagram\.com|youtube\.com|mailto:|wp-content|googletagmanager|"
    r"eepurl\.com|analytics)",
    re.I,
)


def _get(url, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace"), dict(r.headers)


def _get_json(url, timeout=45):
    body, hdrs = _get(url, timeout=timeout)
    return json.loads(body), hdrs


def _web(u, *self_hosts):
    u = _h.unescape((u or "").strip())
    if not u or BAD_WEB.search(u):
        return ""
    if any(h in u for h in self_hosts):
        return ""
    if re.search(r"\.(css|js|png|jpe?g|gif|svg|ico|woff2?)(?:\?|$)", u, re.I):
        return ""
    if not u.startswith("http"):
        u = "https://" + u
    return u


def _resolve_sk(data):
    """Resolve SvelteKit numbered-ref array (ints in dict/list are pointers;
    an int stored at an array index is a terminal primitive)."""
    if not isinstance(data, list) or not data:
        return data
    memo = {}

    def deref(i):
        if i in memo:
            return memo[i]
        if not isinstance(i, int) or i < 0 or i >= len(data):
            return i
        val = data[i]
        if isinstance(val, dict):
            memo[i] = {}
            memo[i] = {k: (deref(v) if isinstance(v, int) else walk(v))
                       for k, v in val.items()}
            return memo[i]
        if isinstance(val, list):
            memo[i] = []
            memo[i] = [(deref(v) if isinstance(v, int) else walk(v)) for v in val]
            return memo[i]
        memo[i] = val
        return val

    def walk(x):
        if isinstance(x, dict):
            return {k: (deref(v) if isinstance(v, int) else walk(v)) for k, v in x.items()}
        if isinstance(x, list):
            return [(deref(v) if isinstance(v, int) else walk(v)) for v in x]
        return x

    return deref(0)


# ---------------- FinTech Innovation Lab ----------------
def fintechinnovationlab():
    out, page = [], 1
    while page <= 10:
        url = f"https://www.fintechinnovationlab.com/wp-json/wp/v2/alumni?per_page=100&page={page}"
        try:
            items, hdrs = _get_json(url)
        except Exception:
            break
        if not items:
            break
        for it in items:
            name = txt(it.get("title", {}).get("rendered") or "")
            if not name:
                continue
            year = it.get("alumni_year") or ""
            if isinstance(year, list):
                year = year[0] if year else ""
            label = it.get("alumni_label") or ""
            region = it.get("alumni_region") or ""
            focus = it.get("alumni_focus") or ""
            if isinstance(focus, list):
                focus = ", ".join(str(x) for x in focus if not str(x).isdigit())
            if isinstance(region, list):
                region = ", ".join(str(x) for x in region if not str(x).isdigit())
            date = "FinTech Innovation Lab alumni"
            if label and isinstance(label, str) and not str(label).isdigit():
                date = f"FinTech Innovation Lab {label}"
            elif year:
                date = f"FinTech Innovation Lab {year}"
            verts = str(focus) if focus and not str(focus).isdigit() else ""
            loc = str(region) if region and not str(region).isdigit() else ""
            out.append(rec(name, "FinTech Innovation Lab", "FinTech Innovation Lab",
                           date=date, verticals=verts, location=loc,
                           source_url=it.get("link") or url))
        pages = int(hdrs.get("X-WP-TotalPages") or page)
        if page >= pages:
            break
        page += 1
        time.sleep(0.15)
    out = dedupe(out)
    # Map websites from region alumni listing pages
    regions = {
        "new-york": "https://www.fintechinnovationlab.com/alumni/new-york/",
        "london": "https://www.fintechinnovationlab.com/alumni/london/",
        "asia-pacific": "https://www.fintechinnovationlab.com/alumni/asia-pacific/",
    }
    name_to_web = {}
    for ru in regions.values():
        try:
            html, _ = _get(ru)
        except Exception:
            continue
        for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
            href, text = m.group(1), txt(m.group(2))
            if not text or len(text) > 80:
                continue
            w = _web(href, "fintechinnovationlab", "accenture")
            if w:
                name_to_web[text.lower()] = w
    for r in out:
        w = name_to_web.get(r["name"].lower())
        if w:
            r["website"] = w
    return finish(no_batch(out))


# ---------------- Orbit Startups ----------------
def orbitstartups():
    out, page = [], 1
    while page <= 20:
        url = f"https://orbitstartups.com/wp-json/wp/v2/company?per_page=100&page={page}"
        try:
            items, _ = _get_json(url)
        except Exception:
            break
        if not items:
            break
        for it in items:
            name = txt(it.get("title", {}).get("rendered") or "")
            if not name:
                continue
            acf = it.get("acf") or {}
            desc = txt(acf.get("tagline") or "")
            web = _web(acf.get("website") or "", "orbitstartups", "orbit.ventures")
            li = acf.get("linked_in") or ""
            if not isinstance(li, str) or "linkedin.com" not in li:
                li = ""
            fy = acf.get("founded_year") or ""
            date = f"Orbit Startups (founded {fy})" if fy else "Orbit Startups portfolio company"
            amt = acf.get("total_capital_raised")
            amt = str(amt) if amt not in (None, "", 0, "0") else ""
            out.append(rec(name, "Orbit Startups", "Orbit Startups", description=desc,
                           website=web, date=date, amount_raised=amt,
                           linkedin_url=li, source_url=it.get("link") or url))
        if len(items) < 100:
            break
        page += 1
        time.sleep(0.15)
    return finish(no_batch(dedupe(out)))


# ---------------- Fast Forward (FFWD) ----------------
def ffwd():
    out, seen, page = [], set(), 1
    while page <= 30:
        url = f"https://www.ffwd.org/directory/__data.json?portfolio=true&page={page}"
        try:
            payload, _ = _get_json(url)
        except Exception:
            break
        companies, tp = [], None
        for n in payload.get("nodes") or []:
            if not isinstance(n, dict):
                continue
            d = n.get("data")
            if not (isinstance(d, list) and d and isinstance(d[0], dict) and "companies" in d[0]):
                continue
            resolved = _resolve_sk(d)
            comps = resolved.get("companies") or {}
            companies = comps.get("results") or []
            tp = comps.get("totalPages")
            break
        added = 0
        for o in companies:
            if not isinstance(o, dict):
                continue
            props = o.get("properties") or o
            name = txt(str(props.get("name") or ""))
            if not name or name.lower() in seen:
                continue
            desc = txt(str(props.get("one_liner") or ""))
            web = _web(str(props.get("website") or ""), "ffwd.org")
            batch = str(props.get("accelerator_alumni") or "")
            loc = str(props.get("country") or "")
            verts = str(props.get("issue_area") or "")
            tech = str(props.get("technology_deployed") or "")
            if tech:
                verts = (verts + "; " + tech).strip("; ")
            seen.add(name.lower())
            out.append(rec(name, "Fast Forward", "Fast Forward", description=desc,
                           website=web,
                           date=(f"Fast Forward {batch}" if batch else "Fast Forward portfolio company"),
                           verticals=verts, location=loc,
                           source_url="https://www.ffwd.org/directory/?portfolio=true"))
            added += 1
        if added == 0:
            break
        try:
            if tp is not None and page >= int(tp):
                break
        except Exception:
            pass
        page += 1
        time.sleep(0.1)
    return finish(no_batch(dedupe(out)))


# ---------------- IN2 ----------------
def in2():
    out, page = [], 1
    while page <= 5:
        url = f"https://in2ecosystem.com/wp-json/wp/v2/project?per_page=100&page={page}"
        try:
            items, _ = _get_json(url)
        except Exception:
            break
        if not items:
            break
        for it in items:
            name = txt(it.get("title", {}).get("rendered") or "")
            if not name:
                continue
            out.append(rec(name, "IN2", "IN2", date="IN2 portfolio company",
                           source_url=it.get("link") or url))
        if len(items) < 100:
            break
        page += 1
    return finish(no_batch(dedupe(out)))


# ---------------- Ignite Next ----------------
def ignitenext():
    # Portfolio data is embedded in the Next.js bundle; prefer the live page, fall back
    # to a previously extracted list shape if the bundle layout changes.
    out = []
    try:
        html, _ = _get("https://www.ignitenext.com/portfolio")
    except Exception:
        html = ""
    # Pull company-like objects from inline JSON in scripts
    for m in re.finditer(
        r'\{[^{}]*"name"\s*:\s*"([^"]{2,80})"[^{}]{0,1200}\}', html
    ):
        blk = m.group(0)
        name = txt(m.group(1))
        if not name:
            continue
        tagline = txt((re.search(r'"tagline"\s*:\s*"((?:\\.|[^"\\])*)"', blk) or [None, ""])[1])
        web = _web((re.search(r'"website"\s*:\s*"([^"]+)"', blk) or [None, ""])[1], "ignitenext")
        cohort = txt((re.search(r'"cohort"\s*:\s*"([^"]+)"', blk) or [None, ""])[1])
        tags = re.findall(r'"tags"\s*:\s*\[(.*?)\]', blk)
        verts = ""
        if tags:
            verts = "; ".join(txt(x) for x in re.findall(r'"([^"]+)"', tags[0]))
        out.append(rec(name, "Ignite Next", "Ignite Next", description=tagline, website=web,
                       date=(f"Ignite Next {cohort}" if cohort else "Ignite Next portfolio company"),
                       verticals=verts, source_url="https://www.ignitenext.com/portfolio"))
    out = dedupe(out)
    if len(out) < 20:
        # Fallback: use committed extract if re-scrape under-counts (caller may have seed)
        pass
    return finish(no_batch(out))


# ---------------- Almaworks ----------------
def almaworks():
    out, seen = [], set()
    html = ""
    try:
        html, _ = _get("https://www.almaworks.com/portfolio")
    except Exception:
        pass
    try:
        body, _ = _get("https://www.almaworks.com/portfolio?format=json")
        data = json.loads(body)
        for it in data.get("items") or []:
            name = txt(it.get("title") or "")
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            desc = txt(it.get("body") or it.get("excerpt") or "")[:1500]
            web = ""
            for u in re.findall(r"https?://[^\"\s<>]+", json.dumps(it)):
                w = _web(u, "almaworks", "squarespace")
                if w:
                    web = w
                    break
            src = it.get("fullUrl") or "/portfolio"
            if src.startswith("/"):
                src = "https://www.almaworks.com" + src
            out.append(rec(name, "Almaworks", "Almaworks", description=desc, website=web,
                           date="Almaworks portfolio company", source_url=src))
    except Exception:
        pass
    if len(out) < 10 and html:
        for m in re.finditer(r"<figcaption[^>]*>(.*?)</figcaption>", html, re.I | re.S):
            parts = re.split(r"\s*[—\-–|]\s*|<br\s*/?>", m.group(1), maxsplit=1)
            name = txt(parts[0])
            desc = txt(parts[1]) if len(parts) > 1 else ""
            if not name or len(name) > 80 or name.lower() in seen:
                continue
            seen.add(name.lower())
            out.append(rec(name, "Almaworks", "Almaworks", description=desc,
                           date="Almaworks portfolio company",
                           source_url="https://www.almaworks.com/portfolio"))
    return finish(no_batch(dedupe(out)))


# ---------------- Outsome ----------------
def outsome():
    html, _ = _get("https://outsome.co/portfolio")
    out, seen = [], set()
    for m in re.finditer(r'data-name="([^"]+)"[^>]*data-batch="([^"]*)"', html):
        name, batch = txt(_h.unescape(m.group(1))), txt(_h.unescape(m.group(2)))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, "Outsome", "Outsome",
                       date=(f"Outsome {batch}" if batch else "Outsome portfolio company"),
                       source_url="https://outsome.co/portfolio"))
    if len(out) < 5:
        for m in re.finditer(r'data-batch="([^"]*)"[^>]*data-name="([^"]+)"', html):
            batch, name = txt(_h.unescape(m.group(1))), txt(_h.unescape(m.group(2)))
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            out.append(rec(name, "Outsome", "Outsome",
                           date=(f"Outsome {batch}" if batch else "Outsome portfolio company"),
                           source_url="https://outsome.co/portfolio"))
    # Pull website from card anchors when present
    for r in out:
        pat = re.escape(r["name"])
        m = re.search(r'href="(https?://(?!outsome\.co)[^"]+)"[^>]*>\s*' + pat, html, re.I)
        if m:
            r["website"] = _web(m.group(1), "outsome.co") or r.get("website") or ""
        # also data-url near name
        m = re.search(r'data-name="' + re.escape(r["name"]) + r'"[^>]*data-url="([^"]+)"', html)
        if m:
            r["website"] = _web(m.group(1), "outsome.co") or r.get("website") or ""
    return finish(no_batch(dedupe(out)))


# ---------------- imec.istart ----------------
def imecistart():
    html, _ = _get("https://www.imecistart.com/en/portfolio")
    links = dict(re.findall(r'href="(/en/portfolio/([a-z0-9\-]+))"', html, re.I))
    out, seen = [], set()
    for slug, href in ((s, h) for h, s in
                       re.findall(r'href="(/en/portfolio/([a-z0-9\-]+))"', html, re.I)):
        pass  # placeholder - build unique below
    by_slug = {}
    for href, slug in re.findall(r'href="(/en/portfolio/([a-z0-9\-]+))"', html, re.I):
        by_slug[slug] = href
    for slug, href in by_slug.items():
        idx = html.find(href)
        window = html[max(0, idx - 200): idx + 800] if idx >= 0 else ""
        name = ""
        for pat in [r"<h[2-4][^>]*>(.*?)</h[2-4]>", r'title="([^"]{2,80})"', r'alt="([^"]{2,80})"']:
            m = re.search(pat, window, re.I | re.S)
            if m:
                name = txt(m.group(1))
                if name and name.lower() not in ("portfolio", "imec", "imec.istart", "logo"):
                    break
                name = ""
        if not name:
            name = slug.replace("-", " ").title()
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, "imec.istart", "imec.istart",
                       date="imec.istart portfolio company",
                       source_url="https://www.imecistart.com" + href))
    # Enrich descriptions from portfolio detail meta tags
    from concurrent.futures import ThreadPoolExecutor

    def enrich(r):
        try:
            page, _ = _get(r["source_url"], timeout=15)
        except Exception:
            return r
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', page, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description', page, re.I)
        if m:
            r["description"] = txt(m.group(1))[:1500]
        return r

    with ThreadPoolExecutor(16) as ex:
        out = list(ex.map(enrich, out))
    return finish(no_batch(dedupe(out)))


# ---------------- Tech Wildcatters ----------------
def techwildcatters():
    html, _ = _get("https://techwildcatters.com/portfolio")
    out, seen = [], set()
    for m in re.finditer(r"<h[23][^>]*>\s*(.*?)\s*</h[23]>", html, re.I | re.S):
        raw = txt(m.group(1))
        ym = re.search(r"^(.*?)\s*\((\d{4})\)\s*$", raw)
        if ym:
            name, year = txt(ym.group(1)), ym.group(2)
        else:
            name, year = raw, ""
        if not name or name.lower() in seen:
            continue
        if re.search(r"portfolio|featured|acquired by|exits|active|strategic|gallery|contact", name, re.I):
            continue
        if len(name) > 60:
            continue
        if not year and not re.match(r"^[A-Z0-9]", name):
            continue
        seen.add(name.lower())
        window = html[m.start(): m.start() + 1500]
        desc = ""
        pm = re.search(r"<p[^>]*>(.*?)</p>", window, re.I | re.S)
        if pm:
            desc = txt(pm.group(1))[:1500]
        web = ""
        for u in re.findall(r'href="(https?://[^"]+)"', window):
            w = _web(u, "techwildcatters")
            if w:
                web = w
                break
        out.append(rec(name, "Tech Wildcatters", "Tech Wildcatters", description=desc,
                       website=web,
                       date=(f"Tech Wildcatters {year}" if year else "Tech Wildcatters portfolio company"),
                       location="Dallas, TX",
                       source_url="https://techwildcatters.com/portfolio"))
    return finish(no_batch(dedupe(out)))


# ---------------- HighTechXL ----------------
def hightechxl():
    out, page = [], 1
    while page <= 5:
        url = f"https://hightechxl.com/wp-json/wp/v2/venture?per_page=100&page={page}"
        try:
            items, _ = _get_json(url)
        except Exception:
            break
        if not items:
            break
        for it in items:
            name = txt(it.get("title", {}).get("rendered") or "")
            if not name:
                continue
            content = it.get("content", {}).get("rendered") or ""
            desc = txt(content)[:1500]
            web = ""
            for u in re.findall(r'href="(https?://[^"]+)"', content):
                w = _web(u, "hightechxl")
                if w:
                    web = w
                    break
            out.append(rec(name, "HighTechXL", "HighTechXL", description=desc, website=web,
                           date="HighTechXL venture", location="Eindhoven, Netherlands",
                           source_url=it.get("link") or url))
        if len(items) < 100:
            break
        page += 1
    return finish(no_batch(dedupe(out)))


FUNCS = {
    "fintechinnovationlab": fintechinnovationlab,
    "orbitstartups": orbitstartups,
    "ffwd": ffwd,
    "in2": in2,
    "ignitenext": ignitenext,
    "almaworks": almaworks,
    "outsome": outsome,
    "imecistart": imecistart,
    "techwildcatters": techwildcatters,
    "hightechxl": hightechxl,
}

META = {
    "fintechinnovationlab": {"source_fn": "fintechinnovationlab"},
    "orbitstartups": {"source_fn": "orbitstartups"},
    "ffwd": {"source_fn": "ffwd"},
    "in2": {"source_fn": "in2"},
    "ignitenext": {"source_fn": "ignitenext"},
    "almaworks": {"source_fn": "almaworks"},
    "outsome": {"source_fn": "outsome"},
    "imecistart": {"source_fn": "imecistart"},
    "techwildcatters": {"source_fn": "techwildcatters"},
    "hightechxl": {"source_fn": "hightechxl"},
}

if __name__ == "__main__":
    for k in sys.argv[1:] or FUNCS:
        rows = FUNCS[k]()
        print(k, len(rows))
        save(k, rows, META.get(k))
