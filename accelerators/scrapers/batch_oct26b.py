"""Scrapers for the 2026-10-26 +20 accelerator add (batch B).
Usage: python batch_oct26b.py [slug...]

Sources: each program's own public portfolio / alumni directory (WP REST, GraphQL
cache, static HTML, theme admin-ajax). Never Crunchbase / LinkedIn / PitchBook.
Tags via automation/tags.py only (no LLM).
"""
from __future__ import annotations

import html as _h
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

from batch_oct8 import finish, rec
from batch_oct12 import txt
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
    r"eepurl\.com|analytics|squarespace|freeelectrons\.org|startlife\.nl|"
    r"healthincubatorhelsinki|innoenergy\.com|startx\.com|endeavor\.org|"
    r"idealab\.com|fuelaccelerator\.com|venturelab|digitalhealth\.london|"
    r"medtechinnovator|disneyaccelerator|joinef\.com)",
    re.I,
)
WORK = "/workspace/accel20-2026-10-26"


def _get(url, timeout=45, headers=None):
    req = urllib.request.Request(url, headers=headers or UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace"), dict(r.headers)


def _get_json(url, timeout=45):
    body, hdrs = _get(url, timeout=timeout)
    return json.loads(body), hdrs


def _post(url, data: dict, timeout=45):
    raw = urllib.parse.urlencode(data).encode()
    h = {**UA, "Content-Type": "application/x-www-form-urlencoded"}
    req = urllib.request.Request(url, data=raw, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "replace")


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


# ---------------- StartLife ----------------
def startlife():
    body, _ = _get("https://startlife.nl/startups/")
    out = []
    for it in re.findall(r'<li class="startup-item"[^>]*>(.*?)</li>', body, re.I | re.S):
        nm = re.search(r'<h4[^>]*class="title"[^>]*>(.*?)</h4>', it, re.I | re.S)
        if not nm:
            continue
        name = txt(nm.group(1))
        if not name:
            continue
        desc_m = re.search(r'class="description[^"]*"[^>]*>(.*?)</div>', it, re.I | re.S)
        tag_m = re.search(r'class="tag"[^>]*>(.*?)</div>', it, re.I | re.S)
        web = ""
        for u in re.findall(r'href="(https?://[^"]+)"', it):
            w = _web(u, "startlife.nl")
            if w:
                web = w
                break
        out.append(rec(
            name, "StartLife", "startlife.nl/startups",
            description=txt(desc_m.group(1)) if desc_m else "",
            website=web,
            verticals=txt(tag_m.group(1)) if tag_m else "AgriFoodTech",
            source_url="https://startlife.nl/startups/",
            location="Netherlands",
        ))
    return finish(dedupe(out))


# ---------------- Health Incubator Helsinki ----------------
def healthincubatorhelsinki():
    out, page = [], 1
    while page <= 5:
        url = f"https://healthincubatorhelsinki.com/wp-json/wp/v2/company?per_page=100&page={page}"
        try:
            items, hdrs = _get_json(url)
        except Exception:
            break
        if not items:
            break
        for it in items:
            name = txt((it.get("title") or {}).get("rendered") or "")
            if not name:
                continue
            link = it.get("link") or ""
            desc = txt((it.get("excerpt") or {}).get("rendered") or "")
            if not desc:
                desc = txt((it.get("content") or {}).get("rendered") or "")[:600]
            out.append(rec(
                name, "Health Incubator Helsinki", "healthincubatorhelsinki.com/wp-json",
                description=desc,
                website="",
                source_url=link,
                location="Helsinki, Finland",
                verticals="Health",
            ))
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
    return finish(dedupe(out))


# ---------------- InnoEnergy (cached GraphQL nodes + optional refresh) ----------------
def innoenergy():
    nodes = []
    cache = os.path.join(WORK, "innoenergy_nodes.json")
    if os.path.exists(cache):
        nodes = json.load(open(cache))
    if len(nodes) < 50:
        # Fallback: scrape portfolio listing HTML titles from public page
        body, _ = _get("https://www.innoenergy.com/discover-innovative-solutions/portfolio/")
        for m in re.findall(r'href="(/portfolio/[^"]+)"[^>]*>\s*<[^>]+>\s*([^<]{2,80})', body):
            nodes.append({"title": txt(m[1]), "uri": m[0], "slug": m[0].strip("/").split("/")[-1], "status": "publish"})
    out = []
    for n in nodes:
        name = txt(n.get("title") or "")
        if not name or n.get("status") not in (None, "publish", "PUBLISH"):
            if name and not n.get("status"):
                pass
            elif not name:
                continue
        uri = n.get("uri") or ""
        src = ("https://www.innoenergy.com" + uri) if uri.startswith("/") else (uri or "https://www.innoenergy.com/discover-innovative-solutions/portfolio/")
        out.append(rec(
            name, "InnoEnergy", "innoenergy.com/portfolio",
            description="",
            website="",
            source_url=src,
            verticals="Energy, Cleantech",
            location="Europe",
        ))
    return finish(dedupe(out))


# ---------------- StartX ----------------

def startx():
    """Prefer cleaned cache from prior HTML parse; avoid logo-filename junk."""
    cache = os.path.join(WORK, "startx_companies.json")
    raw = json.load(open(cache)) if os.path.exists(cache) else []
    out, seen = [], set()
    bad = re.compile(
        r"(copy of|\.png|\.jpe?g|\.svg|\.gif|\.webp|\.txt|\bscreenshot\b|demo day|"
        r"open.?uri|discord avatar|site icon|\bhttp\b|color no background|\blogo\b|\bicon\b)",
        re.I,
    )
    for c in raw:
        name = txt(c.get("name") or "")
        name = re.sub(r"^Copy of\s+", "", name, flags=re.I)
        name = re.sub(r"\.(png|jpe?g|svg|webp|gif).*$", "", name, flags=re.I)
        name = re.sub(r"\?.*$", "", name).strip(" -_")
        if not name or len(name) < 2 or bad.search(name):
            continue
        name2 = re.sub(r"\s+LOGO.*$", "", name, flags=re.I).strip()
        if name2 and len(name2) >= 2:
            name = name2
        k = name.lower()
        if k in seen:
            continue
        seen.add(k)
        web = _web(c.get("website") or "", "startx.com")
        out.append(rec(
            name, "StartX", "startx.com/companies",
            website=web,
            source_url="https://startx.com/companies/",
            location="Stanford, USA",
        ))
    return finish(dedupe(out))



def freeelectrons():
    page, _ = _get("https://freeelectrons.org/our-alumni/")
    nonce = re.search(r'"nonce":"([^"]+)"', page).group(1)
    m = re.search(r"data-competition-list='([^']+)'", page)
    comp_raw = _h.unescape(m.group(1))
    out, seen = [], set()
    for year in range(2017, 2027):
        try:
            b = _post("https://freeelectrons.org/wp-admin/admin-ajax.php", {
                "action": "freeelectrons_load_startups",
                "year": str(year),
                "competition_list": comp_raw,
                "nonce": nonce,
            })
            j = json.loads(b)
        except Exception as e:
            print("FE year fail", year, e)
            continue
        if not j.get("success"):
            print("FE year nosuccess", year, j)
            continue
        html = (j["data"].get("competitionTabs") or "") + (j["data"].get("competitionDropdown") or "")
        for card in re.findall(r'<a href="([^"]*)"[^>]*class="item company-card[^"]*"(.*?)</a>', html, re.I | re.S):
            href, inner = card
            title_m = re.search(r'class="title"[^>]*>(.*?)</div>', inner, re.I | re.S)
            name = txt(title_m.group(1)) if title_m else ""
            if not name:
                continue
            k = name.lower()
            if k in seen:
                continue
            seen.add(k)
            country_m = re.search(r'class="country-name"[^>]*>(.*?)</div>', inner, re.I | re.S)
            web = _web(href, "freeelectrons.org")
            out.append(rec(
                name, "Free Electrons", "freeelectrons.org/our-alumni",
                website=web,
                date=str(year),
                location=txt(country_m.group(1)) if country_m else "",
                verticals="Energy",
                source_url="https://freeelectrons.org/our-alumni/",
            ))
        time.sleep(0.3)
    return finish(dedupe(out))


# ---------------- Endeavor ----------------
def endeavor():
    out, page = [], 1
    while page <= 20:
        url = f"https://endeavor.org/wp-json/wp/v2/company?per_page=100&page={page}"
        try:
            items, hdrs = _get_json(url)
        except Exception:
            break
        if not items:
            break
        for it in items:
            name = txt((it.get("title") or {}).get("rendered") or "")
            if not name:
                continue
            desc = txt((it.get("excerpt") or {}).get("rendered") or "")
            if not desc:
                desc = txt((it.get("content") or {}).get("rendered") or "")[:600]
            out.append(rec(
                name, "Endeavor", "endeavor.org/wp-json",
                description=desc,
                source_url=it.get("link") or "",
                verticals="Scale-up",
            ))
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 14)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.2)
    return finish(dedupe(out))


