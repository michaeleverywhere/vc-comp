"""Scrapers for the 2026-10-20 late-night accelerator add (chunk D).
Usage: python batch_oct20d.py [slug...]

Sources: each program's own public portfolio / startup pages (static HTML, following the
page's own pagination links), plus company websites for blank descriptions. Never
Crunchbase / LinkedIn / PitchBook. Tags are keyword-only (automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
import threading

from batch_oct8 import finish, rec, year_batch
from batch_oct12 import first, get, no_batch, txt
from common import dedupe, enrich_from_sites


def enrich_capped(out, limit=420):
    todo = [r for r in out if r.get("website") and not r.get("description")]
    t = threading.Thread(target=enrich_from_sites, args=(todo,), daemon=True)
    t.start()
    t.join(limit)


def _web(u):
    u = _h.unescape((u or "").strip())
    if not u or "linkedin.com" in u or u.startswith("#"):
        return ""
    return u if u.startswith("http") else "https://" + u


def _pages(base, key, maxp=60):
    """Follow a Webflow-style ?<key>_page=N list until a page adds nothing new."""
    out, seen = [], set()
    for n in range(1, maxp + 1):
        s = get(base if n == 1 else f"{base}?{key}_page={n}")
        out.append(s)
        if f"{key}_page={n + 1}" not in s:
            break
    return out


# ---------------- Founders, Inc. ----------------
def foundersinc():
    url = "https://f.inc/portfolio"
    s = get(url)
    out, seen = [], set()
    for blk in re.split(r'(?=<a class="[^"]*" data-framer-name="[^"]*" href="\./portfolio/)', s)[1:]:
        slug = first(r'href="\./portfolio/([^"/]+)/?"', blk)
        name = txt(first(r'data-framer-name="Title"[^>]*>\s*<h2[^>]*>(.*?)</h2>', blk))
        if not slug or not name or slug in seen:
            continue
        seen.add(slug)
        labels = [txt(x) for x in re.findall(r'data-framer-name="Name"[^>]*>\s*<p[^>]*>(.*?)</p>', blk)]
        tagline = txt(first(r'data-framer-name="Tagline"[^>]*>\s*<p[^>]*>(.*?)</p>', blk))
        campus = "On Campus" in labels
        labels = [l for l in labels if l and l != "On Campus"]
        out.append(rec(name, "Founders, Inc.", "Founders, Inc.", description=tagline,
                       verticals="; ".join(labels),
                       date="Founders, Inc. On Campus company" if campus else "Founders, Inc. portfolio company",
                       location="", source_url=f"https://f.inc/portfolio/{slug}/"))
    out = dedupe(out)
    from batch_oct12 import pmap
    pmap(_finc_site, out, 12)
    return finish(no_batch(out))


_FINC_SKIP = re.compile(r"(f\.inc|framer|fonts\.|ytimg|youtube|lu\.ma|tally\.so|angellist|instagram|linkedin|notion\.site|"
                        r"twitter\.com|//x\.com|tiktok|google|apple\.com|github\.com/fdotinc|substack)", re.I)


def _finc_site(r):
    try:
        s = get(r["source_url"], timeout=30)
    except Exception:
        return
    hosts = []
    for u in re.findall(r'href="(https?://[^"]+)"', s):
        if not _FINC_SKIP.search(u) and u not in hosts:
            hosts.append(u)
    if len(hosts) == 1:
        r["website"] = _web(hosts[0])


# ---------------- Sting (Stockholm) ----------------
def sting():
    base = "https://www.sting.co/companies"
    out = []
    for s in _pages(base, "8efc5019"):
        for blk in s.split('role="listitem" class="filters5_feed_item w-dyn-item"')[1:]:
            name = txt(first(r'fs-cmsfilter-field="name"[^>]*>(.*?)</h1>', blk))
            if not name:
                continue
            sub = txt(first(r'fs-cmsfilter-field="subtitle"[^>]*>(.*?)</div>', blk))
            inds = [txt(x) for x in re.findall(r'fs-cmsfilter-field="industry">(.*?)</div>', blk)]
            cohort = txt(first(r'fs-cmsfilter-field="cohort">(.*?)</div>', blk))
            cur = txt(first(r'fs-cmsfilter-field="currently-at-sting"[^>]*>(.*?)</div>', blk))
            href = first(r'href="(/companies/[^"]+)"', blk)
            date = f"Sting {cohort} cohort" if cohort else "Sting company"
            if cur == "true":
                date += " (currently at Sting)"
            out.append(rec(name, "Sting", "Sting", description=sub, verticals="; ".join(dict.fromkeys(i for i in inds if i)),
                           date=date, location="Stockholm, Sweden",
                           source_url=("https://www.sting.co" + href) if href else base))
    return finish(year_batch(dedupe(out)))


# ---------------- Bethnal Green Ventures ----------------
def bgv():
    base = "https://bethnalgreenventures.com/portfolio"
    out = []
    for s in _pages(base, "30f83d13"):
        for blk in s.split('role="listitem" class="grid_item w-dyn-item"')[1:]:
            name = txt(first(r'<h4[^>]*>(.*?)</h4>', blk))
            if not name:
                continue
            desc = txt(first(r'</h4></div><p[^>]*>(.*?)</p>', blk))
            web = first(r'<a href="([^"]+)"[^>]*class="button-tertiary', blk) or first(r'<a href="([^"]+)" class="card_logo-wrapper', blk)
            status = [txt(x) for x in re.findall(r'class="category-tag smaller[^"]*">(.*?)</div>', blk)]
            themes = [txt(x) for x in re.findall(r'fs-cmsfilter-field="themes" class="category_label">(.*?)</div>', blk)]
            if "Exited" in status:
                desc = (desc + " (Exited, per Bethnal Green Ventures)").strip()
            out.append(rec(name, "Bethnal Green Ventures", "Bethnal Green Ventures", description=desc,
                           website=_web(web), verticals="; ".join(themes),
                           date="Bethnal Green Ventures portfolio company", location="", source_url=base))
    out = dedupe(out)
    enrich_capped(out)
    return finish(no_batch(out))


# ---------------- SpinLab (Leipzig) ----------------
_SPIN = {"cc": "Current Class", "energy": "Energy", "sc": "Smart City", "health": "Health", "exit": "Exited",
         "fun": "Funded", "fem": "Female", "gen": "Generic", "con": "Construction"}


def _spin_detail(r):
    try:
        s = get(r["source_url"], timeout=30)
    except Exception:
        return
    body = first(r'Share:(.*?)(?:CLICK HERE|Topics:)', s)
    d = txt(body)
    if d and len(d) > 20:
        r["description"] = d[:1500]
    m = re.search(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(?:(?!</a>).)*?WEBSITE', s, re.S | re.I)
    if m and "spinlab.co" not in m.group(1) and "linkedin.com" not in m.group(1):
        r["website"] = _web(m.group(1))


def spinlab():
    from batch_oct12 import pmap
    url = "https://www.spinlab.co/startups"
    s = get(url)
    out = []
    for href, cats, alt in re.findall(r'<a href="(https://www\.spinlab\.co/portfolio/[^"]+)"[^>]*data-category="([^"]*)"[^>]*>.*?<img[^>]*alt="([^"]*)"', s, re.S):
        name = txt(alt)
        if not name:
            continue
        c = [_SPIN.get(x, "") for x in cats.split()]
        secs = [x for x in c if x in ("Energy", "Smart City", "Health", "Construction")]
        flags = [x for x in c if x in ("Exited", "Funded", "Current Class")]
        date = "SpinLab current class" if "Current Class" in flags else "SpinLab portfolio startup"
        if "Exited" in flags:
            date += " (exited, per SpinLab)"
        out.append(rec(name, "SpinLab", "SpinLab", verticals="; ".join(secs), date=date,
                       location="", source_url=href.split("?")[0]))
    out = dedupe(out)
    pmap(_spin_detail, out, 12)
    return finish(no_batch(out))


# ---------------- Taiwan Tech Arena ----------------
def tta():
    base = "https://www.taiwanarena.tech/en/startups/"
    out = []
    for n in range(1, 80):
        s = get(base if n == 1 else f"{base}?page={n}")
        items = s.split('class="item  clearfix"')[1:]
        for blk in items:
            name = txt(first(r'<h3 class="title">(.*?)</h3>', blk))
            if not name:
                continue
            cls = txt(first(r'<div class="class">(.*?)</div>', blk))
            desc = txt(first(r'<p class="text[^"]*">(.*?)</p>', blk))
            tagsl = [txt(x).lstrip("#") for x in re.findall(r'<li class="tagItem">(.*?)</li>', blk)]
            href = first(r'href="(https://www\.taiwanarena\.tech/startups-detail/[^"]+)"', blk)
            out.append(rec(name, "Taiwan Tech Arena", "Taiwan Tech Arena", description=desc, verticals=cls,
                           date=("Taiwan Tech Arena startup (" + ", ".join(tagsl) + ")") if tagsl else "Taiwan Tech Arena startup",
                           location="Taiwan", source_url=href or base))
        if not items or f"?page={n + 1}" not in s:
            break
    return finish(no_batch(dedupe(out)))


# ---------------- YES!Delft ----------------
def yesdelft():
    url = "https://www.yesdelft.com/startups/"
    s = get(url)
    out = []
    for name in re.findall(r'<startup-item>.*?<span>(.*?)</span>\s*</startup-item>', s, re.S):
        name = txt(name)
        if name:
            out.append(rec(name, "YES!Delft", "YES!Delft", date="YES!Delft startup", location="Delft, Netherlands", source_url=url))
    return finish(no_batch(dedupe(out)))


# ---------------- Hatch Blue (Hatch Accelerator) ----------------
def hatchblue():
    url = "https://www.hatch.blue/portfolio"
    out = []
    for s in _pages(url, "xx_never"):
        for blk in s.split('class="portfolio_details-content"')[1:]:
            name = txt(first(r'fs-cmsfilter-field="name"[^>]*>(.*?)</h2>', blk))
            if not name:
                continue
            desc = txt(first(r'fs-cmsfilter-field="description"[^>]*>(.*?)</div>', blk))
            secs = [txt(x) for x in re.findall(r'fs-cmsfilter-field="sector"[^>]*>(.*?)</div>', blk)]
            region = txt(first(r'fs-cmsfilter-field="region"[^>]*>(.*?)</div>', blk))
            fund = txt(first(r'fs-cmsfilter-field="fund"[^>]*>(.*?)</div>', blk))
            web = first(r'<a href="([^"]+)" target="_blank" class="button is-link', blk)
            if re.search(r"\(EXITED\)", name, re.I):
                name = re.sub(r"\s*\(EXITED\)", "", name, flags=re.I).strip()
                desc = (desc + " (Exited, per Hatch Blue)").strip()
            out.append(rec(name, "Hatch Blue", "Hatch Blue", description=desc, website=_web(web),
                           verticals="; ".join(dict.fromkeys(x for x in secs if x and x != "Other")),
                           date=f"Hatch Blue portfolio ({fund})" if fund else "Hatch Blue portfolio company",
                           location=region, source_url=url))
    out = dedupe(out)
    enrich_capped(out)
    return finish(no_batch(out))


# ---------------- AngelPad ----------------
def angelpad():
    url = "https://angelpad.com/portfolio/"
    s = get(url)
    out = []
    for blk in s.split('class="gw-gopf-col-wrap"')[1:]:
        flt = first(r'^\s*data-filter="([^"]*)"', blk) or first(r'data-filter="([^"]*)"', blk[:200])
        m = re.search(r'gw-gopf-post-title"><b><a href="([^"]+)"[^>]*>(.*?)</a></b>(.*?)</div>', blk, re.S)
        if not m:
            continue
        href, name, rest = m.groups()
        name = txt(name)
        desc = txt(re.sub(r"<!DOCTYPE[^>]*>", "", rest))
        batch = first(r"AngelPad #(\d+)", desc) or first(r"\bap(\d+)f\b", flt or "")
        labels = [re.sub(r"(b2c|b2b|saas)f$", r"\1", x) for x in (flt or "").split()
                  if not re.match(r"ap\d+f$", x) and x not in ("featured", "exited")]
        labels = [{"b2c": "B2C", "b2b": "B2B", "saas": "SaaS"}.get(x, x.replace("-", " ")) for x in labels]
        web = href if "angelpad.com" not in href else ""
        out.append(rec(name, "AngelPad", "AngelPad", description=desc, website=_web(web),
                       verticals="; ".join(labels),
                       date=f"AngelPad #{batch}" if batch else "AngelPad portfolio company",
                       location="", source_url=href))
    out = dedupe(out)
    nums = [int(first(r"#(\d+)", r["date"])) for r in out if "#" in r["date"]]
    top = max(nums) if nums else None
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top) and r["date"] == f"AngelPad #{top}"
    return finish(out)


# ---------------- NSRCEL (IIM Bangalore) ----------------
def nsrcel():
    url = "https://nsrcel.org/startups/"
    s = get(url)
    out = []
    for blk in s.split('fintech-coe-startup-popup')[1:]:
        name = txt(first(r'<img[^>]*alt="([^"]+)"', blk))
        if not name:
            continue
        desc = txt(first(r'elementor-widget-text-editor.*?<p>(.*?)</p>', blk))
        items = {}
        for it in re.findall(r'elementor-icon-list-text">([^<]*)<', blk):
            k, _, v = it.partition(":")
            items[k.strip().lower()] = v.strip()
        team = "; ".join(x for x in (items.get("founder", ""), items.get("co-founders", "") or items.get("co-founder", "")) if x)
        out.append(rec(name, "NSRCEL (IIM Bangalore)", "NSRCEL", description=desc, website=_web(items.get("website", "")),
                       team=team, round=items.get("stage of venture", ""), verticals=items.get("sub-sectors", ""),
                       date="NSRCEL FinTech Centre of Excellence startup", location="India", source_url=url))
    return finish(no_batch(dedupe(out)))


# ---------------- Village Capital ----------------
def vilcap():
    """vilcap.com/our-alumni loads its list in the browser; page through it with the
    page's own Next button in headless Chrome (scrapers/cdp.py)."""
    import time
    import cdp
    url = "https://vilcap.com/our-alumni"
    c = cdp._Chrome(9473, "/tmp/cdp_vilcap")
    names = []
    try:
        c.call("Page.enable")
        c.call("Page.navigate", url=url)
        time.sleep(8)
        ev = lambda e: ((c.call("Runtime.evaluate", expression=e, awaitPromise=True, returnByValue=True) or {})
                        .get("result", {}).get("value"))
        for _ in range(200):
            got = json.loads(ev("JSON.stringify([...document.querySelectorAll('section a[target=_blank]')]"
                                ".map(a=>[(a.querySelector('span')||a).textContent.trim(),a.href]))") or "[]")
            new = [g for g in got if g not in names]
            names += new
            clicked = ev("(()=>{const bs=[...document.querySelectorAll('button')].filter(e=>/Next|\u00bb/.test(e.textContent.trim())&&!e.disabled);"
                         "if(!bs.length)return false;bs[bs.length-1].click();return true})()")
            time.sleep(2.5)
            if not new or not clicked:
                break
    finally:
        c.close()
    out = [rec(n, "Village Capital", "Village Capital", website=_web(w), date="Village Capital alumni",
               location="", source_url=url) for n, w in names if n]
    out = dedupe(out)
    enrich_capped(out)
    return finish(no_batch(out))


FUNCS = {"foundersinc": foundersinc, "sting": sting, "bgv": bgv, "spinlab": spinlab, "tta": tta, "yesdelft": yesdelft,
         "hatchblue": hatchblue, "angelpad": angelpad, "nsrcel": nsrcel, "vilcap": vilcap}

if __name__ == "__main__":
    for k in sys.argv[1:] or FUNCS:
        r = FUNCS[k]()
        print(k, len(r))
