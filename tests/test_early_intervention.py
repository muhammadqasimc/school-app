"""Tests for the Early Intervention tracking system.

Exercises the three new models, the management report handler,
and the CRUD API endpoints for interventions and referrals.
"""

import importlib
import json


# ── Fixture helpers ──────────────────────────────────────────────────────────

def _client(monkeypatch):
    """Return a test client with login disabled and a clean schema."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["TESTING"] = True
    app_mod.app.config["LOGIN_DISABLED"] = False  # Need real user for IDs
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # Ensure tables exist
    with app_mod.app.app_context():
        app_mod.db.create_all()
        # Create a dummy admin user so foreign keys to user.id work
        if not app_mod.User.query.get(1):
            u = app_mod.User(
                id=1,
                username="test_admin",
                password_hash="x",
                is_manager=True,
            )
            app_mod.db.session.add(u)
            app_mod.db.session.commit()
    monkeypatch.setattr(app_mod, "is_analytics_user", lambda _user: True)
    monkeypatch.setattr(app_mod, "_management_user_can_access_reports", lambda _user: True)
    client = app_mod.app.test_client()
    # Log in the test user via session
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True
    return client


def _ensure_tables(monkeypatch):
    """Import the module and create all tables."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app_mod.app.app_context():
        app_mod.db.create_all()
    return app_mod


# ── Tests ────────────────────────────────────────────────────────────────────


class TestEarlyInterventionModels:
    """Verify the three new models exist and can be created/queried."""

    def test_create_intervention_model(self, monkeypatch):
        """Create an EarlyIntervention record and check its fields."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            # Create a minimal intervention
            i = app_mod.EarlyIntervention(
                learner_id="L1001",
                learner_name="John Doe",
                grade="8",
                class_name="8A",
                risk_type="grade",
                intervention_type="academic_support",
                description="Struggling with math",
                created_by_user_id=1,
            )
            app_mod.db.session.add(i)
            app_mod.db.session.commit()
            fetched = app_mod.EarlyIntervention.query.get(i.id)
            assert fetched is not None
            assert fetched.learner_id == "L1001"
            assert fetched.risk_type == "grade"
            assert fetched.intervention_type == "academic_support"
            assert fetched.status == "open"  # default
            assert fetched.created_by_user_id == 1

    def test_default_status_is_open(self, monkeypatch):
        """Interventions should default to status='open'."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            i = app_mod.EarlyIntervention(
                learner_id="L1002",
                risk_type="attendance",
                intervention_type="parent_meeting",
                created_by_user_id=1,
            )
            app_mod.db.session.add(i)
            app_mod.db.session.commit()
            assert i.status == "open"

    def test_intervention_referral_model(self, monkeypatch):
        """Create an InterventionReferral linked to an intervention."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            i = app_mod.EarlyIntervention(
                learner_id="L1003",
                risk_type="discipline",
                intervention_type="counseling",
                created_by_user_id=1,
            )
            app_mod.db.session.add(i)
            app_mod.db.session.flush()
            r = app_mod.InterventionReferral(
                intervention_id=i.id,
                referred_to="counselor",
                reason="Needs behavioral counseling",
                created_by_user_id=1,
            )
            app_mod.db.session.add(r)
            app_mod.db.session.commit()
            assert r.id is not None
            assert r.status == "pending"  # default
            assert r.intervention_id == i.id

    def test_intervention_notification_model(self, monkeypatch):
        """Create an InterventionNotification linked to an intervention."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            i = app_mod.EarlyIntervention(
                learner_id="L1004",
                risk_type="general",
                intervention_type="other",
                created_by_user_id=1,
            )
            app_mod.db.session.add(i)
            app_mod.db.session.flush()
            n = app_mod.InterventionNotification(
                intervention_id=i.id,
                learner_id="L1004",
                recipient_phone="+27123456789",
                message_snapshot="Test notification",
                sent_by_user_id=1,
            )
            app_mod.db.session.add(n)
            app_mod.db.session.commit()
            assert n.id is not None
            assert n.channel == "sms"  # default


