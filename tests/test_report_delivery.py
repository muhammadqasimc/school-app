"""
Tests for ReportDelivery model and the process-report-subscriptions CLI command.
"""
import json
import importlib


def _ensure_tables(monkeypatch):
    """Import the module and create all tables (drops first)."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app_mod.app.app_context():
        app_mod.db.drop_all()
        app_mod.db.create_all()
    return app_mod


class TestReportDeliveryModel:
    """Verify the ReportDelivery model exists and works."""

    def _seed(self, app_mod):
        """Create a user, preset, and subscription. Caller must be inside app_context."""
        u = app_mod.User(id=1, username="admin", password_hash="x")
        app_mod.db.session.add(u)
        p = app_mod.ReportFilterPreset(
            id=1, user_id=1, name="My Preset", report_key="general-overview",
            filters_json=json.dumps({"year": "2026", "term": "Term 1"}),
        )
        app_mod.db.session.add(p)
        app_mod.db.session.commit()
        sub = app_mod.ReportSubscription(
            id=1, user_id=1, preset_id=1, name="Daily Report",
            schedule_type="daily",
            schedule_params_json=json.dumps({"hour": 8}),
            delivery_channel="in_app", is_active=True,
        )
        app_mod.db.session.add(sub)
        app_mod.db.session.commit()
        return u, p, sub

    def test_create_delivery(self, monkeypatch):
        """Create and retrieve a ReportDelivery record."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u, p, sub = self._seed(app_mod)

            delivery = app_mod.ReportDelivery(
                subscription_id=sub.id,
                user_id=u.id,
                status="delivered",
                channel="in_app",
                details_json=json.dumps({"report_key": "general-overview", "filters": {"year": "2026"}}),
            )
            app_mod.db.session.add(delivery)
            app_mod.db.session.commit()

            fetched = app_mod.db.session.get(app_mod.ReportDelivery, delivery.id)
            assert fetched is not None
            assert fetched.status == "delivered"
            assert fetched.channel == "in_app"
            assert fetched.subscription_id == sub.id
            assert fetched.user_id == u.id
            assert fetched.delivered_at is not None

    def test_delivery_defaults(self, monkeypatch):
        """Verify default values on ReportDelivery."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u, p, sub = self._seed(app_mod)

            delivery = app_mod.ReportDelivery(
                subscription_id=sub.id,
                user_id=u.id,
            )
            app_mod.db.session.add(delivery)
            app_mod.db.session.commit()

            assert delivery.status == "pending"
            assert delivery.channel == "in_app"
            assert delivery.details_json == "{}"
            assert delivery.error_message is None

    def test_delivery_cascade_on_subscription_delete(self, monkeypatch):
        """Deleting a subscription cascades to its deliveries."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u, p, sub = self._seed(app_mod)

            d1 = app_mod.ReportDelivery(subscription_id=sub.id, user_id=u.id)
            d2 = app_mod.ReportDelivery(subscription_id=sub.id, user_id=u.id)
            app_mod.db.session.add_all([d1, d2])
            app_mod.db.session.commit()

            assert app_mod.ReportDelivery.query.count() == 2

            app_mod.db.session.delete(sub)
            app_mod.db.session.commit()

            assert app_mod.ReportDelivery.query.count() == 0

    def test_subscription_deliveries_relationship(self, monkeypatch):
        """Verify sub.deliveries backref works."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u, p, sub = self._seed(app_mod)

            d1 = app_mod.ReportDelivery(subscription_id=sub.id, user_id=u.id)
            d2 = app_mod.ReportDelivery(subscription_id=sub.id, user_id=u.id)
            app_mod.db.session.add_all([d1, d2])
            app_mod.db.session.commit()

            assert sub.deliveries.count() == 2


class TestProcessReportSubscriptionsCLI:
    """Test the process-report-subscriptions CLI command logic."""

    def _run_cli_inline(self, app_mod):
        """Simulate the CLI command logic inline for testability.
        Caller must be inside app_context."""
        from datetime import date, timedelta, datetime
        now = datetime.utcnow()
        today = date.today()
        cutoff = now - timedelta(hours=1)
        processed = 0
        due = 0

        subs = app_mod.ReportSubscription.query.filter_by(is_active=True).all()
        for sub in subs:
            skip = False
            if sub.last_run_at and sub.last_run_at > cutoff:
                skip = True
            if skip:
                continue

            sub_due = False
            sp = json.loads(sub.schedule_params_json or "{}")

            if sub.schedule_type == "daily":
                if not sub.last_run_at or sub.last_run_at.date() < today:
                    sub_due = True
            elif sub.schedule_type == "weekly":
                dow_target = (sp.get("day_of_week") or "monday").lower().strip()
                dow_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                           "friday": 4, "saturday": 5, "sunday": 6}
                if today.weekday() == dow_map.get(dow_target, 0):
                    if not sub.last_run_at or sub.last_run_at.date() < today:
                            sub_due = True
            elif sub.schedule_type == "monthly":
                dom = int(sp.get("day_of_month", 1))
                if today.day == dom:
                    if not sub.last_run_at or sub.last_run_at.date() < today:
                        sub_due = True

            if sub_due:
                due += 1
                preset = sub.preset
                delivery = app_mod.ReportDelivery(
                    subscription_id=sub.id,
                    user_id=sub.user_id,
                    status="delivered",
                    channel=sub.delivery_channel,
                    details_json=json.dumps({
                        "report_key": preset.report_key if preset else None,
                        "filters": json.loads(preset.filters_json) if preset and preset.filters_json else {},
                        "preset_name": preset.name if preset else None,
                        "subscription_name": sub.name,
                    }),
                )
                app_mod.db.session.add(delivery)
                sub.last_run_at = now
                processed += 1
        app_mod.db.session.commit()
        return due, processed

    def test_never_run_subscription_is_due(self, monkeypatch):
        """A subscription with last_run_at=None should be due."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(
                id=1, user_id=1, name="Preset", report_key="general-overview",
                filters_json=json.dumps({"year": "2026"}),
            )
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            sub = app_mod.ReportSubscription(
                id=1, user_id=1, preset_id=1, name="Daily",
                schedule_type="daily", is_active=True,
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()
            assert sub.last_run_at is None

            due, processed = self._run_cli_inline(app_mod)
            assert due == 1
            assert processed == 1

            dcount = app_mod.ReportDelivery.query.count()
            assert dcount == 1
            d = app_mod.ReportDelivery.query.first()
            assert d.status == "delivered"
            details = json.loads(d.details_json)
            assert details["report_key"] == "general-overview"

    def test_already_run_today_skipped(self, monkeypatch):
        """A subscription already run within the grace window should be skipped."""
        from datetime import datetime, timedelta
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(id=1, user_id=1, name="P", report_key="attendance")
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            sub = app_mod.ReportSubscription(
                id=1, user_id=1, preset_id=1, name="Daily",
                schedule_type="daily", is_active=True,
                last_run_at=datetime.utcnow() - timedelta(minutes=5),
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            due, processed = self._run_cli_inline(app_mod)
            assert due == 0
            assert processed == 0

    def test_old_run_is_due(self, monkeypatch):
        """A subscription run yesterday should be due for daily."""
        from datetime import datetime, timedelta
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(id=1, user_id=1, name="P", report_key="attendance")
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            sub = app_mod.ReportSubscription(
                id=1, user_id=1, preset_id=1, name="Daily",
                schedule_type="daily", is_active=True,
                last_run_at=datetime.utcnow() - timedelta(hours=25),
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            due, processed = self._run_cli_inline(app_mod)
            assert due == 1
            assert processed == 1

    def test_weekly_subscription_on_wrong_day_skipped(self, monkeypatch):
        """Weekly subscription should only run on configured day of week."""
        from datetime import date
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(id=1, user_id=1, name="W", report_key="attendance")
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            today = date.today()
            target_dow = "saturday" if today.weekday() != 5 else "sunday"
            sub = app_mod.ReportSubscription(
                id=1, user_id=1, preset_id=1, name="Weekly",
                schedule_type="weekly",
                schedule_params_json=json.dumps({"day_of_week": target_dow}),
                is_active=True,
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            due, processed = self._run_cli_inline(app_mod)
            assert due == 0
            assert processed == 0

    def test_inactive_subscription_skipped(self, monkeypatch):
        """Inactive subscriptions should be skipped."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(id=1, user_id=1, name="I", report_key="attendance")
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            sub = app_mod.ReportSubscription(
                id=1, user_id=1, preset_id=1, name="Inactive",
                schedule_type="daily", is_active=False,
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            due, processed = self._run_cli_inline(app_mod)
            assert due == 0
            assert processed == 0

    def test_monthly_subscription_on_wrong_day_skipped(self, monkeypatch):
        """Monthly subscription should only run on configured day of month."""
        from datetime import date
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            u = app_mod.User(id=1, username="admin", password_hash="x")
            app_mod.db.session.add(u)
            p = app_mod.ReportFilterPreset(id=1, user_id=1, name="M", report_key="finance-overview")
            app_mod.db.session.add(p)
            app_mod.db.session.commit()
            today = date.today()
            target_dom = 28 if today.day != 28 else 15
            sub = app_mod.ReportSubscription(
                id=1, user_id=1, preset_id=1, name="Monthly",
                schedule_type="monthly",
                schedule_params_json=json.dumps({"day_of_month": target_dom}),
                is_active=True,
            )
            app_mod.db.session.add(sub)
            app_mod.db.session.commit()

            due, processed = self._run_cli_inline(app_mod)
            assert due == 0
            assert processed == 0
