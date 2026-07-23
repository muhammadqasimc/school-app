"""Integration tests for the parent portal assignments feature."""
import json
import sys
import os
from unittest.mock import patch

os.environ["FLASK_ENV"] = "testing"
os.environ["TESTING"] = "1"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin"
os.environ["RATELIMIT_ENABLED"] = "false"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as r
r.limiter.enabled = False

r.app.config["SECRET_KEY"] = "test"
r.app.config["WTF_CSRF_ENABLED"] = False
r.app.config["SERVER_NAME"] = "localhost"
client = r.app.test_client()

from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text
from io import BytesIO
from datetime import datetime, timedelta


# Mock learner info for test learner L001 (Grade 10)
FAKE_LEARNER_INFO = {
    "id": "1",
    "learner_id": "L001",
    "name": "Test",
    "surname": "Student",
    "grade": "10",
}


def ensure():
    """Ensure DB tables exist (create if needed)."""
    with r.app.app_context():
        r.db.drop_all()
        r.db.create_all()
        insp = inspect(r.db.engine)
        cols = [c["name"] for c in insp.get_columns("teacher_assignment")]
        needed = ["id", "user_id", "title", "description", "assignment_type",
                  "target_grade", "target_class", "due_date", "file_attachments",
                  "links", "is_active", "created_at", "updated_at"]
        existing = set(cols)
        with r.db.engine.connect() as conn:
            for col in needed:
                if col not in existing:
                    col_type = {
                        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                        "user_id": "INTEGER NOT NULL",
                        "title": "VARCHAR(200) NOT NULL",
                        "description": "TEXT",
                        "assignment_type": "VARCHAR(32) DEFAULT 'assignment'",
                        "target_grade": "VARCHAR(32)",
                        "target_class": "VARCHAR(64)",
                        "due_date": "DATETIME",
                        "file_attachments": "TEXT",
                        "links": "TEXT",
                        "is_active": "BOOLEAN DEFAULT 1",
                        "created_at": "DATETIME",
                        "updated_at": "DATETIME",
                    }
                    try:
                        conn.execute(text(
                            f"ALTER TABLE teacher_assignment ADD COLUMN {col} {col_type[col]}"
                        ))
                    except Exception:
                        pass
            conn.commit()

        # Also ensure UserLearner table exists for parent-child linking
        if "user_learner" not in [t.name for t in r.db.metadata.sorted_tables]:
            try:
                conn.execute(text(
                    "CREATE TABLE IF NOT EXISTS user_learner "
                    "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "user_id INTEGER NOT NULL, "
                    "learner_id VARCHAR(50) NOT NULL)"
                ))
                conn.commit()
            except Exception:
                pass


def _seed():
    """Seed test users and assignments."""
    with r.app.app_context():
        u_admin = r.User(username="admin", password_hash=generate_password_hash("admin"),
                         learner_id="ADMIN", first_login=False)
        u_teacher = r.User(username="mr_smith", password_hash=generate_password_hash("pass"),
                           is_teacher=True, first_login=False, educator_id="ED-001")
        u_parent = r.User(username="parent1", password_hash=generate_password_hash("pass"),
                          first_login=False)
        r.db.session.add_all([u_admin, u_teacher, u_parent])
        r.db.session.commit()

        # Create UserLearner link: parent -> learner "L001" (Grade 10)
        from sqlalchemy import Table, MetaData
        meta = MetaData()
        try:
            ul_table = Table("user_learner", meta, autoload_with=r.db.engine)
            r.db.session.execute(
                ul_table.insert().values(user_id=u_parent.id, learner_id="L001")
            )
        except Exception:
            # Table might not exist, try raw SQL
            try:
                r.db.session.execute(
                    text("INSERT INTO user_learner (user_id, learner_id) VALUES (:uid, :lid)"),
                    {"uid": u_parent.id, "lid": "L001"}
                )
            except Exception:
                pass
        r.db.session.commit()

        # Create a child link for admin as well (so tests can use admin too)
        try:
            r.db.session.execute(
                ul_table.insert().values(user_id=u_admin.id, learner_id="L001")
            )
        except Exception:
            try:
                r.db.session.execute(
                    text("INSERT INTO user_learner (user_id, learner_id) VALUES (:uid, :lid)"),
                    {"uid": u_admin.id, "lid": "L001"}
                )
            except Exception:
                pass
        r.db.session.commit()

        # Create assignments by the teacher
        # Assignment targeting Grade 10 (matches L001 which is Grade 10)
        a1 = r.TeacherAssignment(
            user_id=u_teacher.id,
            title="Math Homework",
            description="Complete exercises 1-10",
            assignment_type="homework",
            target_grade="10",
            target_class="A",
            due_date=datetime.utcnow() + timedelta(days=7),
            file_attachments=json.dumps([
                {"original_name": "hw.pdf", "stored_name": "abc.pdf",
                 "mime_type": "application/pdf", "size_bytes": 1024,
                 "storage_relpath": "uploads/assignments/abc.pdf"}
            ]),
            links=json.dumps([
                {"url": "https://example.com", "title": "Reference"}
            ]),
        )
        # Assignment targeting Grade 8 (different grade, should not match)
        a2 = r.TeacherAssignment(
            user_id=u_teacher.id,
            title="Science Project",
            description="Build a volcano",
            assignment_type="assignment",
            target_grade="8",
            target_class="B",
            due_date=datetime.utcnow() + timedelta(days=14),
        )
        # Assignment with no specific grade (all grades) - should match
        a3 = r.TeacherAssignment(
            user_id=u_teacher.id,
            title="All-Grades Activity",
            description="Read the school newsletter",
            assignment_type="activity",
            target_grade=None,
            due_date=datetime.utcnow() + timedelta(days=3),
        )
        # Inactive assignment - should NOT match
        a4 = r.TeacherAssignment(
            user_id=u_teacher.id,
            title="Old Assignment",
            description="Inactive",
            assignment_type="assignment",
            target_grade="10",
            is_active=False,
        )
        r.db.session.add_all([a1, a2, a3, a4])
        r.db.session.commit()

        return {
            "teacher_id": u_teacher.id,
            "parent_id": u_parent.id,
            "admin_id": u_admin.id,
            "assignment1_id": a1.id,
            "assignment2_id": a2.id,
            "assignment3_id": a3.id,
            "assignment4_id": a4.id,
        }


