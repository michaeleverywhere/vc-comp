"""Smaller accelerators (one function per queue slug). Usage: python small.py <slug>...

Every field comes from the accelerator's own public page; blank when not published.
"""
import html as _h
import json
import re
import sys

import requests

from common import UA, clean, dedupe, save, tag

SPACE = "Deeptech / Robotics / AR/VR"


def get(url):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return r.text


def strip(s):
    return clean(_h.unescape(re.sub(r"<[^>]+>", " ", s or "")))


def rec(name, acc, source, **kw):
    r = {"name": clean(name), "description": "", "website": "", "team": "", "round": "",
         "amount_raised": "", "date": "", "verticals": "", "investors": acc, "source": source,
         "everywhere_tags": [], "source_url": ""}
    r.update({k: (clean(v) if isinstance(v, str) else v) for k, v in kw.items()})
    if not r["everywhere_tags"]:
        r["everywhere_tags"] = tag(r["name"], r["description"],
                                   [x for x in r["verticals"].split("; ") if x])
    return r


ROUNDS = {"pre-seed": "Pre-Seed", "seed": "Seed", "series a": "Series A", "series b": "Series B",
          "series c": "Series C", "series d": "Series D", "series e": "Series E", "growth": "Growth"}


def southparkcommons():
    url = "https://www.southparkcommons.com/companies"
    s = get(url)
    data = json.loads(re.search(r'<script type="application/json" id="company-data">(.*?)</script>', s, re.S).group(1))
    # highlight cards publish founders' first names + stage
    hl = {}
    t = _h.unescape(re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S))
    t = re.sub(r"<[^>]+>", "\n", t)
    lines = [clean(x) for x in t.split("\n") if clean(x)]
    for i, ln in enumerate(lines):
        if ln.startswith("·") and i >= 2:
            names = ln.lstrip("· ").strip() or (lines[i + 1] if i + 1 < len(lines) else "")
            hl.setdefault(lines[i - 2], (lines[i - 1], names))
    out = []
    for c in data:
        stage, team = hl.get(c["name"], ("", ""))
        st = (c.get("status") or stage or "").strip()
        out.append(rec(c["name"], "South Park Commons", "South Park Commons",
                       description=c.get("bio"), verticals="; ".join(x for x in [c.get("industry"), c.get("location")] if x),
                       team=re.sub(r",?\s*&\s*", ", ", team),
                       round=ROUNDS.get(st.lower(), ""),
                       date=f"SPC (founded {c['founded']})" if c.get("founded") else "SPC",
                       status=st, source_url=f"{url}#{c.get('slug')}",
                       everywhere_tags=tag(c["name"], c.get("bio"), [c.get("industry")])))
    return out


def zfellows():
    url = "https://www.zfellows.com/"
    s = get(url)
    i = s.find('<section id="za">')
    seg = s[i:s.find("</section>", i)]
    lines = [clean(x) for x in _h.unescape(re.sub(r"<[^>]+>", "\n", seg)).split("\n") if clean(x)]
    alts = [_h.unescape(a) for a in re.findall(r'alt="([^"]+)"', seg)]
    out = []
    for a in alts:
        nm = re.sub(r"^.* - ", "", a)  # "President of Cursor - Oskar" style alts
        if a not in lines:
            continue
        j = lines.index(a)
        company = lines[j + 1] if j + 1 < len(lines) else ""
        if not company or company.lower() == "openai":   # employer, not a Z Fellows company
            continue
        out.append(rec(company, "Z Fellows", "Z Fellows", team=a.replace(" & ", ", "),
                       date="Z Fellows", source_url=url))
    return out


def hf0():
    url = "https://www.hf0.com/facts"
    # HF0 publishes no company directory; only companies named on its own Facts page.
    t = _h.unescape(re.sub(r"<[^>]+>", "\n", get(url)))
    lines = [clean(x) for x in t.split("\n") if clean(x)]
    out, batch = [], ""
    for ln in lines:
        if re.fullmatch(r"[SWF]\d\d", ln):
            batch = ln
        m = re.match(r"// ([A-Z][A-Za-z0-9]+) (collects|releases|raises|launches) (.*)", ln)
        if m:
            out.append(rec(m.group(1), "HF0", "HF0", description=f"{m.group(1)} {m.group(2)} {m.group(3)}".strip("*"),
                           date=f"HF0 {batch}", source_url=url))
    return out


