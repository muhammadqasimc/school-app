"""
Tests for Report Subscriptions UI page.
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


class TestReportSubscriptionsUI:
    """Test the subscription management UI page."""

    def test_page_returns_200(self, monkeypatch):
        """GET /management/report-subscriptions should return 200 for authorized user."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        assert resp.status_code == 200

    def test_page_title_and_heading(self, monkeypatch):
        """Page should contain the expected heading."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "Report Subscriptions" in html
        assert "<h3" in html
        assert "fa-bell" in html

    def test_page_has_back_link(self, monkeypatch):
        """Page should have a back link to management dashboard."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "/management" in html or "management_dashboard" in html
        assert "Back to Reports" in html or "back" in html.lower()

    def test_page_has_new_subscription_button(self, monkeypatch):
        """Page should have a 'New Subscription' button that targets the modal."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "New Subscription" in html
        assert "data-bs-target=\"#subscriptionModal\"" in html

    def test_page_has_subscriptions_table(self, monkeypatch):
        """Page should have the subscriptions table."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "subscriptionsTable" in html
        assert "Your Subscriptions" in html
        assert "Name" in html and "Preset" in html and "Schedule" in html
        assert "Channel" in html and "Status" in html and "Actions" in html

    def test_page_has_modal_for_create_edit(self, monkeypatch):
        """Page should have a modal form for creating/editing subscriptions."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "subscriptionModal" in html
        assert "sub-name" in html
        assert "sub-preset" in html
        assert "sub-schedule-type" in html
        assert "sub-channel" in html
        assert "sub-active" in html

    def test_page_has_delete_confirmation_modal(self, monkeypatch):
        """Page should have a delete confirmation modal."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "deleteModal" in html
        assert "confirmDeleteBtn" in html

    def test_page_lists_presets_in_dropdown(self, monkeypatch):
        """The preset dropdown should include presets from the DB."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        # The preset "My Preset (general-overview)" should appear
        assert "My Preset" in html
        assert "general-overview" in html

    def test_page_inline_js_has_core_functions(self, monkeypatch):
        """The inline JS should have the expected subscription management functions."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        # Core JS functions should be defined
        assert "function loadSubscriptions" in html
        assert "function saveSubscription" in html
        assert "function deleteSubscription" in html
        assert "function toggleActive" in html
        assert "function editSubscription" in html
        assert "function resetSubscriptionForm" in html

    def test_page_reports_js_shows_loading(self, monkeypatch):
        """The table body should show a loading message initially."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "Loading subscriptions" in html

    def test_page_has_extra_css_block(self, monkeypatch):
        """Page should include management-reports.css."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "management-reports.css" in html

    def test_unauthorized_user_gets_403(self, monkeypatch):
        """A user without access should get 403."""
        app_mod = importlib.import_module("app")
        app_mod.app.config["TESTING"] = True
        app_mod.app.config["LOGIN_DISABLED"] = False
        app_mod.app.config["WTF_CSRF_ENABLED"] = False
        app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        with app_mod.app.app_context():
            app_mod.db.drop_all()
            app_mod.db.create_all()
            u = app_mod.User(id=1, username="user", password_hash="x")
            app_mod.db.session.add(u)
            app_mod.db.session.commit()

        monkeypatch.setattr(app_mod, "is_analytics_user", lambda _user: False)
        monkeypatch.setattr(
            app_mod, "_management_user_can_access_reports", lambda _user: False
        )
        client = app_mod.app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True

        resp = client.get("/management/report-subscriptions")
        assert resp.status_code == 403

    def test_page_has_schedule_params_ui_controls(self, monkeypatch):
        """Page should have day-of-week, day-of-month, and hour controls for schedule params."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "sub-day-of-week" in html
        assert "sub-day-of-month" in html
        assert "sub-hour" in html

    def test_page_has_schedule_type_selector(self, monkeypatch):
        """Page should have schedule type options: daily, weekly, monthly."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "Daily" in html
        assert "Weekly" in html
        assert "Monthly" in html

    def test_schedule_params_ui_js_function(self, monkeypatch):
        """The JS function updateScheduleParamsUI should exist."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "function updateScheduleParamsUI" in html

    def test_page_has_format_helper_functions(self, monkeypatch):
        """The inline JS should have format helpers."""
        client = _client(monkeypatch)
        resp = client.get("/management/report-subscriptions")
        html = resp.data.decode("utf-8")
        assert "function formatSchedule" in html
        assert "function formatLastRun" in html
        assert "function getScheduleParams" in html
