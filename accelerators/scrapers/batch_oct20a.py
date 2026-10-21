"""Scrapers for the 2026-10-20 late-night accelerator add (chunk A).
Usage: python batch_oct20a.py [slug...]

Sources: each accelerator's own public portfolio / member / cohort pages (or the data those
pages embed), plus company websites for blank descriptions. Never Crunchbase / LinkedIn /
PitchBook. Tags are keyword-only (automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import re
import sys

import batch_oct8
from batch_oct8 import finish, rec, year_batch
from batch_oct12 import first, get, no_batch, pmap, txt
from common import dedupe, enrich_from_sites, save


# Agoranov's own (French) sector labels -> Everywhere tags (label mapping, same as ES_LABELS)
batch_oct8.ES_LABELS.update({"santé": "Health", "industrie & greentech": "Climate / Sustainability"})


def _rsc(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    return "".join(json.loads('"' + c + '"') for c in chunks)


def _json_array_after(t, key):
    i = t.find(key)
    if i < 0:
        return []
    j = t.index("[", i)
    depth, k, ins, esc = 0, j, False, False
    while True:
        ch = t[k]
        if ins:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                ins = False
        elif ch == '"':
            ins = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(t[j:k + 1])
        k += 1


# ---------------- Capital Factory ----------------
def _cf_vehicle(veh):
    if not veh or veh == "unknown":
        return "Capital Factory portfolio"
    v = veh.replace("_", " ").title()
    v = re.sub(r"\bIi\b", "II", re.sub(r"\bIii\b", "III", v))
    return "Capital Factory " + v

def capitalfactory():
    url = "https://www.capitalfactory.com/portfolio"
    t = _rsc(get(url))
    arr = _json_array_after(t, '{"companies":')
    out = []
    for c in arr:
        if not isinstance(c, dict) or not c.get("name"):
            continue
        st = c.get("exitStatus") or ""
        acq = c.get("acquirer") if isinstance(c.get("acquirer"), str) and not str(c.get("acquirer")).startswith("$") else ""
        desc = c.get("tagline") if isinstance(c.get("tagline"), str) and not c["tagline"].startswith("$") else ""
        if st and st not in ("active", "$undefined"):
            desc = (desc + f" (Status per Capital Factory: {st}{', ' + acq if acq else ''})").strip()
        stage = c.get("stage") if isinstance(c.get("stage"), str) and not c["stage"].startswith("$") else ""
        veh = c.get("holdingVehicle") if isinstance(c.get("holdingVehicle"), str) and not c["holdingVehicle"].startswith("$") else ""
        cities = c.get("cities") if isinstance(c.get("cities"), list) else []
        out.append(rec(c["name"], "Capital Factory", "Capital Factory", description=desc,
                       website=c.get("url") if isinstance(c.get("url"), str) and c["url"].startswith("http") else "",
                       round=stage.replace("-", " ").title() if stage else "",
                       verticals="; ".join(x for x in (c.get("sectors") or []) if isinstance(x, str)),
                       date=_cf_vehicle(veh),
                       location="; ".join(x for x in cities if isinstance(x, str)) or "Texas, USA",
                       source_url=f"https://www.capitalfactory.com/portfolio/{c.get('slug')}"))
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- Dreamit ----------------
def dreamit():
    base = "https://dreamit.com/portfolio"
    s0 = get(base)
    keys = sorted(set(re.findall(r'\?([a-z0-9]+)_page=\d+', s0)))
    pages = [s0]
    for k in keys:
        for pg in range(2, 40):
            s = get(f"{base}?{k}_page={pg}")
            if 'portoflio-itemfull' not in s:
                break
            pages.append(s)
            if f"{k}_page={pg + 1}" not in s:
                break
    out = []
    for s in pages:
        for blk in s.split('class="portoflio-itemfull"')[1:]:
            name = _h.unescape(first(r'alt="([^"]+)" class="image-7"', blk))
            if not name:
                name = txt(first(r'>Visit ([^<]+)</a>', blk))
            if not name:
                continue
            web = first(r'href="(https?://[^"]+)" class="portfolio-website-link"', blk)
            vert = txt(first(r'fs-cmsfilter-field="Vertical"[^>]*>(.*?)</div>', blk))
            fund = txt(first(r'fs-cmsfilter-field="Fund"[^>]*>(.*?)</div>', blk))
            status = txt(first(r'fs-cmsfilter-field="Status"[^>]*>(.*?)</div>', blk))
            desc = txt(first(r'class="paragraph-3">(.*?)</p>', blk))
            short = txt(first(r'class="text-block-21[^"]*">(.*?)</div>', blk))
            d = desc or short
            if status and status.lower() != "active":
                d = (d + f" (Status per Dreamit: {status})").strip()
            out.append(rec(name, "Dreamit Ventures", "Dreamit", description=d, website=web, verticals=vert,
                           date=f"Dreamit {fund}" if fund else "Dreamit portfolio", location="USA",
                           source_url=base))
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- Greentown Labs ----------------
def _gt_detail(item):
    slug, name = item
    url = f"https://greentown.org/members/{slug}"
    try:
        s = get(url, timeout=40)
    except Exception:
        return rec(name, "Greentown Labs", "Greentown Labs", date="Greentown Labs member", source_url=url)
    body = re.sub(r'(?is)<(script|style|svg)[^>]*>.*?</\1>', ' ', s)
    web = ""
    m = re.search(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*Visit website', body, re.I)
    if m:
        web = m.group(1)
    meta = txt(first(r'(Greentown (?:Boston|Houston|Labs)[^<]{0,40}Member[^<]*)<', body))
    founded = first(r'Founded\s*(?:<[^>]+>\s*)*(\d{4})', body)
    desc = _h.unescape(first(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', s, re.I))
    if not desc or "greentown" in desc.lower()[:40]:
        ps = [txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', body, re.S)]
        ps = [p for p in ps if len(p) > 60]
        desc = ps[0] if ps else ""
    loc = "Houston, TX, USA" if "Houston" in meta else ("Somerville (Boston), MA, USA" if "Boston" in meta else "USA")
    return rec(name, "Greentown Labs", "Greentown Labs", description=desc, website=web,
               date=meta or "Greentown Labs member", location=loc, source_url=url,
               founded_year=founded)


def greentownlabs():
    s = get("https://greentown.org/members")
    items, seen = [], set()
    for slug, name in re.findall(r'<a href="/members/([^"]+)"[^>]*>([^<]+)</a>', s):
        if slug in seen:
            continue
        seen.add(slug)
        items.append((slug, _h.unescape(name).strip()))
    out = pmap(_gt_detail, items, 12)
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- ERA (Entrepreneurs Roundtable Accelerator) ----------------
def era():
    url = "https://www.eranyc.com/companies/"
    s = get(url)
    out = []
    for blk in s.split('<article class="companies-cell')[1:]:
        blk = blk.split("</article>")[0]
        name = txt(first(r'class="panel__headline">(.*?)</h2>', blk))
        if not name:
            continue
        cat = txt(first(r'class="panel__category">(.*?)</span>', blk))
        prog = txt(first(r'class="panel__program">(.*?)</span>', blk))
        wys = first(r'class="panel__wysiwyg">(.*?)</div>', blk)
        paras = [txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', wys, re.S)]
        desc = next((p for p in paras if p and not re.match(r'Founders?\s*:', p) and "email" not in p.lower()
                     and "protected" not in p.lower()), "")
        team = next((re.sub(r'^Founders?\s*:\s*', '', p) for p in paras if re.match(r'Founders?\s*:', p)), "")
        web = first(r'<a href="(https?://[^"]+)"[^>]*>Website</a>', blk)
        li = first(r'<a href="(https?://[^"]*linkedin\.com/company[^"]+)"', blk)
        out.append(rec(name, "ERA (Entrepreneurs Roundtable Accelerator)", "ERA", description=desc, website=web,
                       team=team, verticals=cat, date=prog or "ERA portfolio", location="New York, NY, USA",
                       source_url=url, linkedin_url=li))
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:
        y = first(r'(20\d\d)', r.get("date") or "")
        r["batch_date"] = f"{y}-01-01" if y else ""
        r["batch_date_precision"] = "year" if y else ""
        r["most_recent_batch"] = bool(r.get("date", "").startswith("Current Companies"))
    return finish(out)


# ---------------- Blue Startups ----------------
def bluestartups():
    url = "https://www.bluestartups.com/portfolio"
    pages = [get(url)]
    for pg in range(2, 30):
        try:
            s = get(f"{url}/page/{pg}/")
        except Exception:
            break
        if "<article" not in s:
            break
        pages.append(s)
    out = []
    for s in pages:
        for blk in re.findall(r'<article class="([^"]*type-portfolio[^"]*)"[^>]*aria-label="([^"]+)"(.*?)</article>', s, re.S):
            cls, name, body = blk
            cohort = first(r'cohort-cohort-(\d+)', cls)
            ribbon = txt(first(r'class="ribbon">(.*?)</div>', body))
            desc = txt(first(r'class="whole">(.*?)</div>', body)) or txt(first(r'<p>(.*?)</p>', body))
            if ribbon:
                desc = (desc + f" ({ribbon})").strip()
            web = first(r'class="info">\s*<a[^>]+href="([^"]+)"', body)
            out.append(rec(_h.unescape(name), "Blue Startups", "Blue Startups", description=desc, website=web,
                           date=f"Blue Startups Cohort {cohort}" if cohort else "Blue Startups portfolio",
                           location="Honolulu, HI, USA",
                           source_url=first(r'href="(https://www\.bluestartups\.com/portfolio/[^"]+)"', body) or url))
    out = dedupe(out)
    enrich_from_sites(out)
    ns = [int(first(r'Cohort (\d+)', r["date"]) or 0) for r in out]
    top = max(ns) if ns else 0
    for r, n in zip(out, ns):
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and n == top)
    return finish(out)


# ---------------- AI Grant ----------------
def aigrant():
    url = "https://aigrant.com/"
    s = get(url)
    out = []
    for hdr, ul in re.findall(r'(AI Grant companies[^<]*?batch\s*\d+)\s*<ul>(.*?)</ul>', s, re.S | re.I):
        b = txt(hdr)
        for web, name, desc in re.findall(r'<li>\s*<a href="([^"]+)"[^>]*>(.*?)</a>\s*(?:&mdash;|—|-)?\s*(.*?)</li>', ul, re.S):
            out.append(rec(txt(name), "AI Grant", "AI Grant", description=txt(desc), website=web,
                           date=b.replace("AI Grant companies — ", "AI Grant ").replace("AI Grant companies", "AI Grant"),
                           location="", source_url=url))
    out = dedupe(out)
    enrich_from_sites(out)
    ns = [int(first(r'batch\s*(\d+)', r["date"], re.I) or 0) for r in out]
    top = max(ns) if ns else 0
    for r, n in zip(out, ns):
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and n == top)
    return finish(out)


# ---------------- Agoranov ----------------
def agoranov():
    base = "https://www.agoranov.com/startups"
    s0 = get(base)
    keys = sorted(set(re.findall(r'\?([a-z0-9]+)_page=\d+', s0)))
    pages = [s0]
    for k in keys:
        for pg in range(2, 60):
            s = get(f"{base}?{k}_page={pg}")
            if 'class="table mix w-dyn-item"' not in s:
                break
            pages.append(s)
            if f"{k}_page={pg + 1}" not in s:
                break
    out = []
    for s in pages:
        for blk in s.split('<div role="listitem" class="table mix w-dyn-item">')[1:]:
            name = txt(first(r'class="searc">(.*?)</h3>', blk))
            if not name:
                continue
            web = first(r'<a href="(https?://[^"]+)" class="link-block-18', blk)
            cats = [txt(c) for c in re.findall(r'class="categorie">(.*?)</div>', blk)]
            cats = list(dict.fromkeys(c for c in cats if c and c != "Tous les secteurs"))
            desc = txt(first(r'class="text-block-38">(.*?)</div>', blk))
            yr = first(r'<div class="div-date">(\d{4})</div>', blk)
            funds = txt(first(r'fonds_laptop">(.*?)</div>', blk))
            out.append(rec(name, "Agoranov", "Agoranov", description=desc, website=web, verticals="; ".join(cats),
                           amount_raised=f"${funds}M (raised, per Agoranov)" if funds else "",
                           date=f"Agoranov {yr}" if yr else "Agoranov", location="Paris, France",
                           source_url=base))
    out = dedupe(out)
    enrich_from_sites([r for r in out if not r.get("description")])  # Agoranov publishes a description for nearly all
    return finish(year_batch(out))


FUNCS = {
    "capitalfactory": capitalfactory,
    "dreamit": dreamit,
    "greentownlabs": greentownlabs,
    "eranyc": era,
    "bluestartups": bluestartups,
    "aigrant": aigrant,
    "agoranov": agoranov,
}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        print(f"=== {slug} ===", flush=True)
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct20a.{FUNCS[slug].__name__}"})
