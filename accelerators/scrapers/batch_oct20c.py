"""Scrapers for the 2026-10-20 late-night accelerator add (chunk C).
Usage: python batch_oct20c.py [slug...]

Sources: each program's own public portfolio / resident pages (static HTML or the JSON the
page embeds), plus company websites for blank descriptions. Never Crunchbase / LinkedIn /
PitchBook. Tags are keyword-only (automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
import threading
from urllib.parse import urlparse

import cdp
from batch_oct8 import finish, rec, year_batch
from batch_oct12 import first, get, no_batch, txt
from common import dedupe, enrich_from_sites, save


def enrich_capped(out, limit=420):
    todo = [r for r in out if r.get("website") and not r.get("description")]
    t = threading.Thread(target=enrich_from_sites, args=(todo,), daemon=True)
    t.start()
    t.join(limit)


def _web(u):
    u = (u or "").strip()
    if not u or "linkedin.com" in u:
        return ""
    return u if u.startswith("http") else "https://" + u


# ---------------- Elemental Impact ----------------
def elementalimpact():
    url = "https://elementalimpact.com/companies/"
    s = get(url)
    out = []
    for blk in s.split("js-cportfolio-modal")[1:]:
        name = txt(first(r'cportfolio__popup__main__top">\s*<h2>(.*?)</h2>', blk))
        if not name:
            continue
        tagline = txt(first(r'cportfolio__popup__main__top">\s*<h2>.*?</h2>\s*<p>(.*?)</p>', blk))
        body = txt(first(r'<section class="main-content">(.*?)</section>', blk))
        loc = txt(first(r'cportfolio__popup__logo">.*?</div>\s*<p>(.*?)</p>', blk))
        web = first(r'<a href="([^"]+)">Website</a>', blk)

        def tags(h):
            seg = first(rf'<h4>{h}</h4>\s*<div class="cportfolio__popup__sidebar__tags">(.*?)</div>', blk)
            return [txt(x) for x in re.findall(r'<span[^>]*>(.*?)</span>', seg or "")]
        sectors, status = tags("Sectors"), tags("Status")
        desc = " ".join(x for x in (tagline, body) if x)
        if status:
            desc = (desc + f" (Status: {', '.join(status)}, per Elemental Impact)").strip()
        out.append(rec(name, "Elemental Impact", "Elemental Impact", description=desc, website=_web(web),
                       verticals="; ".join(sectors), date="Elemental Impact portfolio company",
                       location=loc, source_url=url))
    out = dedupe(out)
    enrich_capped(out)
    return finish(no_batch(out))


# ---------------- JFDI.Asia ----------------
def jfdi():
    url = "https://www.jfdi.asia/portfolio"
    s = get(url)
    out = []
    for li in re.findall(r'<li>(.*?)</li>', s, re.S):
        t = txt(li)
        m = re.match(r'^(.+?), from (.+?), (?:was|is|offered|offers|developed|develops|built|builds|'
                     r'provided|provides|made|makes|created|creates|helped|helps|had|has)\b(.*?)\((20\d\d[AB]?)\)\s*$', t)
        if not m:
            continue
        name, country, rest, batch = m.groups()
        desc = t.rsplit("(", 1)[0].strip().replace(" ,", ",")
        out.append(rec(name.strip(), "JFDI.Asia", "JFDI.Asia", description=desc,
                       date=f"JFDI.Asia {batch}", location=country, source_url=url))
    out = dedupe(out)
    return finish(year_batch(out))


# ---------------- Urban Future Lab ----------------
_VERB = (r"is|was|develops|developed|provides|has|builds|built|makes|offers|uses|creates|integrates|"
         r"transforms|delivers|revolutionizes|helps|enables|produces|designs|designed|turns|connects|"
         r"captures|combines|converts|manufactures|leverages|empowers|brings|accelerates|operates|"
         r"partners|works|aims|specializes|focuses|harnesses|deploys|reduces|unlocks|optimizes|"
         r"modernizes|simplifies|supports|offer|provide|develop|build")
_NAME_RX = re.compile(rf"^(?:Based in [^,]+, )?([A-Z0-9][\w.&®™'’\-]*(?: [\w.&®™'’\-]+){{0,4}}?)(?:’s|'s)? (?:{_VERB})\b")


def _alnum(x):
    return re.sub(r"[^a-z0-9]", "", x.lower())


def _name_ok(name, web):
    host = urlparse(web).netloc.lower().removeprefix("www.").split(".")[0] if web else ""
    n = _alnum(name.replace("®", "").replace("™", ""))
    if not host or not n:
        return False
    h = _alnum(host)
    return n[:4] in h or h[:4] in n or any(len(w) >= 4 and _alnum(w) in h for w in name.split())


def urbanfuturelab():
    url = "https://www.ufl.nyc/portfolio"
    s = get(url)
    out, skipped = [], 0
    parts = re.split(r'(<strong>(?:Current|Graduate) Companies</strong>)', s)
    section = ""
    for p in parts:
        if p.startswith("<strong>"):
            section = "current" if "Current" in p else "graduate"
            continue
        for web, alt in re.findall(r'<a\s+href="([^"]+)"[^>]*class="gallery-grid-image-link"[^>]*>\s*<img [^>]*?alt="([^"]*)"', p):
            desc = _h.unescape(alt).strip()
            if not desc:
                continue
            m = _NAME_RX.match(desc)
            name = m.group(1).strip() if m else ""
            name = re.sub(r"(?:’s|'s)\s+(?:mission|goal|vision|team|platform|technology)$", "", name).strip()
            name = re.split(r"’s |'s ", name)[0].strip()
            if re.search(r"\s(?:mission|goal|vision)$", name) or any(
                    w[0].islower() and w not in ("of", "and", "the", "for", "de", "&") for w in name.split()[1:]):
                name = ""
            if not name or not _name_ok(name, web):
                skipped += 1
                continue
            out.append(rec(name.rstrip("®™"), "Urban Future Lab", "Urban Future Lab", description=desc, website=_web(web),
                           date=f"Urban Future Lab {section} company" if section else "Urban Future Lab portfolio company",
                           location="", source_url=url))
    print("urbanfuturelab: skipped (name not stated clearly)", skipped, flush=True)
    out = dedupe(out)
    return finish(no_batch(out))


# ---------------- UnternehmerTUM ----------------
def unternehmertum():
    url = "https://www.unternehmertum.de/en/startups"
    s = get(url)
    out = []
    for href, blk in re.findall(r'<a class="tile startup-tile" href="([^"]+)"(.*?)</a>', s, re.S):
        name = txt(first(r'<h2 class="display-4">(.*?)</h2>', blk))
        if not name:
            continue
        desc = txt(first(r'</h2>\s*<p>(.*?)</p>', blk))
        out.append(rec(name, "UnternehmerTUM", "UnternehmerTUM", description=desc,
                       date="UnternehmerTUM featured startup", location="Munich (Garching), Germany", source_url=href))
    out = dedupe(out)
    return finish(no_batch(out))


# ---------------- Ag Startup Engine ----------------
def agstartupengine():
    url = "https://www.agstartupengine.com/portfolio"
    s = get(url)
    out = []
    for m in re.finditer(r'"metaData":\{"description":"((?:[^"\\]|\\.)*)","title":"((?:[^"\\]|\\.)*)","link":\{(.*?)\},"alt"', s):
        desc, name, link = (json.loads(f'"{g}"') if i < 2 else g for i, g in enumerate(m.groups()))
        name = name.strip()
        if not name:
            continue
        web = first(r'"url":"((?:[^"\\]|\\.)*)"', link)
        web = json.loads(f'"{web}"') if web else ""
        out.append(rec(name, "Ag Startup Engine", "Ag Startup Engine", description=desc.strip(), website=_web(web),
                       date="Ag Startup Engine portfolio company", location="Ames, Iowa, USA", source_url=url))
    out = dedupe(out)
    enrich_capped(out)
    return finish(no_batch(out))


# ---------------- Plug and Play APAC ----------------
def plugandplayapac():
    url = "https://www.plugandplayapac.com/our-startups"
    js = ("(()=>{const b=[...document.querySelectorAll('button,a,span')].find(e=>/^\\s*Load More\\s*$/i.test(e.textContent)"
          "&&e.offsetParent);if(b)b.click();return document.querySelectorAll('[id^=\"comp-kqa8ptbf__\"]').length})()")
    s = cdp.render(url, loop_js=js, settle=12, port=9531, prof="/tmp/cdp_pnpapac")
    items = {}
    for uid, inner in re.findall(r'<div id="comp-[a-z0-9]+__([0-9a-f-]{36})"[^>]*data-testid="richTextElement">(.*?)</div>', s, re.S):
        t = txt(inner)
        if t:
            items.setdefault(uid, []).append(t)
    out = []
    for uid, ts in items.items():
        name = ts[0].strip()
        vert = ts[1].strip() if len(ts) > 1 and len(ts[1]) < 40 and not ts[1].startswith("http") else ""
        web = next((x for x in ts[1:] if re.match(r"^https?://\S+$", x)), "")
        rest = [x for x in ts[1:] if x not in (vert, web)]
        blurb = max(rest, key=len) if rest else ""
        if not name:
            continue
        out.append(rec(name, "Plug and Play APAC", "Plug and Play APAC", description=blurb.replace("\u0003", ""),
                       website=_web(web), verticals=vert,
                       date=f"Plug and Play APAC startup ({vert})" if vert else "Plug and Play APAC startup",
                       location="", source_url=url))
    out = dedupe(out)
    return finish(no_batch(out))


# ---------------- LabCentral ----------------
def labcentral():
    url = "https://www.labcentral.org/about/our-resident-network"
    s = get(url)
    out = []
    for blk in s.split('ac-trigger">')[1:]:
        spans = re.findall(r'<span[^>]*>(.*?)</span>', blk.split("</button>")[0], re.S)
        if not spans:
            continue
        name = txt(spans[0])
        site = txt(spans[1]) if len(spans) > 1 else ""
        yr = txt(spans[2]) if len(spans) > 2 else ""
        panel = blk.split('ac-panel', 1)[-1]
        desc = " ".join(txt(x) for x in re.findall(r'<(?:h3|p)>(.*?)</(?:h3|p)>', first(r'redactor">(.*?)</div>', panel) or "", re.S) if txt(x))
        web = first(r'<a href="(https?://[^"]+)"[^>]*>\s*<span[^>]*>View Company', panel)
        if not name or name.lower() in ("company name", "all"):
            continue
        out.append(rec(name, "LabCentral", "LabCentral", description=desc, website=_web(web),
                       date=f"LabCentral resident {yr} ({site})".replace(" ()", "") if yr or site else "LabCentral resident",
                       location="Cambridge / Boston, MA, USA", source_url=url))
    out = dedupe(out)
    enrich_capped(out)
    return finish(year_batch(out))


FUNCS = {
    "elementalimpact": elementalimpact,
    "jfdi": jfdi,
    "urbanfuturelab": urbanfuturelab,
    "unternehmertum": unternehmertum,
    "agstartupengine": agstartupengine,
    "plugandplayapac": plugandplayapac,
    "labcentral": labcentral,
}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        print(f"=== {slug} ===", flush=True)
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct20c.{FUNCS[slug].__name__}"})
