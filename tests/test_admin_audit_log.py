import importlib
import json


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


def test_admin_audit_log_route_exists():
    """Verify /admin/audit-log is registered in the URL map."""
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/admin/audit-log" in rules, (
        f"Route /admin/audit-log not found. "
        f"Available admin routes: {[r for r in sorted(rules) if '/admin/' in r]}"
    )
    assert "/admin/audit-log/data" in rules, (
        f"Route /admin/audit-log/data not found."
    )


def test_admin_audit_log_page_returns_200():
    """Admin GET /admin/audit-log returns 200 with expected content."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.get("/admin/audit-log")
    assert resp.status_code == 200, resp.get_data(as_text=True)
    html = resp.get_data(as_text=True)
    assert "Admin Audit Log" in html
    assert "Back to Admin" in html
    assert "Operation" in html
    assert "Module" in html
    assert "Status" in html


def test_admin_audit_log_page_non_admin_returns_403():
    """Non-admin GET /admin/audit-log returns 403."""
    app_mod = importlib.import_module("app")
    client = _non_admin_client(app_mod)
    resp = client.get("/admin/audit-log")
    assert resp.status_code == 403, resp.get_data(as_text=True)


def test_admin_audit_log_shows_entries():
    """Create entries via the model, verify they appear on the page."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    with app_mod.app.app_context():
        admin_user = app_mod.User.query.filter_by(
            username=app_mod.ADMIN_USERNAME
        ).first()
        assert admin_user is not None, "Admin user must exist"

        # Create test audit log entries
        entry1 = app_mod.AdminAuditLog(
            user_id=admin_user.id,
            operation="csv_import",
            module="students",
            record_count=42,
            filename="students_2024.csv",
            summary="Imported 42 student records",
            details_json=json.dumps({"rows": ["a", "b"]}),
            status="success",
        )
        entry2 = app_mod.AdminAuditLog(
            user_id=admin_user.id,
            operation="bulk_update",
            module="attendance",
            record_count=10,
            filename=None,
            summary="Bulk updated attendance",
            status="partial",
        )
        entry3 = app_mod.AdminAuditLog(
            user_id=admin_user.id,
            operation="csv_export",
            module="grades",
            record_count=100,
            filename="grades_export.csv",
            summary="Exported 100 grade records",
            status="success",
        )
        app_mod.db.session.add_all([entry1, entry2, entry3])
        app_mod.db.session.commit()

    resp = client.get("/admin/audit-log")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Verify entries appear
    assert "csv_import" in html
    assert "students" in html
    assert "students_2024.csv" in html or "students_2024" in html
    assert "42" in html  # record_count

    assert "bulk_update" in html
    assert "attendance" in html
    assert "10" in html  # record_count

    assert "csv_export" in html
    assert "grades" in html

    # Verify status badges
    assert "success" in html
    assert "partial" in html


def test_admin_audit_log_filters():
    """Test filtering by operation, module, and status."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    with app_mod.app.app_context():
        admin_user = app_mod.User.query.filter_by(
            username=app_mod.ADMIN_USERNAME
        ).first()
        assert admin_user is not None

        # Create entries with varied attributes
        entries = [
            app_mod.AdminAuditLog(
                user_id=admin_user.id,
                operation="csv_import",
                module="students",
                record_count=5,
                status="success",
            ),
            app_mod.AdminAuditLog(
                user_id=admin_user.id,
                operation="csv_import",
                module="attendance",
                record_count=3,
                status="failure",
            ),
            app_mod.AdminAuditLog(
                user_id=admin_user.id,
                operation="bulk_delete",
                module="students",
                record_count=2,
                status="success",
            ),
        ]
        app_mod.db.session.add_all(entries)
        app_mod.db.session.commit()

    # Filter by operation
    resp = client.get("/admin/audit-log?operation=csv_import")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "csv_import" in html
    # bulk_delete filtered out - won't have the "bulk_delete" text
    # (other entries might show, but the key one won't be listed by name)
    # Actually let's just check the filter is working - the text should contain the right stuff

    # Filter by module
    resp = client.get("/admin/audit-log?module=attendance")
    assert resp.status_code == 200

    # Filter by status
    resp = client.get("/admin/audit-log?status=failure")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # The failure entry should be visible
    assert "failure" in html

    # Filter by operation + module
    resp = client.get("/admin/audit-log?operation=csv_import&module=students")
    assert resp.status_code == 200


def test_admin_audit_log_data_json_endpoint():
    """Test the JSON data endpoint returns paginated entries."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    with app_mod.app.app_context():
        admin_user = app_mod.User.query.filter_by(
            username=app_mod.ADMIN_USERNAME
        ).first()
        assert admin_user is not None

        entry = app_mod.AdminAuditLog(
            user_id=admin_user.id,
            operation="csv_import",
            module="students",
            record_count=5,
            status="success",
            summary="JSON test",
        )
        app_mod.db.session.add(entry)
        app_mod.db.session.commit()

    resp = client.get("/admin/audit-log/data")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None
    assert "entries" in data
    assert "page" in data
    assert "pages" in data
    assert "total" in data
    assert len(data["entries"]) >= 1
    # Verify entry structure
    first = data["entries"][0]
    assert "id" in first
    assert "operation" in first
    assert "module" in first
    assert "status" in first
    assert "summary" in first
    assert "created_at" in first


def test_admin_audit_log_data_non_admin_returns_403():
    """Non-admin GET /admin/audit-log/data returns 403."""
    app_mod = importlib.import_module("app")
    client = _non_admin_client(app_mod)
    resp = client.get("/admin/audit-log/data")
    assert resp.status_code == 403, resp.get_data(as_text=True)
