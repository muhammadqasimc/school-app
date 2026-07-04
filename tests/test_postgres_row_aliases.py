"""Tests for global PostgreSQL / EMS row key aliasing."""

from postgres_repo import expand_legacy_row_key_aliases, legacy_key_variants


def test_totalmark_aliases():
    row = {"totalmark": 100}
    expand_legacy_row_key_aliases(row)
    assert row["TotalMark"] == 100


def test_reportid_cycleid_aliases():
    row = {"reportid": "12", "cycleid": "34"}
    expand_legacy_row_key_aliases(row)
    assert row.get("ReportId") == "12" or row.get("ReportID") == "12"
    assert row.get("CycleId") == "34"


def test_datayear_both_forms():
    row = {"datayear": "2026"}
    expand_legacy_row_key_aliases(row)
    assert row["DataYear"] == "2026"
    assert row["Datayear"] == "2026"


def test_bare_id_key():
    row = {"id": 55}
    expand_legacy_row_key_aliases(row)
    assert row["ID"] == 55


def test_legacy_key_variants_totalmark():
    kset = set(legacy_key_variants("totalmark"))
    assert "TotalMark" in kset
    assert "totalmark" in kset
