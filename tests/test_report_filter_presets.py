"""Tests for ReportFilterPreset model and API (save / load / delete)."""

import json
import importlib


# ── Fixture helpers ──────────────────────────────────────────────────────────


def _client(monkeypatch):
    """Return a test client with an admin user and in-memory SQLite."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["TESTING"] = True
    app_mod.app.config["LOGIN_DISABLED"] = False
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app_mod.app.app_context():
        app_mod.db.drop_all()
        app_mod.db.create_all()
        # Create a dummy admin user
        u = app_mod.User(
            id=1,
            username="admin",
            password_hash="x",
            is_manager=True,
        )
        app_mod.db.session.add(u)
        app_mod.db.session.commit()

    monkeypatch.setattr(app_mod, "is_analytics_user", lambda _user: True)
    monkeypatch.setattr(app_mod, "_management_user_can_access_reports", lambda _user: True)
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True
    return client


def _ensure_tables(monkeypatch):
    """Import the module and create all tables (drops first)."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app_mod.app.app_context():
        app_mod.db.drop_all()
        app_mod.db.create_all()
    return app_mod


# ── Tests ────────────────────────────────────────────────────────────────────


class TestReportFilterPresetModel:
    """Verify the model exists and can store/query data."""

    def _seed_preset(self, app_mod):
        """Helper: create a preset directly via the model."""
        with app_mod.app.app_context():
            p = app_mod.ReportFilterPreset(
                user_id=1,
                name="My Filters",
                report_key="general-overview",
                filters_json=json.dumps({"year": "2026", "term": "Term 1"}),
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            return p

    def test_create_preset(self, monkeypatch):
        """Create and retrieve a ReportFilterPreset."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            p = app_mod.ReportFilterPreset(
                user_id=1,
                name="Test Preset",
                report_key="attendance",
                filters_json=json.dumps({"year": "2026", "term": "Term 1", "phase": "Senior"}),
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            fetched = app_mod.ReportFilterPreset.query.get(p.id)
            assert fetched is not None
            assert fetched.name == "Test Preset"
            assert fetched.report_key == "attendance"
            assert json.loads(fetched.filters_json) == {"year": "2026", "term": "Term 1", "phase": "Senior"}

    def test_preset_defaults(self, monkeypatch):
        """Default values for filters_json and is_default."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            p = app_mod.ReportFilterPreset(
                user_id=1,
                name="Defaults",
                report_key="finance-overview",
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            assert p.filters_json == "{}"
            assert p.is_default is False
            assert p.created_at is not None
            assert p.updated_at is not None

    def test_preset_belongs_to_user(self, monkeypatch):
        """Preset is linked to the correct user."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            # Create a second user
            u2 = app_mod.User(id=2, username="user2", password_hash="x")
            app_mod.db.session.add(u2)
            app_mod.db.session.commit()

            p1 = app_mod.ReportFilterPreset(
                user_id=1, name="User1 Preset", report_key="attendance",
                filters_json=json.dumps({"year": "2025"}),
            )
            p2 = app_mod.ReportFilterPreset(
                user_id=2, name="User2 Preset", report_key="attendance",
                filters_json=json.dumps({"year": "2026"}),
            )
            app_mod.db.session.add_all([p1, p2])
            app_mod.db.session.commit()

            user1_presets = app_mod.ReportFilterPreset.query.filter_by(user_id=1).all()
            assert len(user1_presets) == 1
            assert user1_presets[0].name == "User1 Preset"


class TestReportFilterPresetAPI:
    """Test the CRUD API endpoints for presets."""

    def test_save_preset(self, monkeypatch):
        """POST /api/report-filters/presets creates a new preset."""
        client = _client(monkeypatch)
        resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({
                "name": "My Saved Filters",
                "report_key": "general-overview",
                "filters": {"year": "2026", "term": "Term 1", "grade": "10"},
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "My Saved Filters"
        assert data["report_key"] == "general-overview"
        assert data["filters"]["year"] == "2026"
        assert data["filters"]["grade"] == "10"
        assert "id" in data

    def test_save_preset_missing_name(self, monkeypatch):
        """POST without name returns 400."""
        client = _client(monkeypatch)
        resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({"report_key": "attendance", "filters": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_save_preset_missing_report_key(self, monkeypatch):
        """POST without report_key returns 400."""
        client = _client(monkeypatch)
        resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({"name": "Test", "filters": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_list_presets(self, monkeypatch):
        """GET /api/report-filters/presets?report_key=X returns saved presets."""
        client = _client(monkeypatch)
        # Save two presets
        client.post(
            "/api/report-filters/presets",
            data=json.dumps({"name": "First", "report_key": "attendance", "filters": {"year": "2025"}}),
            content_type="application/json",
        )
        client.post(
            "/api/report-filters/presets",
            data=json.dumps({"name": "Second", "report_key": "attendance", "filters": {"year": "2026"}}),
            content_type="application/json",
        )
        # Save a preset for a different report (should not appear)
        client.post(
            "/api/report-filters/presets",
            data=json.dumps({"name": "Other", "report_key": "finance-overview", "filters": {}}),
            content_type="application/json",
        )

        resp = client.get("/api/report-filters/presets?report_key=attendance")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        names = [p["name"] for p in data]
        assert "First" in names
        assert "Second" in names

    def test_list_presets_requires_report_key(self, monkeypatch):
        """GET without report_key returns 400."""
        client = _client(monkeypatch)
        resp = client.get("/api/report-filters/presets")
        assert resp.status_code == 400

    def test_get_preset(self, monkeypatch):
        """GET /api/report-filters/presets/<id> returns the preset."""
        client = _client(monkeypatch)
        # Create a preset
        create_resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({
                "name": "Get Test",
                "report_key": "attendance",
                "filters": {"year": "2026", "grade": "12"},
            }),
            content_type="application/json",
        )
        preset_id = create_resp.get_json()["id"]

        resp = client.get(f"/api/report-filters/presets/{preset_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Get Test"
        assert data["filters"]["year"] == "2026"
        assert data["filters"]["grade"] == "12"

    def test_get_preset_not_found(self, monkeypatch):
        """GET for non-existent preset returns 404."""
        client = _client(monkeypatch)
        resp = client.get("/api/report-filters/presets/9999")
        assert resp.status_code == 404

    def test_update_preset_rename(self, monkeypatch):
        """PUT /api/report-filters/presets/<id> renames the preset."""
        client = _client(monkeypatch)
        create_resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({
                "name": "Old Name",
                "report_key": "attendance",
                "filters": {"year": "2026"},
            }),
            content_type="application/json",
        )
        preset_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/report-filters/presets/{preset_id}",
            data=json.dumps({"name": "New Name"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "New Name"

    def test_update_preset_filters(self, monkeypatch):
        """PUT updates the filters JSON."""
        client = _client(monkeypatch)
        create_resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({
                "name": "Filter Update",
                "report_key": "attendance",
                "filters": {"year": "2025"},
            }),
            content_type="application/json",
        )
        preset_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/report-filters/presets/{preset_id}",
            data=json.dumps({"filters": {"year": "2026", "term": "Term 2"}}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["filters"]["year"] == "2026"
        assert data["filters"]["term"] == "Term 2"

    def test_delete_preset(self, monkeypatch):
        """DELETE /api/report-filters/presets/<id> deletes the preset."""
        client = _client(monkeypatch)
        create_resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({
                "name": "Delete Me",
                "report_key": "attendance",
                "filters": {"year": "2026"},
            }),
            content_type="application/json",
        )
        preset_id = create_resp.get_json()["id"]

        resp = client.delete(f"/api/report-filters/presets/{preset_id}")
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

        # Verify it's gone
        get_resp = client.get(f"/api/report-filters/presets/{preset_id}")
        assert get_resp.status_code == 404

    def test_delete_preset_not_found(self, monkeypatch):
        """DELETE for non-existent preset returns 404."""
        client = _client(monkeypatch)
        resp = client.delete("/api/report-filters/presets/9999")
        assert resp.status_code == 404

    def test_unauthorized_user_cannot_access_other_preset(self, monkeypatch):
        """A second user cannot get/update/delete another user's preset."""
        app_mod = importlib.import_module("app")
        client = _client(monkeypatch)

        # Save a preset as admin (user_id=1)
        create_resp = client.post(
            "/api/report-filters/presets",
            data=json.dumps({
                "name": "Admin Preset",
                "report_key": "attendance",
                "filters": {"year": "2026"},
            }),
            content_type="application/json",
        )
        preset_id = create_resp.get_json()["id"]

        # Create a second user in the DB
        with app_mod.app.app_context():
            u2 = app_mod.User(id=2, username="user2", password_hash="x")
            app_mod.db.session.add(u2)
            app_mod.db.session.commit()

        # Create a new client session as user2
        client2 = app_mod.app.test_client()
        with client2.session_transaction() as sess:
            sess["_user_id"] = "2"
            sess["_fresh"] = True

        # GET should return 403
        resp = client2.get(f"/api/report-filters/presets/{preset_id}")
        assert resp.status_code == 403

        # PUT should return 403
        resp = client2.put(
            f"/api/report-filters/presets/{preset_id}",
            data=json.dumps({"name": "Hacked"}),
            content_type="application/json",
        )
        assert resp.status_code == 403

        # DELETE should return 403
        resp = client2.delete(f"/api/report-filters/presets/{preset_id}")
        assert resp.status_code == 403
