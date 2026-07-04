"""EMS → PostgreSQL SQL translation regressions (compat mode)."""

import importlib


def test_translate_quotes_unbracketed_ems_tables():
    app_mod = importlib.import_module("app")
    q = app_mod.MDBConnection._translate_access_to_postgres(
        "SELECT * FROM ReportMarks rm, ReportCycles rc WHERE 1=1"
    )
    assert 'FROM "ReportMarks" rm' in q.replace("  ", " ")
    assert ', "ReportCycles" rc' in q.replace("  ", " ")


def test_translate_top_limit_with_quoted_tables():
    app_mod = importlib.import_module("app")
    q = app_mod.MDBConnection._translate_access_to_postgres(
        "SELECT TOP 10 ID FROM Learner_Info WHERE Status = 'C'"
    )
    assert "LIMIT 10" in q
    assert 'FROM "Learner_Info"' in q


def test_translate_quotes_qualified_mixed_case_columns():
    app_mod = importlib.import_module("app")
    q = app_mod.MDBConnection._translate_access_to_postgres(
        "SELECT rm.ReportId, rc.CycleId FROM ReportMarks rm, ReportCycles rc WHERE rm.ReportId = rc.CycleId"
    )
    assert 'rm."ReportId"' in q
    assert 'rc."CycleId"' in q
