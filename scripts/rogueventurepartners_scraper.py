#!/usr/bin/env python3
"""rogueventurepartners portfolio scraper.

Source: https://seedtable.com/investors/rogue-venture-partners/portfolio — Rogue Venture Partners portfolio.
"""
from __future__ import annotations
import json
from pathlib import Path
from _d50_common import rec, finish

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "rogueventurepartners_companies.json"


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
                "Rogue Venture Partners",
                "https://seedtable.com/investors/rogue-venture-partners/portfolio",
                "2026-10-26",
            )
        )
    finish(out, "rogueventurepartners", ["company_name"])


if __name__ == "__main__":
    main()
