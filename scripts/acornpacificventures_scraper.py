#!/usr/bin/env python3
"""Acorn Pacific Ventures portfolio scraper -> acornpacificventures_companies.json
Source: https://www.acornpacific.ventures/portfolio — static portfolio outbound company links; name from logo alt or domain label."""
import os, re, sys, requests
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://www.acornpacific.ventures/portfolio"
PRIMARY = "Acorn Pacific Ventures"
SKIP_HOST = re.compile(r"(?i)(linkedin|twitter|facebook|youtube|instagram|google|carta|cloudflare|webflow|jsdelivr|cdn\.|w3\.org|medium\.com|crunchbase|typeform|hubspot|vimeo|apple\.com|schema\.org|fontawesome|googleapis|gstatic|github\.com|notion\.so|substack|sharefile|wixstatic|parastorage)")
SELF = ['acornpacific.ventures']

def host_to_name(host):
    host = re.sub(r"^www\d?\.", "", host.lower())
    label = host.split(".")[0]
    if re.match(r"^[a-z0-9]+$", label):
        parts = re.findall(r"[a-z]+|\d+", label)
        if len(parts) >= 2 and all(len(p) >= 2 or p.isdigit() for p in parts):
            return " ".join(p.upper() if p.isdigit() else p.capitalize() for p in parts)
        return label.capitalize()
    return label

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT); r.raise_for_status()
    s = BeautifulSoup(r.text, "html.parser")
    out=[]; seen=set()
    for a in s.find_all("a", href=True):
        href = a["href"].strip()
        if not href.startswith("http") or is_social(href): continue
        host = urlparse(href).netloc.lower().replace("www.", "")
        if not host or SKIP_HOST.search(host): continue
        if any(x in host for x in SELF): continue
        path = urlparse(href).path.rstrip("/")
        if path and path.count("/") > 1: continue
        name = None
        img = a.find("img")
        if img and img.get("alt"):
            alt = clean(re.sub(r"(?i)\s*logo$", "", img["alt"]))
            if alt and 1 < len(alt) <= 45 and not re.search(r"(?i)^(logo|image|photo|icon)", alt):
                name = alt
        if not name:
            name = host_to_name(host)
        if not name or name.lower() in seen or len(name) > 45: continue
        seen.add(name.lower())
        site = href if not path else f"https://{host}"
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "acornpacificventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