def _reset():
    """Full reset: clear client session, rebuild DB."""
    with client.session_transaction() as sess:
        sess.clear()
    ensure()
    return _seed()


def _inject_session(user_id, learner_id="L001"):
    """Directly inject user ID and active learner into session."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["active_learner_id"] = learner_id
        sess["portal_mode"] = "parent"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@patch('app.fetch_learner_info_by_id')
def test_parent_assignments_returns_matching_grade(mock_fetch):
    """Test that the API returns assignments matching the learner's grade."""
    mock_fetch.return_value = FAKE_LEARNER_INFO
    users = _reset()
    _inject_session(users["parent_id"])
    resp = client.get("/api/parent/assignments")
    assert resp.status_code == 200
    data = resp.get_json()
    # Should return a1 (grade 10) and a3 (no grade), but not a2 (grade 8) or a4 (inactive)
    titles = [a["title"] for a in data]
    assert "Math Homework" in titles, f"Expected 'Math Homework' in {titles}"
    assert "All-Grades Activity" in titles, f"Expected 'All-Grades Activity' in {titles}"
    assert "Science Project" not in titles, f"'Science Project' should not be in {titles}"
    assert "Old Assignment" not in titles, f"'Old Assignment' should not be in {titles}"
    print("  ✓ Returns matching grade assignments")


def test_parent_assignments_empty_for_unlinked():
    """Test that the API returns empty list when no learner is linked."""
    users = _reset()
    # No active_learner_id in session
    with client.session_transaction() as sess:
        sess["_user_id"] = str(users["parent_id"])
        sess["_fresh"] = True
        sess["portal_mode"] = "parent"
        # Don't set active_learner_id
        if "active_learner_id" in sess:
            del sess["active_learner_id"]
    resp = client.get("/api/parent/assignments")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == [], f"Expected empty list, got {data}"
    print("  ✓ Empty list for unlinked learner")


@patch('app.fetch_learner_info_by_id')
def test_parent_assignments_file_download_urls(mock_fetch):
    """Test that file download URLs are included in the response."""
    mock_fetch.return_value = FAKE_LEARNER_INFO
    users = _reset()
    _inject_session(users["parent_id"])
    resp = client.get("/api/parent/assignments")
    assert resp.status_code == 200
    data = resp.get_json()
    # Find Math Homework which has a file attachment
    math_hw = next((a for a in data if a["title"] == "Math Homework"), None)
    assert math_hw is not None, "Math Homework not found"
    assert "fileDownloadUrls" in math_hw, "Missing fileDownloadUrls"
    assert len(math_hw["fileDownloadUrls"]) == 1
    dl_url = math_hw["fileDownloadUrls"][0]
    assert "/api/parent/assignments/" in dl_url
    assert "/files/0" in dl_url
    print("  ✓ File download URLs included")


@patch('app.fetch_learner_info_by_id')
def test_parent_assignments_file_download(mock_fetch):
    """Test that the file download endpoint works (404 because file doesn't exist)."""
    mock_fetch.return_value = FAKE_LEARNER_INFO
    users = _reset()
    _inject_session(users["parent_id"])
    aid = users["assignment1_id"]
    # The actual file doesn't exist on disk, so we expect 404
    resp = client.get(f"/api/parent/assignments/{aid}/files/0")
    # The file won't exist, expect 404
    assert resp.status_code == 404
    print("  ✓ File download returns 404 for missing file")


@patch('app.fetch_learner_info_by_id')
def test_parent_assignments_file_download_no_file(mock_fetch):
    """Test download endpoint for assignment with no attachments."""
    mock_fetch.return_value = FAKE_LEARNER_INFO
    users = _reset()
    _inject_session(users["parent_id"])
    aid = users["assignment3_id"]
    resp = client.get(f"/api/parent/assignments/{aid}/files/0")
    assert resp.status_code == 404
    print("  ✓ File download 404 for no attachments")


@patch('app.fetch_learner_info_by_id')
def test_parent_assignments_invalid_index(mock_fetch):
    """Test download with invalid file index."""
    mock_fetch.return_value = FAKE_LEARNER_INFO
    users = _reset()
    _inject_session(users["parent_id"])
    aid = users["assignment1_id"]
    resp = client.get(f"/api/parent/assignments/{aid}/files/99")
    assert resp.status_code == 404
    print("  ✓ File download 404 for invalid index")


def test_parent_assignments_requires_auth():
    """Test that unauthenticated requests are blocked."""
    _reset()  # Clean state
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/api/parent/assignments")
    assert resp.status_code in (302, 401, 403)
    print("  ✓ Auth guard for list")

    # Also test for download
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/api/parent/assignments/1/files/0")
    assert resp.status_code in (302, 401, 403)
    print("  ✓ Auth guard for download")


if __name__ == "__main__":
    print("Parent Assignment Tests:")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                print(f"  ✗ {name}: FAIL — {e}")
                raise
    print("\n✅ All parent assignment tests passed!")