# ---------------- Idealab ----------------
def idealab():
    body, _ = _get("https://www.idealab.com/")
    # Current + historical company logo alts
    skip = re.compile(
        r"idealab|menu|close|video|twitter|facebook|linkedin|youtube|bill gross|"
        r"marcia|susan|tod |gloria|stephanie|tom mcg|yeran|rene",
        re.I,
    )
    alts = []
    for a in re.findall(r'alt="([^"]+)"', body):
        a = txt(a)
        if not a or skip.search(a) or len(a) < 2:
            continue
        alts.append(a)
    # Split current vs historical by section if possible
    out, seen = [], set()
    for name in alts:
        k = name.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(rec(
            name, "Idealab", "idealab.com",
            source_url="https://www.idealab.com/",
            location="Pasadena, USA",
            verticals="Venture builder",
        ))
    return finish(dedupe(out))


# ---------------- Fuel Accelerator ----------------
def fuelaccelerator():
    body, _ = _get("https://www.fuelaccelerator.com/portfolio")
    heads = [(m.start(), int(m.group(1)), txt(m.group(2))) for m in re.finditer(r"<h([1-4])[^>]*>(.*?)</h\1>", body, re.I | re.S)]
    cohort = ""
    out, seen = [], set()
    for pos, level, name in heads:
        if not name:
            continue
        if level <= 2 and re.search(r"COHORT|FUEL ", name, re.I) and re.search(r"20\d\d", name):
            cohort = name
            continue
        if level != 4:
            continue
        if name in ("Past Cohorts", "Subscribe", "FAQs", "Who Are We", "FUEL ALUMNI") or len(name) > 70:
            continue
        k = name.lower()
        if k in seen:
            continue
        seen.add(k)
        # website near heading
        chunk = body[pos:pos + 1200]
        web = ""
        for u in re.findall(r'href="(https?://[^"]+)"', chunk):
            w = _web(u, "fuelaccelerator.com", "startupjunkie")
            if w:
                web = w
                break
        year_m = re.search(r"(20\d\d)", cohort or "")
        out.append(rec(
            name, "Fuel Accelerator", "fuelaccelerator.com/portfolio",
            website=web,
            date=year_m.group(1) if year_m else "",
            source_url="https://www.fuelaccelerator.com/portfolio",
            location="Arkansas, USA",
            verticals="HealthTech, AI/ML" if "HEALTH" in (cohort or "").upper() or "AI" in (cohort or "").upper() else "",
            round=cohort,
        ))
    return finish(dedupe(out))


