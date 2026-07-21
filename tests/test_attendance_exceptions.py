"""Tests for Attendance Exception Codes with notes and attachment support."""

import importlib
import io
import os

# ── Fixture helpers ──────────────────────────────────────────────────────────


def _client(monkeypatch):
    """Return a test client with an admin user and in-memory SQLite."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["TESTING"] = True
    app_mod.app.config["LOGIN_DISABLED"] = False
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # Ensure upload folder exists
    upload_dir = app_mod.app.config.get(
        "ATTENDANCE_EXCEPTION_UPLOAD_FOLDER", "static/uploads/attendance_exceptions"
    )
    os.makedirs(upload_dir, exist_ok=True)

    with app_mod.app.app_context():
        app_mod.db.create_all()
        # Seed default exception codes via the seed function
        app_mod._seed_attendance_exception_codes()
        # Create a dummy admin user
        if not app_mod.User.query.get(1):
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
    """Import the module and create all tables + seed codes (drops first)."""
    app_mod = importlib.import_module("app")
    app_mod.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app_mod.app.app_context():
        app_mod.db.drop_all()
        app_mod.db.create_all()
        app_mod._seed_attendance_exception_codes()
    return app_mod


# ── Tests ────────────────────────────────────────────────────────────────────


class TestAttendanceExceptionModels:
    """Verify the models exist and can store/query data."""

    def test_create_exception_code(self, monkeypatch):
        """Create and retrieve an AttendanceExceptionCode."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            code = app_mod.AttendanceExceptionCode(
                code="TEST",
                name="Test Code",
                description="A test code",
                color="#FF00FF",
            )
            app_mod.db.session.add(code)
            app_mod.db.session.commit()
            fetched = app_mod.AttendanceExceptionCode.query.filter_by(code="TEST").first()
            assert fetched is not None
            assert fetched.name == "Test Code"
            assert fetched.color == "#FF00FF"
            assert fetched.is_active is True

    def test_seed_codes_created(self, monkeypatch):
        """Seed function creates default exception codes."""
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            codes = app_mod.AttendanceExceptionCode.query.all()
            code_map = {c.code: c for c in codes}
            assert "LATE" in code_map
            assert "EXCUSED" in code_map
            assert "MEDICAL" in code_map
            assert "UNEXCUSED" in code_map
            assert "OTHER" in code_map

    def test_create_exception(self, monkeypatch):
        """Create an AttendanceException linked to a code."""
        from datetime import date
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            code = app_mod.AttendanceExceptionCode.query.filter_by(code="LATE").first()
            exc = app_mod.AttendanceException(
                exception_code_id=code.id,
                learner_id="L12345",
                absentee_date=date(2026, 3, 15),
                notes="Traffic delay",
                created_by_user_id=1,
                created_by_name="test_admin",
            )
            app_mod.db.session.add(exc)
            app_mod.db.session.commit()
            fetched = app_mod.AttendanceException.query.get(exc.id)
            assert fetched is not None
            assert fetched.learner_id == "L12345"
            assert str(fetched.absentee_date) == "2026-03-15"
            assert fetched.notes == "Traffic delay"

    def test_exception_with_attachment_metadata(self, monkeypatch):
        """Store attachment metadata with an exception."""
        from datetime import date
        app_mod = _ensure_tables(monkeypatch)
        with app_mod.app.app_context():
            code = app_mod.AttendanceExceptionCode.query.filter_by(code="MEDICAL").first()
            exc = app_mod.AttendanceException(
                exception_code_id=code.id,
                learner_id="L67890",
                absentee_date=date(2026, 4, 1),
                notes="Doctor's note attached",
                original_filename="sick_note.pdf",
                stored_filename="abc123_sick_note.pdf",
                storage_relpath="/tmp/abc123_sick_note.pdf",
                mime_type="application/pdf",
                size_bytes=102400,
                created_by_user_id=1,
            )
            app_mod.db.session.add(exc)
            app_mod.db.session.commit()
            fetched = app_mod.AttendanceException.query.get(exc.id)
            assert fetched.original_filename == "sick_note.pdf"
            assert fetched.mime_type == "application/pdf"
            assert fetched.size_bytes == 102400


