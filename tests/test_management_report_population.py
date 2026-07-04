import importlib

"""
Management portal: JSON contracts exercised by templates under templates/management/.

Primary endpoints:
- GET /api/management-report-filters -> {"filters": {years, terms, phases, grades, subjects}}
- GET /api/management-report?report_key=…&year&term&… -> {"reportData": {kpis, charts, tables, …}}
- GET /api/management-distribution-results -> {"groups": [...], "meta": {...}}
- GET /api/management-averages-per-subject-per-grade -> {"groups": [...], "meta": {...}}
- GET /api/management-results-per-grade-subject -> {"rows": [...], "meta": {...}}
- GET /api/management-analysis -> {"blocks": [...], "meta": {...}}
- GET /api/management-learner-movement?mode&year&grade -> {rows, filters, selected, meta}
- GET /api/management-academics-previous-year-comparison/filters -> {"filters": {...}}
- GET /api/management-academics-previous-year-comparison/preview -> {rows, summary, filters}
- GET /api/management-average-academics-previous-year-comaparison/filters -> {"filters": {...}}
- GET /api/management-average-academics-previous-year-comaparison/preview -> {rows, summary, filters}
- GET /api/management-result-analysis, /api/management-achievement-promotion-analysis, mark-schedules/* (existing)
"""


class _FakeMdb:
    def execute_query(self, query, params=()):
        text = " ".join(str(query).split())

        if "SELECT DISTINCT CSTR(rm.Datayear) AS Y" in text and "FROM ReportMarks rm" in text:
            return [{"Y": "2024"}]
        if "SELECT DISTINCT CSTR(rc.Term) AS T" in text and "FROM ReportMarks rm, ReportCycles rc" in text:
            return [{"T": "1"}]
        if "SELECT DISTINCT CSTR(lp.Grade) AS G" in text and "FROM LearnerPromotion lp" in text:
            return [{"G": "8"}]
        if "SELECT DISTINCT s.Name AS N" in text and "FROM ReportMarks rm, Subjects s" in text:
            return [{"N": "Mathematics"}]

        if "FROM LearnerPromotion" in text and "AS Lid" in text and "AS G" in text:
            year = str(params[0]) if params else ""
            if year == "2024":
                return [{"Lid": "1001", "G": "8"}]
            return []

        if "FROM LearnerPromotion" in text and "AS Lid" in text and "AS G" not in text:
            year = str(params[0]) if params else ""
            gr = str(params[1]) if len(params) > 1 else ""
            if year == "2024" and gr == "8":
                return [{"Lid": "1001"}]
            return []

        if (
            "FROM LearnerPromotion c" in text
            and "INNER JOIN LearnerPromotion p" in text
            and "CSTR(p.Grade) = CSTR(c.Grade)" in text
        ):
            return [{"LearnerId": "1001"}]

        if "SELECT DataYear FROM LearnerPromotion" in text and "GROUP BY DataYear" in text:
            return [{"DataYear": "2024"}]
        if "SELECT Grade FROM LearnerPromotion" in text and "GROUP BY Grade" in text:
            return [{"Grade": "8"}]
        if "FROM LearnerPromotion WHERE DataYear = ?" in text:
            year = str(params[0]) if params else ""
            if year == "2024":
                return [{"LearnerId": "1001", "Grade": "8"}]
            if year == "2023":
                return [{"LearnerId": "1001", "Grade": "8"}]
            return []

        if "FROM ReportMarks rm, ReportCycles rc, Subjects s" in text and "CSTR(rm.Datayear) = ?" in text:
            year = str(params[0]) if params else ""
            term = str(params[1]) if len(params) > 1 else ""
            if year == "2024" and term == "1":
                return [
                    {
                        "LearnerID": "L1001",
                        "Subject": "Mathematics",
                        "Mark": 72,
                        "TotalMark": 100,
                        "Term": "1",
                    }
                ]
            return []

        if "SELECT CSTR(LearnerId) AS LearnerID, CSTR(Grade) AS Grade FROM LearnerPromotion WHERE CSTR(Datayear)=?" in text:
            year = str(params[0]) if params else ""
            if year == "2024":
                return [{"LearnerID": "1001", "Grade": "8"}]
            return []

        if "SELECT CSTR(ID) AS IDText, CSTR(LearnerID) AS LearnerCode FROM Learner_Info" in text:
            return [{"IDText": "1001", "LearnerCode": "L1001"}]

        if "FROM Learner_Info WHERE Status='C' AND CSTR(Grade)=?" in text:
            return [{"LearnerID": "1001", "LearnerCode": "L1001"}]
        if "FROM Learner_Info WHERE Status='C'" in text:
            return [{"LearnerID": "1001", "LearnerCode": "L1001", "Grade": "8"}]

        if "SELECT CSTR(lp.LearnerId) AS LearnerID, CSTR(lp.Grade) AS Grade, lp.CodeSelected, lp.CodeAuto, lp.PromotionDecision FROM LearnerPromotion lp, ReportCycles rc" in text:
            # Simulate missing ReportId/CycleId linkage in legacy data.
            return []
        if (
            "FROM LearnerPromotion lp WHERE CSTR(lp.DataYear)=?" in text
            or "FROM LearnerPromotion lp WHERE CSTR(lp.Datayear)=?" in text
        ) and "CodeSelected" in text:
            year = str(params[0]) if params else ""
            if year == "2024":
                return [{"LearnerID": "1001", "Grade": "8", "CodeSelected": "", "CodeAuto": "P", "PromotionDecision": ""}]
            return []

        if "SELECT CSTR(ID) AS ID, CSTR(LearnerID) AS LearnerCode, Gender FROM Learner_Info" in text:
            return [{"ID": "1001", "LearnerCode": "L1001", "Gender": "Male"}]
        if "SELECT ID, LearnerID, SName, FName, Gender, Grade, [Class], [Status] FROM Learner_Info" in text:
            return [
                {
                    "ID": "1001",
                    "LearnerID": "L1001",
                    "SName": "Doe",
                    "FName": "John",
                    "Gender": "Male",
                    "Grade": "8",
                    "Class": "8A",
                    "Status": "C",
                }
            ]

        if "[ID]" in text and "[LearnerID]" in text and "[FName]" in text and "FROM Learner_Info" in text:
            return [
                {
                    "ID": "1001",
                    "LearnerID": "L1001",
                    "SName": "Doe",
                    "FName": "John",
                    "Gender": "Male",
                    "Grade": "8",
                    "Class": "8A",
                    "Status": "C",
                }
            ]

        return []


