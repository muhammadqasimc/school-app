import importlib


def test_teacher_routes_exist():
    app_mod = importlib.import_module("app")
    app = app_mod.app
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/teacher" in rules
    assert "/teacher/classes" in rules
    assert "/teacher/attendance" in rules
    assert "/api/teacher/dashboard" in rules
    assert "/api/teacher/messages/send" in rules
    assert "/api/teacher/attendance" in rules
    assert "/api/teacher/discipline" in rules
    assert "/api/teacher/assessments" in rules
    assert "/api/teacher/announcements" in rules
    assert "/api/teacher/announcements/save" in rules
    assert "/management/report/<report_key>" in rules
    assert "/api/management-mark-schedules/filters" in rules
    assert "/api/management-mark-schedules/preview" in rules
    assert "/api/management-mark-schedules/pdf" in rules
    assert "/api/management-academics-previous-year-comparison/filters" in rules
    assert "/api/management-academics-previous-year-comparison/preview" in rules
    assert "/api/management-average-academics-previous-year-comaparison/filters" in rules
    assert "/api/management-average-academics-previous-year-comaparison/preview" in rules
    assert "/api/management-result-analysis" in rules
    assert "/api/management-result-analysis/pdf" in rules
    assert "/api/management-result-analysis/xlsx" in rules


def test_teacher_user_fields_exist():
    app_mod = importlib.import_module("app")
    user_cols = {c.name for c in app_mod.User.__table__.columns}
    assert "is_teacher" in user_cols
    assert "educator_id" in user_cols
    assert "teacher_role" in user_cols


def test_teacher_api_smoke_authenticated():
    app_mod = importlib.import_module("app")
    app = app_mod.app
    with app.app_context():
        ident = app_mod.get_educator_identity_by_edid("66")
        if not ident:
            return
        user = app_mod.get_or_create_teacher_user(ident)
        user.first_login = False
        app_mod.db.session.commit()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True
            sess["portal_mode"] = "teacher"
        for route in (
            "/api/teacher/dashboard",
            "/api/teacher/classes",
            "/api/teacher/roster",
            "/api/teacher/attendance",
            "/api/teacher/discipline",
            "/api/teacher/assessments",
            "/api/teacher/reports/export",
        ):
            resp = client.get(route)
            assert resp.status_code in (200, 403), route
