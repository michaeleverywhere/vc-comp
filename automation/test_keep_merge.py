"""Tests for the never-remove merge (python3 -m pytest automation/test_keep_merge.py)."""
import keep_merge as km


def test_dropped_company_is_kept_and_dated():
    old = [{"company_name": "A", "company_url": "https://a.com", "description": "x"},
           {"company_name": "B", "company_url": "https://b.com"}]
    new = [{"company_name": "A", "company_url": "https://a.com", "description": ""},
           {"company_name": "C", "company_url": "https://c.com"}]
    out, st = km.merge(old, new, "2026-10-20")
    by = {r["company_name"]: r for r in out}
    assert set(by) == {"A", "B", "C"} and len(out) >= len(old)
    assert by["A"]["description"] == "x" and by["A"]["listed_on_site"] is True
    assert by["B"]["listed_on_site"] is False and by["B"]["delisted_date"] == "2026-10-20"
    assert by["C"]["first_seen"] == "2026-10-20"
    assert st["newly_delisted"] == 1 and st["added"] == 1


def test_delisted_date_not_overwritten_and_relist():
    old = [{"name": "B", "listed_on_site": False, "delisted_date": "2026-10-01"}]
    out, _ = km.merge(old, [], "2026-10-20")
    assert out[0]["delisted_date"] == "2026-10-01"
    out, st = km.merge(old, [{"name": "B"}], "2026-10-21")
    assert out[0]["listed_on_site"] is True and out[0]["relisted_date"] == "2026-10-21"
    assert out[0]["previous_delisted_date"] == "2026-10-01" and st["relisted"] == 1


def test_rename_matched_by_domain_or_former_name():
    old = [{"name": "SuperRadiant", "website": "https://superradiant.co"},
           {"name": "Old", "website": "https://old.io"}]
    new = [{"name": "Primordiant", "former_name": "SuperRadiant", "website": "https://p.com"},
           {"name": "New Name", "website": "https://www.old.io/"}]
    out, st = km.merge(old, new, "2026-10-20")
    assert len(out) == 2 and st["newly_delisted"] == 0
    assert km.missing(old, new) == []


def test_missing_lists_drops():
    assert [r["name"] for r in km.missing([{"name": "X"}, {"name": "Y"}], [{"name": "X"}])] == ["Y"]