def _client(monkeypatch):
    app_mod = importlib.import_module("app")
    app_mod.app.config["TESTING"] = True
    app_mod.app.config["LOGIN_DISABLED"] = True
    monkeypatch.setattr(app_mod, "is_analytics_user", lambda _user: True)
    monkeypatch.setattr(app_mod, "_management_user_can_access_reports", lambda _user: True)
    monkeypatch.setattr(app_mod, "mdb_conn", _FakeMdb())
    return app_mod.app.test_client()


def test_distribution_averages_and_results_populate(monkeypatch):
    client = _client(monkeypatch)
    for route in (
        "/api/management-distribution-results?year=2024&term=1",
        "/api/management-averages-per-subject-per-grade?year=2024&term=1",
        "/api/management-results-per-grade-subject?year=2024&term=1&grade=8",
    ):
        resp = client.get(route)
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload
        if "distribution-results" in route:
            assert any(group.get("rows") for group in payload.get("groups", []))
        elif "averages-per-subject-per-grade" in route:
            assert any(group.get("subjects") for group in payload.get("groups", []))
        else:
            assert payload.get("rows")


def test_analysis_populates(monkeypatch):
    client = _client(monkeypatch)
    resp = client.get("/api/management-analysis?year=2024&term=1")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload.get("blocks")


def test_achievement_and_learner_movement_populate(monkeypatch):
    client = _client(monkeypatch)

    achievement = client.get("/api/management-achievement-promotion-analysis?year=2024&term=1")
    assert achievement.status_code == 200
    achievement_payload = achievement.get_json()
    assert achievement_payload.get("rows")

    movement = client.get("/api/management-learner-movement?mode=repeating&year=2024&grade=8")
    assert movement.status_code == 200
    movement_payload = movement.get_json()
    assert movement_payload.get("rows")


def test_management_registry_api_smoke(monkeypatch):
    """All MANAGEMENT_REPORT_REGISTRY report keys reach a non-error JSON API (mocked EMS)."""
    client = _client(monkeypatch)
    mod = importlib.import_module("app")

    r = client.get("/api/management-report-filters?year=2024&term=1")
    assert r.status_code == 200
    assert r.get_json().get("filters")

    report_keys = (
        "general-overview",
        "principal-overview",
        "attendance",
        "learner-chart-report",
        "school-achievement-report",
        "learner-promotion-rate",
        "enrolment-by-year-trend",
        "subject-achievement-insights",
        "term-to-date-insights",
    )
    for rk in report_keys:
        resp = client.get(f"/api/management-report?report_key={rk}&year=2024&term=1")
        assert resp.status_code == 200, rk
        data = resp.get_json()
        assert data.get("reportData"), rk

    for path, required in (
        ("/api/management-distribution-results?year=2024&term=1", "groups"),
        ("/api/management-averages-per-subject-per-grade?year=2024&term=1", "groups"),
        ("/api/management-results-per-grade-subject?year=2024&term=1&grade=8", "rows"),
        ("/api/management-analysis?year=2024&term=1", "blocks"),
        ("/api/management-academics-previous-year-comparison/filters", "filters"),
        ("/api/management-average-academics-previous-year-comaparison/filters", "filters"),
    ):
        resp = client.get(path)
        assert resp.status_code == 200, path
        assert resp.get_json().get(required) is not None, path

    p1 = client.get("/api/management-academics-previous-year-comparison/preview?year=2024&grade=8&term=1")
    assert p1.status_code == 200
    assert "rows" in p1.get_json()

    p2 = client.get("/api/management-average-academics-previous-year-comaparison/preview?year=2024&grade=8&term=1")
    assert p2.status_code == 200
    assert "rows" in p2.get_json()

    ra = client.get("/api/management-result-analysis?year=2024&term=1")
    assert ra.status_code == 200
    assert ra.get_json().get("phases") is not None

    ms = client.get("/api/management-mark-schedules/filters?year=2024&grade=8")
    assert ms.status_code == 200
    assert ms.get_json().get("filters")
