import importlib
import secrets
import json


def _auth_user(app_mod, username_suffix, **kwargs):
    """Create and auth a user in the test client."""
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    user_id = None
    with app_mod.app.app_context():
        app_mod.ensure_sqlite_schema()
        suffix = secrets.token_hex(4)
        user = app_mod.User(
            username=f"tpl_{username_suffix}_{suffix}",
            password_hash="x",
            first_login=False,
            **kwargs,
        )
        app_mod.db.session.add(user)
        app_mod.db.session.commit()
        user_id = user.id  # Capture ID while still in session
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client, user_id


def _admin_client(app_mod):
    """Create an admin test client."""
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


def test_message_template_model_exists():
    app_mod = importlib.import_module("app")
    assert hasattr(app_mod, "MessageTemplate")


def test_message_template_routes_exist():
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/api/message-templates" in rules
    assert "/api/message-templates/<int:template_id>" in rules
    assert "/api/teacher/message-templates" in rules


def test_admin_create_template():
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.post(
        "/api/message-templates",
        json={"name": "Late Arrival Notice", "category": "attendance", "body": "Dear {parent_name}, your child {learner_name} was late to school today.", "placeholders": ["parent_name", "learner_name"]},
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.get_data(as_text=True)
    data = resp.get_json() or {}
    assert data.get("ok") is True
    assert data.get("template", {}).get("name") == "Late Arrival Notice"


def test_admin_create_template_missing_fields():
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.post(
        "/api/message-templates",
        json={"name": "", "body": ""},
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_admin_create_template_invalid_category():
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    resp = client.post(
        "/api/message-templates",
        json={"name": "Bad", "category": "invalid_cat", "body": "test"},
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_teacher_list_templates():
    app_mod = importlib.import_module("app")
    # Create a template as admin first
    admin_client = _admin_client(app_mod)
    admin_client.post(
        "/api/message-templates",
        json={"name": "Test Template", "category": "behavior", "body": "Behavior notice for {learner_name}."},
        content_type="application/json",
    )
    # Teacher user should see it
    teacher_client, _ = _auth_user(app_mod, "teacher", is_teacher=True)
    resp = teacher_client.get("/api/teacher/message-templates")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    templates = data.get("templates") or []
    assert len(templates) >= 1
    found = any(t["name"] == "Test Template" for t in templates)
    assert found, f"Template not found in {templates}"


def test_teacher_list_templates_filtered():
    app_mod = importlib.import_module("app")
    admin_client = _admin_client(app_mod)
    admin_client.post("/api/message-templates", json={"name": "Attendance Tpl", "category": "attendance", "body": "Attendance: {learner_name}"}, content_type="application/json")
    admin_client.post("/api/message-templates", json={"name": "Academic Tpl", "category": "academic", "body": "Academic: {learner_name}"}, content_type="application/json")
    teacher_client, _ = _auth_user(app_mod, "teacher2", is_teacher=True)
    resp = teacher_client.get("/api/teacher/message-templates?category=attendance")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    templates = data.get("templates") or []
    assert all(t["category"] == "attendance" for t in templates)
    # Should not include the academic one in results
    academic = [t for t in templates if t["name"] == "Academic Tpl"]
    assert len(academic) == 0


def test_admin_update_template():
    app_mod = importlib.import_module("app")
    admin_client = _admin_client(app_mod)
    # Create
    create_resp = admin_client.post("/api/message-templates", json={"name": "Original", "category": "general", "body": "Original text"}, content_type="application/json")
    tpl_id = (create_resp.get_json() or {}).get("template", {}).get("id")
    assert tpl_id is not None
    # Update
    update_resp = admin_client.put(
        f"/api/message-templates/{tpl_id}",
        json={"name": "Updated", "body": "Updated text", "placeholders": ["parent_name"]},
        content_type="application/json",
    )
    assert update_resp.status_code == 200, update_resp.get_data(as_text=True)
    # Verify via teacher list
    teacher_client, _ = _auth_user(app_mod, "teacher3", is_teacher=True)
    resp = teacher_client.get("/api/teacher/message-templates")
    data = resp.get_json() or {}
    found = [t for t in (data.get("templates") or []) if t["id"] == tpl_id]
    assert len(found) == 1
    assert found[0]["name"] == "Updated"
    assert found[0]["body"] == "Updated text"


def test_admin_delete_template():
    app_mod = importlib.import_module("app")
    admin_client = _admin_client(app_mod)
    create_resp = admin_client.post("/api/message-templates", json={"name": "DeleteMe", "category": "general", "body": "To be deleted"}, content_type="application/json")
    tpl_id = (create_resp.get_json() or {}).get("template", {}).get("id")
    admin_client.delete(f"/api/message-templates/{tpl_id}")
    teacher_client, _ = _auth_user(app_mod, "teacher4", is_teacher=True)
    resp = teacher_client.get("/api/teacher/message-templates")
    data = resp.get_json() or {}
    found = [t for t in (data.get("templates") or []) if t["id"] == tpl_id]
    assert len(found) == 0


def test_non_admin_cannot_create_template():
    app_mod = importlib.import_module("app")
    teacher_client, _ = _auth_user(app_mod, "plain", is_teacher=True)
    resp = teacher_client.post("/api/message-templates", json={"name": "Should Fail", "category": "general", "body": "test"}, content_type="application/json")
    assert resp.status_code == 403


def test_non_teacher_cannot_access_teacher_templates():
    app_mod = importlib.import_module("app")
    parent_client, _ = _auth_user(app_mod, "parent", is_parent=True)
    resp = parent_client.get("/api/teacher/message-templates")
    assert resp.status_code == 403
