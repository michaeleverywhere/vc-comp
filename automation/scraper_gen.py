"""Generate a bespoke scraper for one firm via the Claude API.

Called from discover mode for firms that lack a scripts/<slug>_scraper.py —
both needs-scraper sites and thin generic ones being upgraded to rich data.
Generation happens ONCE per firm (a scraper is a durable artifact); the result
is only trusted after scraper_guard's static checks + sandboxed run + output
validation pass.

The prompt ships real site context: the portfolio page HTML, any large embedded
JSON blobs (many "JS" sites embed their data — nextjs/RSC payloads), the list of
same-domain links, and one sample same-domain profile page for detail-page sites.

Env: ANTHROPIC_API_KEY (required), GEN_MODEL (default claude-sonnet-4-5),
GEN_MAX_TOKENS (default 8000).

Burst tries use prompt caching (_build_content): the contract+context block is
cache-marked, so retries within a burst re-read it at 0.1x input price instead
of re-paying full freight; per-call token usage is printed for the Railway logs.
"""
from __future__ import annotations

import json
import os
import re
from urllib.parse import urljoin, urlsplit

import requests

import extract

_API = "https://api.anthropic.com/v1/messages"

_CONTRACT = """Write a complete Python scraper module for the VC firm below.

HARD REQUIREMENTS (violations make the code unusable):
- Define  scrape() -> list[dict]  that returns one dict per portfolio company.
  All network work happens inside scrape(), not at import time.
- Use ONLY: requests, bs4 (BeautifulSoup), json, re, time, datetime, urllib.parse,
  html, collections, itertools, typing, math, string, unicodedata.
- NEVER: read environment variables, open/write files, subprocess, eval/exec,
  sockets, or any import outside that list. Do not include a __main__ block or
  any file I/O — the caller handles persistence.
- Site-tailored schema: include ONLY fields the site actually exposes. Missing
  scalar -> None; missing list -> []. NEVER fabricate or guess values.
- Aim for RICH fields where the site exposes them: company_name, company_url,
  description, plus founders / sectors / stage / status / profile URL when present.
  If data lives on per-company detail pages, fetch them (politely: a shared
  requests.Session, timeout=20, time.sleep(0.3) between requests).
- Include "everywhere_tags": [] and "source_url": the portfolio URL on each record.
- Be robust: tolerate missing nodes, don't index blindly, dedupe companies.

Return ONLY a single ```python code block with the module, nothing else."""


def _blobs(html: str, cap: int = 40_000) -> str:
    """Large embedded JSON blobs (script payloads) — often the real data source."""
    out, total = [], 0
    for m in re.finditer(r"<script[^>]*>(.*?)</script>", html, re.S | re.I):
        body = m.group(1).strip()
        if len(body) > 2000 and (body.count("{") > 10 or body.startswith("{") or body.startswith("[")):
            take = body[: cap - total]
            out.append(take)
            total += len(take)
            if total >= cap:
                break
    return "\n---BLOB---\n".join(out)


def _same_domain_sample(html: str, page_url: str) -> tuple[str, str]:
    """One same-domain link that looks like a company profile page, + its HTML."""
    host = urlsplit(page_url).netloc
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html):
        u = urljoin(page_url, m.group(1))
        p = urlsplit(u)
        if p.netloc == host and re.search(r"/(portfolio|companies|company)/[^/]+/?$", p.path):
            sample = extract.fetch(u)
            if sample:
                return u, sample[:30_000]
    return "", ""


def build_context(firm_name: str, slug: str, portfolio_url: str) -> str | None:
    html = extract.fetch(portfolio_url)
    if not html:
        return None
    profile_url, profile_html = _same_domain_sample(html, portfolio_url)
    parts = [
        f"FIRM: {firm_name}   SLUG: {slug}   PORTFOLIO URL: {portfolio_url}",
        f"\n===== PORTFOLIO PAGE HTML (truncated) =====\n{html[:60_000]}",
    ]
    blobs = _blobs(html)
    if blobs:
        parts.append(f"\n===== EMBEDDED SCRIPT JSON BLOBS =====\n{blobs}")
    if profile_html:
        parts.append(f"\n===== SAMPLE COMPANY PROFILE PAGE ({profile_url}) =====\n{profile_html}")
    return "\n".join(parts)


