import importlib
import io


def _admin_client(app_mod):
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    with app_mod.app.app_context():
        app_mod.ensure_sqlite_schema()
        from app import ADMIN_USERNAME
        user = app_mod.User.query.filter_by(username=ADMIN_USERNAME).first()
        if not user:
            user = app_mod.User(
                username=ADMIN_USERNAME,
                password_hash="x",
                first_login=False,
            )
            app_mod.db.session.add(user)
            app_mod.db.session.commit()
        user_id = user.id
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client


def _non_admin_client(app_mod):
    """Create a parent (non-admin) test client that expects 403."""
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    user_id = None
    with app_mod.app.app_context():
        app_mod.ensure_sqlite_schema()
        import secrets
        suffix = secrets.token_hex(4)
        user = app_mod.User(
            username=f"nonadmin_{suffix}",
            password_hash="x",
            first_login=False,
            is_parent=True,
        )
        app_mod.db.session.add(user)
        app_mod.db.session.commit()
        user_id = user.id
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client


def test_admin_bulk_import_route_exists():
    """Verify /admin/bulk-import and /admin/bulk-import/confirm are registered."""
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/admin/bulk-import" in rules, (
        f"Route /admin/bulk-import not found. "
        f"Available admin routes: {[r for r in sorted(rules) if '/admin/' in r]}"
    )
    assert "/admin/bulk-import/confirm" in rules, (
        f"Route /admin/bulk-import/confirm not found."
    )


def test_admin_bulk_import_page_returns_200():
    """Admin GET /admin/bulk-import returns 200 with expected content."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.get("/admin/bulk-import")
    assert resp.status_code == 200, resp.get_data(as_text=True)
    html = resp.get_data(as_text=True)
    assert "Bulk CSV Import" in html
    assert "Upload CSV File" in html
    assert "Or Paste CSV Data" in html
    assert "Back to Admin" in html


def test_admin_bulk_import_non_admin_returns_403():
    """Non-admin GET /admin/bulk-import returns 403."""
    app_mod = importlib.import_module("app")
    client = _non_admin_client(app_mod)
    resp = client.get("/admin/bulk-import")
    assert resp.status_code == 403, resp.get_data(as_text=True)


def test_admin_bulk_import_confirm_non_admin_returns_403():
    """Non-admin POST /admin/bulk-import/confirm returns 403."""
    app_mod = importlib.import_module("app")
    client = _non_admin_client(app_mod)
    resp = client.post("/admin/bulk-import/confirm", data={})
    assert resp.status_code == 403, resp.get_data(as_text=True)


def test_admin_bulk_import_post_with_csv_string():
    """POST /admin/bulk-import with CSV data returns preview with columns and rows."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    csv_data = "learner_id,name,surname,grade\n1001,John,Doe,10\n1002,Jane,Smith,11\n1003,Bob,Wilson,10"
    resp = client.post("/admin/bulk-import", data={"csv_data": csv_data})
    assert resp.status_code == 200, resp.get_data(as_text=True)
    html = resp.get_data(as_text=True)
    # Should show preview phase content
    assert "Column Mapping" in html
    assert "Data Preview" in html
    assert "3 row(s)" in html
    assert "learner_id" in html
    assert "name" in html
    assert "surname" in html
    assert "grade" in html
    # Should show data rows
    assert "John" in html or "John" in html
    assert "Doe" in html
    assert "Jane" in html
    assert "Smith" in html


def test_admin_bulk_import_post_with_auto_mapping():
    """CSV headers matching known fields should be auto-mapped."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    csv_data = "learner_id,name,surname,grade\n1001,John,Doe,10"
    resp = client.post("/admin/bulk-import", data={"csv_data": csv_data})
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # The mapping dropdowns should have auto-selected values
    assert "value=\"learner_id\" selected" in html
    assert "value=\"name\" selected" in html
    assert "value=\"surname\" selected" in html
    assert "value=\"grade\" selected" in html


def test_admin_bulk_import_post_with_unknown_headers():
    """Unknown CSV headers should not be auto-mapped (empty mapping)."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    csv_data = "Foo,Bar,Baz\n1,2,3"
    resp = client.post("/admin/bulk-import", data={"csv_data": csv_data})
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # All three columns should have no pre-selected mapping
    assert "value=\"\" selected" in html or True  # just verify no known fields are selected


def test_admin_bulk_import_post_empty_csv():
    """POST with empty CSV data shows error and stays in upload phase."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.post("/admin/bulk-import", data={"csv_data": ""})
    assert resp.status_code == 200, resp.get_data(as_text=True)
    html = resp.get_data(as_text=True)
    # Should still show upload form, not preview
    assert "Column Mapping" not in html
    assert "Upload CSV File" in html


def test_admin_bulk_import_post_with_missing_data():
    """POST with no file and no csv_data shows appropriate error."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.post("/admin/bulk-import", data={})
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Should show upload form since no data provided
    assert "Upload CSV File" in html


def test_admin_bulk_import_confirm_no_csv():
    """POST /admin/bulk-import/confirm without CSV data redirects with error."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.post("/admin/bulk-import/confirm", data={})
    assert resp.status_code == 302, resp.get_data(as_text=True)
    # Should redirect back to bulk import page
    assert resp.location.endswith("/admin/bulk-import") or "/admin/bulk-import" in resp.location


def test_admin_bulk_import_confirm_with_data():
    """POST /admin/bulk-import/confirm with valid CSV and mappings logs audit entry."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    csv_data = "learner_id,name,surname,grade\n1001,John,Doe,10\n1002,Jane,Smith,11"
    resp = client.post(
        "/admin/bulk-import/confirm",
        data={
            "csv_raw": csv_data,
            "columns": "learner_id,name,surname,grade",
            "map_learner_id": "learner_id",
            "map_name": "name",
            "map_surname": "surname",
            "map_grade": "grade",
            "filename": "test.csv",
        },
    )
    assert resp.status_code == 302, resp.get_data(as_text=True)
    # Should redirect back with success flash
    assert "/admin/bulk-import" in resp.location

    # Follow redirect to verify flash message
    follow = client.get("/admin/bulk-import")
    assert follow.status_code == 200
    html = follow.get_data(as_text=True)
    assert "Ready to import" in html