class TestEarlyInterventionAPI:
    """Test the CRUD API endpoints for interventions and referrals."""

    def test_create_intervention(self, monkeypatch):
        """POST /api/early-intervention/create returns the new intervention."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2001",
                "learner_name": "Jane Smith",
                "grade": "10",
                "class_name": "10B",
                "risk_type": "grade",
                "intervention_type": "tutoring",
                "description": "Falling behind in science",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["intervention"]["learner_id"] == "L2001"
        assert data["intervention"]["risk_type"] == "grade"
        assert data["intervention"]["status"] == "open"

    def test_list_interventions(self, monkeypatch):
        """GET /api/early-intervention/list returns interventions."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        # First create one
        client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2002",
                "learner_name": "Bob Wilson",
                "risk_type": "attendance",
                "intervention_type": "parent_meeting",
            }),
            content_type="application/json",
        )
        resp = client.get("/api/early-intervention/list")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert len(data["interventions"]) >= 1
        # Should contain our new intervention
        ids = [i["id"] for i in data["interventions"]]
        assert len(ids) >= 1

    def test_list_interventions_with_filters(self, monkeypatch):
        """Filter by status and risk_type."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        # Create two interventions with different risk types
        client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2003",
                "learner_name": "Alice A",
                "risk_type": "grade",
                "intervention_type": "tutoring",
            }),
            content_type="application/json",
        )
        client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2004",
                "learner_name": "Bob B",
                "risk_type": "attendance",
                "intervention_type": "parent_meeting",
            }),
            content_type="application/json",
        )
        # Filter by grade risk
        resp = client.get("/api/early-intervention/list?risk_type=grade")
        assert resp.status_code == 200
        data = resp.get_json()
        assert all(i["risk_type"] == "grade" for i in data["interventions"])

    def test_get_intervention_detail(self, monkeypatch):
        """GET /api/early-intervention/detail returns single intervention with referrals."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        # Create intervention
        create_resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2005",
                "learner_name": "Charlie C",
                "risk_type": "discipline",
                "intervention_type": "counseling",
            }),
            content_type="application/json",
        )
        iid = create_resp.get_json()["intervention"]["id"]
        # Add a referral
        client.post(
            "/api/early-intervention/referral/create",
            data=json.dumps({
                "intervention_id": iid,
                "referred_to": "counselor",
                "reason": "Behavioral issues",
            }),
            content_type="application/json",
        )
        # Fetch detail
        resp = client.get(f"/api/early-intervention/detail?id={iid}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["intervention"]["id"] == iid
        assert len(data["referrals"]) >= 1

    def test_update_intervention_status(self, monkeypatch):
        """POST /api/early-intervention/update can change status."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        create_resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2006",
                "learner_name": "Diana D",
                "risk_type": "grade",
                "intervention_type": "academic_support",
            }),
            content_type="application/json",
        )
        iid = create_resp.get_json()["intervention"]["id"]
        resp = client.post(
            "/api/early-intervention/update",
            data=json.dumps({
                "id": iid,
                "status": "resolved",
                "outcome_notes": "Student has improved significantly",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["intervention"]["status"] == "resolved"

    def test_create_referral(self, monkeypatch):
        """POST /api/early-intervention/referral/create stores a referral."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        create_resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2007",
                "learner_name": "Eve E",
                "risk_type": "discipline",
                "intervention_type": "counseling",
            }),
            content_type="application/json",
        )
        iid = create_resp.get_json()["intervention"]["id"]
        resp = client.post(
            "/api/early-intervention/referral/create",
            data=json.dumps({
                "intervention_id": iid,
                "referred_to": "academic_head",
                "referred_to_name": "Mr. Principal",
                "reason": "Requires academic review",
                "notes": "Urgent case",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["referral"]["referred_to"] == "academic_head"
        assert data["referral"]["status"] == "pending"

    def test_update_referral_status(self, monkeypatch):
        """POST /api/early-intervention/referral/update changes referral status."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        create_resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2008",
                "learner_name": "Frank F",
                "risk_type": "grade",
                "intervention_type": "mentoring",
            }),
            content_type="application/json",
        )
        iid = create_resp.get_json()["intervention"]["id"]
        ref_resp = client.post(
            "/api/early-intervention/referral/create",
            data=json.dumps({
                "intervention_id": iid,
                "referred_to": "support_staff",
                "reason": "Extra support needed",
            }),
            content_type="application/json",
        )
        rid = ref_resp.get_json()["referral"]["id"]
        resp = client.post(
            "/api/early-intervention/referral/update",
            data=json.dumps({
                "id": rid,
                "status": "accepted",
                "outcome": "Support plan initiated",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["referral"]["status"] == "accepted"

    def test_from_at_risk_endpoint(self, monkeypatch):
        """GET /api/early-intervention/from-at-risk checks which learners have open interventions."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        # Create an open intervention for L2009
        client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2009",
                "learner_name": "Grace G",
                "risk_type": "attendance",
                "intervention_type": "parent_meeting",
            }),
            content_type="application/json",
        )
        # Close one for L2010
        cr = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2010",
                "learner_name": "Henry H",
                "risk_type": "grade",
                "intervention_type": "tutoring",
            }),
            content_type="application/json",
        )
        iid = cr.get_json()["intervention"]["id"]
        client.post(
            "/api/early-intervention/update",
            data=json.dumps({"id": iid, "status": "closed"}),
            content_type="application/json",
        )
        resp = client.get("/api/early-intervention/from-at-risk?learner_ids=L2009,L2010,L2011")
        assert resp.status_code == 200
        data = resp.get_json()
        # L2009 has open intervention, L2010 is closed (not open), L2011 has none
        assert "L2009" in data["open_intervention_learner_ids"]
        assert "L2010" not in data["open_intervention_learner_ids"]

    def test_access_denied_for_unauthorized(self, monkeypatch):
        """Non-management users get 403 on management endpoints."""
        app_mod = _ensure_tables(monkeypatch)
        app_mod.app.config["TESTING"] = True
        app_mod.app.config["LOGIN_DISABLED"] = True
        app_mod.app.config["WTF_CSRF_ENABLED"] = False
        monkeypatch.setattr(app_mod, "_management_user_can_access_reports", lambda _user: False)
        client = app_mod.app.test_client()

        # Try to list interventions
        resp = client.get("/api/early-intervention/list")
        assert resp.status_code == 403

        # Try to create
        resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L2099",
                "risk_type": "general",
                "intervention_type": "other",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 403

    def test_create_intervention_validates_required_fields(self, monkeypatch):
        """Missing required fields return 400."""
        app_mod = _ensure_tables(monkeypatch)
        client = _client(monkeypatch)
        resp = client.post(
            "/api/early-intervention/create",
            data=json.dumps({"learner_id": "L2100"}),  # missing risk_type, intervention_type
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestEarlyInterventionReportHandler:
    """Test the management report handler for early intervention."""

    def test_report_handler_returns_kpis(self, monkeypatch):
        """The early-intervention report handler returns expected KPI structure."""
        client = _client(monkeypatch)

        # Create a few interventions
        client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L3001",
                "learner_name": "Test A",
                "risk_type": "grade",
                "intervention_type": "tutoring",
            }),
            content_type="application/json",
        )
        client.post(
            "/api/early-intervention/create",
            data=json.dumps({
                "learner_id": "L3002",
                "learner_name": "Test B",
                "risk_type": "attendance",
                "intervention_type": "parent_meeting",
            }),
            content_type="application/json",
        )

        # Hit the generic report API with the early-intervention key
        resp = client.get("/api/management-report?report_key=early-intervention")
        assert resp.status_code == 200
        data = resp.get_json()
        rd = data.get("reportData", {})
        kpis = rd.get("kpis", {})
        assert "openInterventions" in kpis
        assert kpis["openInterventions"] >= 2
        assert "pendingReferrals" in kpis
        assert "totalNotifications" in kpis

    def test_report_handler_in_registry(self, monkeypatch):
        """The early-intervention report key is registered."""
        app_mod = _ensure_tables(monkeypatch)
        assert any(
            r["key"] == "early-intervention"
            for r in app_mod.MANAGEMENT_REPORT_REGISTRY
        ), "early-intervention not found in MANAGEMENT_REPORT_REGISTRY"