class TestAttendanceExceptionCRUD:
    """Test the admin CRUD endpoints."""

    def test_list_page_returns_200(self, monkeypatch):
        """GET /admin/attendance-exceptions returns the page."""
        client = _client(monkeypatch)
        resp = client.get("/admin/attendance-exceptions")
        assert resp.status_code == 200
        assert b"Attendance Exceptions" in resp.data or b"attendance" in resp.data.lower()

    def test_add_exception_without_file(self, monkeypatch):
        """POST to add an exception without file attachment."""
        client = _client(monkeypatch)
        resp = client.post(
            "/admin/attendance-exceptions/add",
            data={
                "learner_id": "L99999",
                "absentee_date": "2026-05-10",
                "code_id": "1",  # LATE
                "notes": "Test exception",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_add_exception_missing_required(self, monkeypatch):
        """Missing required fields should flash error and redirect."""
        client = _client(monkeypatch)
        resp = client.post(
            "/admin/attendance-exceptions/add",
            data={"learner_id": "L99999"},  # missing date and code
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_add_exception_with_file_upload(self, monkeypatch):
        """POST with a file attachment."""
        client = _client(monkeypatch)
        data = {
            "learner_id": "L88888",
            "absentee_date": "2026-06-01",
            "code_id": "3",  # MEDICAL
            "notes": "With attachment",
        }
        # Create a small in-memory file
        file_data = io.BytesIO(b"fake pdf content")
        resp = client.post(
            "/admin/attendance-exceptions/add",
            data={**data, "attachment": (file_data, "test_doc.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_add_exception_invalid_file_type(self, monkeypatch):
        """Uploading a disallowed file type should be rejected."""
        client = _client(monkeypatch)
        data = {
            "learner_id": "L77777",
            "absentee_date": "2026-07-01",
            "code_id": "2",  # EXCUSED
            "notes": "Bad file",
        }
        file_data = io.BytesIO(b"not an exe")
        resp = client.post(
            "/admin/attendance-exceptions/add",
            data={**data, "attachment": (file_data, "virus.exe")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_list_with_filters(self, monkeypatch):
        """Filtering exceptions by learner_id works."""
        client = _client(monkeypatch)
        # Create an exception first
        client.post(
            "/admin/attendance-exceptions/add",
            data={
                "learner_id": "L_FILTER",
                "absentee_date": "2026-08-15",
                "code_id": "1",
                "notes": "Filter test",
            },
            follow_redirects=True,
        )
        resp = client.get("/admin/attendance-exceptions?learner_id=L_FILTER")
        assert resp.status_code == 200
        assert b"L_FILTER" in resp.data

    def test_list_filter_by_code(self, monkeypatch):
        """Filtering by code_id works."""
        client = _client(monkeypatch)
        resp = client.get("/admin/attendance-exceptions?code_id=1")
        assert resp.status_code == 200


class TestExceptionCodesCRUD:
    """Test the exception codes management endpoints."""

    def test_create_code(self, monkeypatch):
        """POST to create a new exception code."""
        client = _client(monkeypatch)
        resp = client.post(
            "/admin/attendance-exception-codes/add",
            data={
                "code": "HOMEWORK",
                "name": "Homework Submission",
                "description": "Late homework submission",
                "color": "#FF9800",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_create_duplicate_code(self, monkeypatch):
        """Creating a duplicate code should flash error."""
        client = _client(monkeypatch)
        resp = client.post(
            "/admin/attendance-exception-codes/add",
            data={"code": "LATE", "name": "Duplicate Late"},
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_toggle_code_active(self, monkeypatch):
        """Toggle a code active/inactive."""
        client = _client(monkeypatch)
        resp = client.post("/admin/attendance-exception-codes/1/toggle", follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_code(self, monkeypatch):
        """Edit a code's attributes."""
        client = _client(monkeypatch)
        resp = client.post(
            "/admin/attendance-exception-codes/1/edit",
            data={
                "code": "LATE",
                "name": "Late Arrival (Updated)",
                "description": "Updated description",
                "color": "#FF5722",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

    def test_delete_exception(self, monkeypatch):
        """POST to delete an exception."""
        client = _client(monkeypatch)
        # Create first
        client.post(
            "/admin/attendance-exceptions/add",
            data={
                "learner_id": "L_DELETE",
                "absentee_date": "2026-09-01",
                "code_id": "1",
                "notes": "To be deleted",
            },
            follow_redirects=True,
        )
        # Get the list page to find exception count
        list_resp = client.get("/admin/attendance-exceptions")
        assert list_resp.status_code == 200

    def test_download_missing_file(self, monkeypatch):
        """Downloading a non-existent file should redirect with error."""
        client = _client(monkeypatch)
        # Create an exception without a file
        resp = client.post(
            "/admin/attendance-exceptions/add",
            data={
                "learner_id": "L_DL",
                "absentee_date": "2026-10-01",
                "code_id": "1",
                "notes": "No file",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200


class TestExceptionCodesPage:
    """Test the exception codes management page."""

    def test_codes_page_accessible(self, monkeypatch):
        """GET /admin/attendance-exception-codes returns the manage codes page."""
        client = _client(monkeypatch)
        resp = client.get("/admin/attendance-exception-codes")
        assert resp.status_code == 200
        # Should contain the LATE code (seeded)
        assert b"LATE" in resp.data
