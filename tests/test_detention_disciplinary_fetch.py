"""Tests for detention notice disciplinary row loading from DisciplinaryRecords."""

import importlib


def test_parse_detention_grades_filter_phase_scoped():
    admin = importlib.import_module("admin_routes")
    assert admin._parse_detention_grades_filter("primary", "4,5,99") == [4, 5]
    assert admin._parse_detention_grades_filter("primary", []) == []
    assert admin._parse_detention_grades_filter("foundation", ["3", "4"]) == [3]


def test_validate_detention_hhmm():
    admin = importlib.import_module("admin_routes")
    assert admin._validate_detention_hhmm("9:05") == "09:05"
    assert admin._validate_detention_hhmm("13:50") == "13:50"
    assert admin._validate_detention_hhmm("25:00") is None
    assert admin._validate_detention_hhmm("ab") is None


def test_load_detention_schedule_times_overrides_win():
    admin = importlib.import_module("admin_routes")

    class FakeConn:
        def execute_query(self, query, params=None):
            return [{"StartTime": "10:00", "EndTime": "11:00"}]

    start, end = admin._load_detention_schedule_times(
        FakeConn(), "foundation", start_override="08:15", end_override="09:30"
    )
    assert start == "08:15"
    assert end == "09:30"


def test_fetch_detention_candidates_grade_filter(monkeypatch):
    app_mod = importlib.import_module("app")

    summary = [
        {"LearnerKey": "1", "Balance": 15},
        {"LearnerKey": "2", "Balance": 20},
    ]
    learners = [
        {"ID": 1, "LearnerID": "1", "FName": "A", "SName": "One", "Grade": "4", "Status": "C"},
        {"ID": 2, "LearnerID": "2", "FName": "B", "SName": "Two", "Grade": "6", "Status": "C"},
    ]

    monkeypatch.setattr(
        app_mod.mdb_conn,
        "execute_query",
        lambda sql, params=None: summary if "DisciplinaryRecords" in sql else learners,
    )

    all_primary = app_mod._fetch_detention_candidates("primary", "2026", 12)
    assert len(all_primary) == 2
    grade4_only = app_mod._fetch_detention_candidates("primary", "2026", 12, grades=[4])
    assert len(grade4_only) == 1
    assert grade4_only[0]["grade"] == "4"


def test_fetch_disciplinary_rows_for_notice_joins_learner_info(monkeypatch):
    admin = importlib.import_module("admin_routes")

    captured: dict[str, tuple] = {}

    def fake_execute(sql, params=None):
        captured["sql"] = sql
        captured["params"] = params
        return [
            {
                "LearnerKey": "101",
                "IncidentDate": "2026-04-01",
                "LevelMisconduct": "1",
                "MisconductDescription": "Late",
                "Demerit": 2,
                "Merit": 0,
                "AuthorisedBy": "Teacher A",
            }
        ]

    class FakeConn:
        def execute_query(self, query, params=None):
            return fake_execute(query, params)

    rows = admin._fetch_disciplinary_rows_for_notice(FakeConn(), ["101"], "2026")
    assert rows["101"][0]["MisconductDescription"] == "Late"
    assert rows["101"][0]["Demerit"] == 2
    sql = captured["sql"]
    assert "INNER JOIN" in sql.upper()
    assert "DisciplinaryRecords" in sql
    assert "Learner_Info" in sql
    assert "IncidentDate" in sql
    assert "[Date]" in sql or '"Date"' in sql
    assert captured["params"] == ("2026", "101")


def test_fetch_disciplinary_rows_normalizes_float_keys(monkeypatch):
    admin = importlib.import_module("admin_routes")

    def fake_execute(sql, params=None):
        return [
            {
                "LearnerKey": "42.0",
                "IncidentDate": None,
                "LevelMisconduct": "1",
                "MisconductDescription": "X",
                "Demerit": 1,
                "Merit": 0,
                "AuthorisedBy": "T",
            }
        ]

    class FakeConn:
        def execute_query(self, query, params=None):
            return fake_execute(query, params)

    rows = admin._fetch_disciplinary_rows_for_notice(FakeConn(), ["42"], "2026")
    assert "42" in rows
    assert len(rows["42"]) == 1
