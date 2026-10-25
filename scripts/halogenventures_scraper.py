#!/usr/bin/env python3
"""Halogen Ventures portfolio scraper -> halogenventures_companies.json
Source: https://halogenvc.com/portfolio — Halogen Ventures, Jesse Draper's Los Angeles early-stage fund investing in
female-founded consumer technology, CPG, AI software and health companies. The portfolio page lists current companies
(A-Z), the "Past Portfolio" (with "Acquired by ..." notes) and the site's "Future of ..." category sections. Each card
gives the site's description and usually the company website; cards are logo-based, so the company name is the phrase
in the description that spells the website's domain, else the description's own opening subject ("<Name> is ...")
when it is corroborated by the domain (or, for cards without a website, when it is a short capitalised name)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://halogenvc.com/portfolio"
PRIMARY = "Halogen Ventures"
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())


def name_keys(url, slug=None):
    keys = set()
    if url:
        host = urlparse(url if "//" in url else "http://" + url).netloc.lower().split(":")[0]
        host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
        keys.add(norm(host.split(".")[0]))
    if slug:
        keys.add(norm(slug))
    return {k for k in keys if len(k) >= 2}


def name_from(texts, keys):
    """The phrase of the site's own text that spells the company's domain (or page slug)."""
    for t in texts:
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.&+'’-]*", t or "")
        for i in range(len(toks)):
            for j in range(i + 1, min(i + 5, len(toks)) + 1):
                ph = re.sub(r"(['’]s|[.'’-])+$", "", " ".join(toks[i:j]))
                if norm(ph) in keys:
                    return ph
    return None


def logo_name(src, keys):
    """Site-authored logo file name, only when it spells the domain/slug."""
    if not src:
        return None
    f = unquote(src.rsplit("/", 1)[-1])
    f = re.sub(r"^[0-9a-f]{20,}_", "", f)
    f = re.sub(r"(-\d+x\d+|-e\d{9,})?\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    f = re.sub(r"\s*\(.*?\)", "", f)
    f = re.sub(r"(?i)[\s_-]*(logo|logotipo|transparente|full|dark|white|black|color|colour|horizontal|green|fka)\b.*$", "", f)
    f = clean(f.replace("_", " ").replace("-", " "))
    return f if f and norm(f) in keys else None


VERB = (r"is|are|was|has|have|makes|helps|offers|builds|provides|enables|allows|lets|uses|harnesses|transforms|"
        r"creates|connects|develops|delivers|empowers|combines|brings|turns|gives|supports|partners|powers|designs")


def lead_name(desc, keys):
    m = re.match(r"^([A-Z0-9][^.,;:!?]{0,40}?)(?:['\u2019]s)?\s+(?:%s)\b" % VERB, desc or "")
    if not m:
        return None
    n = m.group(1).strip()
    words = n.split()
    if keys:
        return n if any(norm(words[0]) and norm(words[0]) in k for k in keys) else None
    return n if len(words) <= 4 and all(w[:1].isupper() or w in ("+", "&", "and", "of", "the") or w[:1].isdigit() for w in words) else None


NOTE = re.compile(r"(?i)^(acquired by|merged with|ipo\b)")


def cards(sb):
    """Walk the section's elements in order: a text element opens a card, the following link element is its
    website/logo. "Acquired by ..." notes are attached only inside the same card group."""
    items, notes = [], {}
    for e in sb.select(".se"):
        if e.select(".se"):
            continue
        g = e.find_parent("div", class_="si-group")
        gid = id(g) if g is not None else None
        if e.name == "a":
            if items and items[-1]["g"] == gid and not items[-1]["a"]:
                items[-1]["a"] = e
            continue
        t = e.select_one(".se-t")
        txt = clean(t.get_text(" ")) if t else None
        if not txt or re.match(r"(?i)^past portfolio$", txt):
            continue
        if NOTE.match(txt):
            if gid is not None:
                notes[gid] = txt
            continue
        items.append({"g": gid, "t": txt, "a": None})
    for it in items:
        a, desc = it["a"], it["t"]
        href = a.get("href", "").strip() if a is not None else ""
        site = href if href.startswith("http") and not is_social(href) and "halogenvc" not in href else None
        titles = [i.get("title") for i in a.find_all("img")] if a is not None else []
        keys = name_keys(site)
        name = (name_from([desc], keys) if keys else None) or lead_name(desc, keys)
        if not name:
            for ti in titles:
                ti = clean(ti or "")
                if ti and not re.match(r"(?i)^(untitled|\d|image|logo)", ti) and (not keys or norm(ti) in keys):
                    name = ti
                    break
        if name:
            yield name, desc, site, notes.get(it["g"])


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    sectors = {}
    intro = soup.select_one("div.sb#intro")
    labels = [clean(x.get_text(" ")) for x in intro.select(".se-t")] if intro else []
    for sb in soup.select("div.sb[id]"):
        sid = sb["id"]
        m = re.match(r"(.+)-\d+$", sid)
        if not m or m.group(1) in ("all", "past-portfolio"):
            continue
        cat = m.group(1).replace("-", " ")
        lab = next((l for l in labels if norm(cat.split()[0]) in norm(l)), None) or cat.title()
        for name, *_ in cards(sb):
            sectors.setdefault(name.lower(), [])
            if lab not in sectors[name.lower()]:
                sectors[name.lower()].append(lab)
    out, seen = [], set()
    for sb in soup.select("div.sb[id]"):
        sid = sb["id"]
        if not re.match(r"(all|past-portfolio)-\d+$", sid):
            continue
        past = sid.startswith("past")
        for name, desc, site, note in cards(sb):
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                           status=("Exited" if note else "Past portfolio") if past else "Current",
                           exit_note=note, halogen_categories=sectors.get(name.lower())))
    if len(out) < 50:
        raise SystemExit(f"FATAL: only {len(out)} Halogen Ventures companies")
    finish(out, "halogenventures", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
