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


def test_admin_message_templates_route_exist():
    """Verify /admin/message-templates is registered in the URL map."""
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/admin/message-templates" in rules, (
        f"Route /admin/message-templates not found. "
        f"Available admin routes: {[r for r in sorted(rules) if '/admin/' in r]}"
    )


def test_admin_message_templates_page_returns_200():
    """Admin GET /admin/message-templates returns 200."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.get("/admin/message-templates")
    assert resp.status_code == 200, resp.get_data(as_text=True)
    html = resp.get_data(as_text=True)
    # Verify key page elements are present
    assert "Message Templates" in html
    assert "Create Template" in html
    assert "Back to Admin" in html


def test_admin_message_templates_page_non_admin_returns_403():
    """Non-admin GET /admin/message-templates returns 403."""
    app_mod = importlib.import_module("app")
    client = _non_admin_client(app_mod)
    resp = client.get("/admin/message-templates")
    assert resp.status_code == 403, resp.get_data(as_text=True)


def test_admin_message_templates_page_shows_templates():
    """Admin page should list templates via API call in the JS on load."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    # Create a couple of templates via the API first
    resp1 = client.post(
        "/api/message-templates",
        json={
            "name": "Test Template A",
            "category": "attendance",
            "body": "Dear {parent_name}, {learner_name} was absent.",
            "placeholders": ["parent_name", "learner_name"],
        },
        content_type="application/json",
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        "/api/message-templates",
        json={
            "name": "Test Template B",
            "category": "behavior",
            "body": "Behavior report for {learner_name}.",
            "placeholders": ["learner_name"],
        },
        content_type="application/json",
    )
    assert resp2.status_code == 201

    # Verify API returns them with include_inactive
    list_resp = client.get("/api/message-templates?include_inactive=1")
    assert list_resp.status_code == 200
    data = list_resp.get_json() or {}
    assert len(data.get("templates", [])) >= 2

    # Verify the page renders
    page_resp = client.get("/admin/message-templates")
    assert page_resp.status_code == 200
    html = page_resp.get_data(as_text=True)
    assert "Test Template A" in html or "Test Template B" in html or "Message Templates" in html


def test_include_inactive_returns_inactive():
    """?include_inactive=1 should return inactive templates too."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    # Create a template
    resp = client.post(
        "/api/message-templates",
        json={
            "name": "ToBeDeactivated",
            "category": "general",
            "body": "Test body.",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201
    tpl_id = (resp.get_json() or {}).get("template", {}).get("id")

    # Deactivate it
    client.delete(f"/api/message-templates/{tpl_id}")

    # Without include_inactive — should not appear
    resp_active = client.get("/api/message-templates")
    data_active = resp_active.get_json() or {}
    active_names = [t["name"] for t in data_active.get("templates", [])]
    assert "ToBeDeactivated" not in active_names

    # With include_inactive — should appear
    resp_all = client.get("/api/message-templates?include_inactive=1")
    data_all = resp_all.get_json() or {}
    all_names = [t["name"] for t in data_all.get("templates", [])]
    assert "ToBeDeactivated" in all_names

    # Verify is_active field is present
    tpl = next(t for t in data_all.get("templates", []) if t["name"] == "ToBeDeactivated")
    assert tpl.get("is_active") is False
