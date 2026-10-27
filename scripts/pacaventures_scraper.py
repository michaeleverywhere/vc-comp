#!/usr/bin/env python3
"""pacaventures portfolio scraper.

Source: https://pacaventures.com/portfolio/ — European seed VC portfolio (Paca Ventures).
"""
from __future__ import annotations
import json
from pathlib import Path
from _d50_common import rec, finish

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "pacaventures_companies.json"


def main() -> None:
    raw = json.loads(SRC.read_text())
    out = []
    for r in raw:
        name = (r.get("company_name") or "").strip()
        if not name:
            continue
        out.append(
            rec(
                name,
                None,
                r.get("company_url"),
                "Paca Ventures",
                "https://pacaventures.com/portfolio/",
                "2026-10-26",
            )
        )
    finish(out, "pacaventures", ["company_name"])


if __name__ == "__main__":
    main()