def _feedback_block(failures: list) -> str:
    """Prompt section describing this run's earlier failed tries, so the next
    generation VARIES its approach instead of resampling the same one.
    `failures`: [{"reason": str, "code": str|None}], oldest first."""
    if not failures:
        return ""
    parts = ["\n\n===== PREVIOUS FAILED ATTEMPTS (same site, this run) ====="]
    for i, f in enumerate(failures, 1):
        parts.append(f"Attempt {i} failed: {f['reason']}")
    last_code = next((f["code"] for f in reversed(failures) if f.get("code")), None)
    if last_code:
        parts.append("Most recent failed attempt's code:\n```python\n"
                     + last_code[:5000] + "\n```")
    parts.append(
        "Take a MATERIALLY DIFFERENT approach this time: fix the stated failure, "
        "and prefer a different on-page data source than before (embedded script "
        "JSON vs. HTML cards vs. per-company detail pages). If fields were too "
        "sparse, fetch the detail pages politely to enrich them.")
    return "\n".join(parts)


def _build_content(context: str, failures: list) -> list:
    """Message content for one generation call, shaped for prompt caching.

    Block 1 (contract + site context, the expensive 20-45K tokens) is marked
    with cache_control: byte-identical across a burst's tries because the
    context is fetched once and reused, so try 1 writes the cache (1.25x input
    price on that block) and later tries read it at 0.1x. The feedback block
    VARIES between tries, so it sits AFTER the cache boundary, uncached.
    5-minute ephemeral TTL, refreshed on every hit; a sandbox run slower than
    that between tries just means the next try re-writes the cache — bounded,
    cents-level downside."""
    content = [{"type": "text", "text": f"{_CONTRACT}\n\n{context}",
                "cache_control": {"type": "ephemeral"}}]
    fb = _feedback_block(failures)
    if fb:
        content.append({"type": "text", "text": fb})
    return content


def generate(firm_name: str, slug: str, portfolio_url: str,
             context: str | None = None, failures: list | None = None) -> str | None:
    """Return the generated module source, or None (no key / site unreachable /
    no code in the reply). Raises on API transport errors so the caller logs them.

    `context` lets a burst of tries reuse one site fetch; `failures` carries the
    burst's earlier failed tries (see _feedback_block)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("[gen] ANTHROPIC_API_KEY not set — skipping generation")
        return None
    if context is None:
        context = build_context(firm_name, slug, portfolio_url)
    if not context:
        print(f"[gen] {slug}: portfolio page unreachable — cannot generate")
        return None

    r = requests.post(
        _API,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={
            "model": os.environ.get("GEN_MODEL", "claude-sonnet-4-5"),
            "max_tokens": int(os.environ.get("GEN_MAX_TOKENS", "8000")),
            "messages": [{"role": "user",
                          "content": _build_content(context, failures or [])}],
        },
        timeout=180,
    )
    r.raise_for_status()
    body = r.json()
    u = body.get("usage", {})
    print(f"[gen] {slug}: tokens in={u.get('input_tokens', '?')} "
          f"cache_write={u.get('cache_creation_input_tokens', 0)} "
          f"cache_read={u.get('cache_read_input_tokens', 0)} "
          f"out={u.get('output_tokens', '?')}")
    text = "".join(b.get("text", "") for b in body.get("content", []))
    m = re.search(r"```python\s*(.*?)```", text, re.S)
    return m.group(1).strip() if m else None


# Trusted footer WE append (never the LLM): makes the file runnable as a normal
# bespoke scraper (python3 scripts/<slug>_scraper.py -> writes data/<slug>_companies.json),
# so the monthly refresh picks it up like the hand-written 47.
FOOTER = '''

# --- auto-appended runner (trusted template, not LLM output) -----------------
if __name__ == "__main__":
    import json as _json, os as _os, sys as _sys
    from datetime import datetime as _dt, timezone as _tz
    _records = scrape()
    _now = _dt.now(_tz.utc).replace(microsecond=0).isoformat()
    for _r in _records:
        _r.setdefault("everywhere_tags", [])
        _r.setdefault("scraped_at", _now)
    _out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                         "..", "data", "{data_file}")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\\n")
    print(f"wrote {{len(_records)}} records")
'''


def with_footer(code: str, data_file: str) -> str:
    header = ("# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed\n"
              "# validation before commit. Regenerate rather than hand-edit heavily.\n")
    return header + code.rstrip() + "\n" + FOOTER.replace("{data_file}", data_file)