# ---------------- Venturelab (featured page + paginated CF list) ----------------
def venturelab():
    out, seen = [], set()
    body, hdrs = _get("https://www.venturelab.swiss/startups")
    # Collect company detail links + names from page 1
    def absorb(html):
        for m in re.finditer(r'<h([23])[^>]*>(.*?)</h\1>', html, re.I | re.S):
            name = txt(m.group(2))
            if not name or re.search(r"Sailing|newsletter|Discover hightech|Sign up", name, re.I):
                continue
            if len(name) > 80:
                continue
            k = name.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(rec(
                name, "Venturelab", "venturelab.swiss/startups",
                source_url="https://www.venturelab.swiss/startups",
                location="Switzerland",
                verticals="Hightech",
            ))
    absorb(body)
    # Follow ColdFusion pagination links from page
    pages = re.findall(r'href="(/index\.cfm\?[^"]*bericht_seite_9735=\d+[^"]*)"', body)
    # Also cookie from set-cookie for session
    cookies = []
    for k, v in hdrs.items():
        if k.lower() == "set-cookie":
            cookies.append(v.split(";")[0])
    cookie_h = {"User-Agent": UA["User-Agent"], "Cookie": "; ".join(cookies)} if cookies else UA
    for rel in list(dict.fromkeys(pages))[:30]:
        url = "https://www.venturelab.swiss" + _h.unescape(rel).split("#")[0]
        try:
            b, _ = _get(url, headers=cookie_h)
            absorb(b)
            time.sleep(0.25)
        except Exception as e:
            print("VL page fail", e)
    return finish(dedupe(out))


# ---------------- Entrepreneurs First ----------------
def entrepreneursfirst():
    body, _ = _get("https://www.joinef.com/companies/")
    skip = re.compile(r"^(featured|all companies|entrepreneurs first|portfolio)$", re.I)
    out, seen = [], set()
    for m in re.finditer(r"<h([23])[^>]*>(.*?)</h\1>", body, re.I | re.S):
        name = txt(m.group(2))
        if not name or skip.match(name) or len(name) > 60:
            continue
        k = name.lower()
        if k in seen:
            continue
        seen.add(k)
        chunk = body[m.start():m.start() + 800]
        web = ""
        for u in re.findall(r'href="(https?://[^"]+)"', chunk):
            w = _web(u, "joinef.com")
            if w:
                web = w
                break
        out.append(rec(
            name, "Entrepreneurs First", "joinef.com/companies",
            website=web,
            source_url="https://www.joinef.com/companies/",
            location="Global",
        ))
    return finish(dedupe(out))


FUNCS = {
    "startlife": startlife,
    "healthincubatorhelsinki": healthincubatorhelsinki,
    "innoenergy": innoenergy,
    "startx": startx,
    "freeelectrons": freeelectrons,
    "endeavor": endeavor,
    "idealab": idealab,
    "fuelaccelerator": fuelaccelerator,
    "venturelab": venturelab,
    "entrepreneursfirst": entrepreneursfirst,
}

META = {k: {"source_fn": k} for k in FUNCS}

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for k in sys.argv[1:] or FUNCS:
        rows = FUNCS[k]()
        print(k, len(rows))
        save(k, rows, META.get(k))
