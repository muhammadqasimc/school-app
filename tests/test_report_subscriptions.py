"""
Tests for ReportSubscription model and CRUD API.
"""
import json
import importlib


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
        # Create a preset to reference
        p = app_mod.ReportFilterPreset(
            id=1,
            user_id=1,
            name="My Preset",
            report_key="general-overview",
            filters_json=json.dumps({"year": "2026", "term": "Term 1"}),
        )
        app_mod.db.session.add(p)
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


# ── Model Tests ──────────────────────────────────────────────────────────────


class TestReportSubscriptionModel:
    """Verify the model exists and can store/query data."""

    def test_create_subscription(self, monkeypatch):
        """Create and retrieve a ReportSubscription."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            # Create a user and preset first
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(
                id=1, user_id=1, name="My Preset", report_key="general-overview",
                filters_json=json.dumps({"year": "2026"}),
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()

            sub = app_mod.ReportSubscription(
                user_id=1,
                preset_id=1,
                name="My Subscription",
                schedule_type="weekly",
                schedule_params_json=json.dumps({"day_of_week": "monday"}),
                delivery_channel="email",
                is_active=True,
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            fetched = app_mod.db.session.get(app_mod.ReportSubscription, sub.id)
            assert fetched is not None
            assert fetched.name == "My Subscription"
            assert fetched.schedule_type == "weekly"
            assert json.loads(fetched.schedule_params_json) == {"day_of_week": "monday"}
            assert fetched.delivery_channel == "email"
            assert fetched.is_active is True
            assert fetched.user_id == 1
            assert fetched.preset_id == 1

    def test_subscription_defaults(self, monkeypatch):
        """Verify default values for is_active, schedule_type, delivery_channel."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(
                id=1, user_id=1, name="Preset", report_key="attendance",
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()

            sub = app_mod.ReportSubscription(
                user_id=1,
                preset_id=1,
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            assert sub.schedule_type == "daily"
            assert sub.schedule_params_json == "{}"
            assert sub.delivery_channel == "in_app"
            assert sub.is_active is True
            assert sub.name is None
            assert sub.last_run_at is None
            assert sub.created_at is not None
            assert sub.updated_at is not None

    def test_subscription_schedule_params(self, monkeypatch):
        """Verify schedule_params_json serialization/deserialization."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(
                id=1, user_id=1, name="Preset", report_key="attendance",
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()

            params = {"day_of_week": "monday", "hour": 8, "minute": 30}
            sub = app_mod.ReportSubscription(
                user_id=1,
                preset_id=1,
                schedule_type="weekly",
                schedule_params_json=json.dumps(params),
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            fetched = app_mod.db.session.get(app_mod.ReportSubscription, sub.id)
            assert json.loads(fetched.schedule_params_json) == params

    def test_subscription_relationship_to_preset(self, monkeypatch):
        """Verify relationship to ReportFilterPreset works (preset.subscriptions)."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(
                id=1, user_id=1, name="Preset", report_key="attendance",
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()

            sub1 = app_mod.ReportSubscription(user_id=1, preset_id=1, schedule_type="daily")
            sub2 = app_mod.ReportSubscription(user_id=1, preset_id=1, schedule_type="weekly")
            app_mod.db.session.add_all([sub1, sub2])
            app_mod.db.session.commit()

            # Verify backref from preset
            assert p.subscriptions.count() == 2
            assert sub1.preset is p
            assert sub2.preset is p

            # Verify cascade delete
            app_mod.db.session.delete(p)
            app_mod.db.session.commit()
            remaining = app_mod.ReportSubscription.query.all()
            assert len(remaining) == 0


# ── API Tests ────────────────────────────────────────────────────────────────


class TestReportSubscriptionAPI:
    """Test the CRUD API endpoints for subscriptions."""

    def _create_subscription(self, client, overrides=None):
        """Helper: create a subscription via API and return response JSON."""
        data = {
            "preset_id": 1,
            "name": "Test Subscription",
            "schedule_type": "daily",
            "schedule_params": {"hour": 8},
            "delivery_channel": "in_app",
            "is_active": True,
        }
        if overrides:
            data.update(overrides)
        resp = client.post(
            "/api/report-subscriptions",
            data=json.dumps(data),
            content_type="application/json",
        )
        return resp

    def test_list_subscriptions(self, monkeypatch):
        """POST 2 subscriptions, GET list, verify count and fields."""
        client = _client(monkeypatch)
        self._create_subscription(client, {"name": "Sub One", "schedule_type": "daily"})
        self._create_subscription(client, {"name": "Sub Two", "schedule_type": "weekly"})

        resp = client.get("/api/report-subscriptions")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        names = [s["name"] for s in data]
        assert "Sub One" in names
        assert "Sub Two" in names
        # Check fields
        for s in data:
            assert "id" in s
            assert "preset_id" in s
            assert "preset_name" in s
            assert "schedule_params" in s
            assert "created_at" in s
            assert "updated_at" in s

    def test_create_subscription(self, monkeypatch):
        """POST valid subscription, verify response."""
        client = _client(monkeypatch)
        resp = self._create_subscription(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Test Subscription"
        assert data["schedule_type"] == "daily"
        assert data["delivery_channel"] == "in_app"
        assert data["is_active"] is True
        assert data["preset_name"] == "My Preset"
        assert "id" in data
        assert data["schedule_params"]["hour"] == 8

    def test_create_subscription_missing_preset_id(self, monkeypatch):
        """POST without preset_id, expect 400."""
        client = _client(monkeypatch)
        resp = client.post(
            "/api/report-subscriptions",
            data=json.dumps({"name": "No Preset"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_subscription_invalid_preset(self, monkeypatch):
        """POST with non-existent preset_id, expect 400."""
        client = _client(monkeypatch)
        resp = client.post(
            "/api/report-subscriptions",
            data=json.dumps({"preset_id": 9999, "name": "Bad Preset"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_get_subscription(self, monkeypatch):
        """POST then GET by id."""
        client = _client(monkeypatch)
        create_resp = self._create_subscription(client)
        sub_id = create_resp.get_json()["id"]

        resp = client.get(f"/api/report-subscriptions/{sub_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Test Subscription"
        assert data["schedule_type"] == "daily"

    def test_get_subscription_not_found(self, monkeypatch):
        """GET non-existent id, expect 404."""
        client = _client(monkeypatch)
        resp = client.get("/api/report-subscriptions/9999")
        assert resp.status_code == 404

    def test_update_subscription(self, monkeypatch):
        """POST, PUT new name/schedule, verify updated."""
        client = _client(monkeypatch)
        create_resp = self._create_subscription(client)
        sub_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/report-subscriptions/{sub_id}",
            data=json.dumps({
                "name": "Updated Sub",
                "schedule_type": "weekly",
                "schedule_params": {"day_of_week": "monday"},
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Updated Sub"
        assert data["schedule_type"] == "weekly"
        assert data["schedule_params"]["day_of_week"] == "monday"

    def test_update_subscription_toggle_active(self, monkeypatch):
        """PUT is_active=False, verify."""
        client = _client(monkeypatch)
        create_resp = self._create_subscription(client)
        sub_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/report-subscriptions/{sub_id}",
            data=json.dumps({"is_active": False}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["is_active"] is False

    def test_delete_subscription(self, monkeypatch):
        """POST, DELETE, verify gone."""
        client = _client(monkeypatch)
        create_resp = self._create_subscription(client)
        sub_id = create_resp.get_json()["id"]

        resp = client.delete(f"/api/report-subscriptions/{sub_id}")
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

        # Verify it's gone
        get_resp = client.get(f"/api/report-subscriptions/{sub_id}")
        assert get_resp.status_code == 404

    def test_delete_subscription_not_found(self, monkeypatch):
        """DELETE non-existent, expect 404."""
        client = _client(monkeypatch)
        resp = client.delete("/api/report-subscriptions/9999")
        assert resp.status_code == 404

    def test_unauthorized_user_cannot_access_other_subscription(self, monkeypatch):
        """Create as user 1, login as user 2, verify 403."""
        app_mod = importlib.import_module("app")
        client = _client(monkeypatch)

        # Create a subscription as admin (user_id=1)
        create_resp = self._create_subscription(client)
        sub_id = create_resp.get_json()["id"]

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
        resp = client2.get(f"/api/report-subscriptions/{sub_id}")
        assert resp.status_code == 403

        # PUT should return 403
        resp = client2.put(
            f"/api/report-subscriptions/{sub_id}",
            data=json.dumps({"name": "Hacked"}),
            content_type="application/json",
        )
        assert resp.status_code == 403

        # DELETE should return 403
        resp = client2.delete(f"/api/report-subscriptions/{sub_id}")
        assert resp.status_code == 403