def pearvc():
    url = "https://pear.vc/companies/"
    s = get(url)
    i = s.find('class="all-area')
    out = []
    for box in s[i:].split('<div class="companies-all-box')[1:]:
        name = strip((re.search(r"<h5>(.*?)</h5>", box, re.S) or [None, ""])[1])
        verts = [strip(x) for x in re.findall(r'<div class="tags-area">(.*?)</div>', box, re.S)]
        verts = [strip(x) for x in re.findall(r"<a [^>]*>(.*?)</a>", "".join(
            re.findall(r'<div class="tags-area">(.*?)</div>', box, re.S)), re.S)]
        desc = strip((re.search(r"<p>(.*?)</p>", box, re.S) or [None, ""])[1])
        entry = re.search(r'class="green">(.*?)</a>', box)
        cur = re.search(r'class="white"[^>]*>(.*?)</a>', box)
        link = re.search(r'href="([^"#]+)(?:#new_tab)?" class="stretched-link"', box)
        if not name:
            continue
        out.append(rec(name, "Pear VC", "Pear VC", description=desc, verticals="; ".join(verts),
                       round=ROUNDS.get(strip(entry.group(1)).lower(), "") if entry else "",
                       status=strip(cur.group(1)) if cur else "",
                       website=link.group(1) if link else "", source_url=url,
                       everywhere_tags=tag(name, desc, verts)))
    return out


def seraphimspace():
    url = "https://seraphim.vc/portfolio/"
    s = get(url)
    out = []
    for m in re.finditer(r'<div class="col-12 col-md-4 ([^"]*)">\s*<a href="([^"]*)"[^>]*>(.*?)</a>', s, re.S):
        if "space_camp" not in m.group(1):
            continue
        name = strip((re.search(r'<div class="info">\s*<p>(.*?)</p>', m.group(3), re.S) or [None, ""])[1])
        if not name:
            continue
        desc = ""
        if len(name) > 40:          # a few cards carry a sentence instead of a name
            desc, name = name, ""
            name = re.split(r" is | are ", desc)[0]
        t = tag(name, desc) or [SPACE]
        if SPACE not in t:
            t = ([SPACE] + t)[:4]
        out.append(rec(name, "Seraphim Space Accelerator", "Seraphim", description=desc,
                       website=m.group(2), date="Seraphim Space Accelerator",
                       verticals="SpaceTech", everywhere_tags=t, source_url=url))
    return out


def catalystaccelerator():
    url = "https://catalystaccelerator.space/company-directory/"
    s = get(url)
    out = []
    for card in s.split('class="company-directory-card"')[1:]:
        name = strip((re.search(r'<h3 class="company-directory-name">(.*?)</h3>', card, re.S) or [None, ""])[1])
        groups = dict((strip(a), strip(b)) for a, b in re.findall(
            r'<div class="company-directory-label">(.*?)</div>\s*<div class="company-directory-values">(.*?)</div>', card, re.S))
        desc = strip((re.search(r'<div class="company-modal-description">(.*?)</div>', card, re.S) or [None, ""])[1])
        site = re.search(r'<p class="company-modal-website">\s*<a href="([^"]+)"', card)
        cohort = groups.get("Cohort", "")
        sectors = groups.get("Technology Sector", "")
        labels = [x.strip() for x in re.split(r",(?![^()]*\))", sectors) if x.strip()]
        t = tag(name, desc, labels)
        if SPACE not in t:
            t = ([SPACE] + t)[:4]      # AFRL / Space Force defense-tech accelerator
        out.append(rec(name, "Catalyst Accelerator", "Catalyst Accelerator", description=desc,
                       website=site.group(1) if site else "",
                       date="; ".join(f"Catalyst {c.strip()}" for c in cohort.split(";") if c.strip()),
                       verticals="; ".join(labels), everywhere_tags=t, source_url=url))
    return out


def betaworks():
    url = "https://www.betaworks.com/camp"
    t = _h.unescape(re.sub(r"<script.*?</script>|<style.*?</style>", "", get(url), flags=re.S))
    lines = [clean(x) for x in re.sub(r"<[^>]+>", "\n", t).split("\n") if clean(x)]
    i = lines.index("Past Camps")
    out, camp = [], ""
    for k in range(i + 1, len(lines)):
        ln = lines[k]
        if k + 1 < len(lines) and lines[k + 1] == "Learn more":
            camp = ln
            continue
        if ln == "Learn more":
            continue
        if ln in ("Apply", "Companies", "Team", "Events", "Writing", "News", "Connect") or ln.startswith("©"):
            break
        if camp:
            out.append(rec(ln, "Betaworks", "Betaworks", date=f"Betaworks {camp}",
                           verticals=camp, source_url=url))
    return out


REG = {f.__name__: f for f in [southparkcommons, zfellows, hf0, pearvc, seraphimspace,
                               catalystaccelerator, betaworks]}

if __name__ == "__main__":
    for slug in sys.argv[1:] or REG:
        recs = dedupe(REG[slug]())
        save(slug, recs, {"source_fn": slug})
