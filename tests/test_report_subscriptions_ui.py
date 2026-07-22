"""
Tests for the subscription management UI page route and rendering.
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
            name="Test Preset",
            report_key="general-overview",
            filters_json=json.dumps({"year": "2026", "term": "Term 1"}),
        )
        app_mod.db.session.add(p)
        # Create a subscription
        sub = app_mod.ReportSubscription(
            id=1,
            user_id=1,
            preset_id=1,
            name="My Subscription",
            schedule_type="daily",
            schedule_params_json=json.dumps({"hour": 8}),
            delivery_channel="in_app",
            is_active=True,
        )
        app_mod.db.session.add(sub)
        app_mod.db.session.commit()

    monkeypatch.setattr(app_mod, "_management_user_can_access_reports", lambda _user: True)
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True
    return client


class TestReportSubscriptionsUIPage:
    """Test the subscription management UI page."""

    def test_page_loads_ok(self, monkeypatch):
        """GET /management/report-subscriptions returns 200."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        assert resp.status_code == 200

    def test_page_title_and_heading(self, monkeypatch):
        """Page contains expected title and heading."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "Report Subscriptions" in html
        assert "Your Subscriptions" in html
        assert "New Subscription" in html

    def test_page_shows_back_link(self, monkeypatch):
        """Page has a back link to management dashboard."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "Back to Reports" in html

    def test_page_shows_create_modal(self, monkeypatch):
        """Page has the subscription creation modal."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "subscriptionModal" in html
        assert "Filter Preset" in html
        assert "Delivery Channel" in html

    def test_page_has_presets_in_template(self, monkeypatch):
        """Page shows available presets in the preset dropdown."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "Test Preset" in html
        assert "general-overview" in html

    def test_page_has_delete_modal(self, monkeypatch):
        """Page has the delete confirmation modal."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "deleteModal" in html
        assert "Delete Subscription" in html

    def test_page_has_css_and_js_assets(self, monkeypatch):
        """Page loads management-reports.css."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "management-reports.css" in html
