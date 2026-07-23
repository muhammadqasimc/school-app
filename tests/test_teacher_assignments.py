"""Integration tests for the teacher assignment posting feature."""
import json
import sys
import os

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


def ensure():
    """Ensure DB tables exist (create if needed)."""
    with r.app.app_context():
        r.db.drop_all()
        r.db.create_all()
        insp = inspect(r.db.engine)
        cols = [c["name"] for c in insp.get_columns("teacher_assignment")]
        # Add any missing columns if they weren't created fresh
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


def _seed():
    """Seed test users."""
    with r.app.app_context():
        u_admin = r.User(username="admin", password_hash=generate_password_hash("admin"),
                         learner_id="ADMIN", first_login=False)
        u_teacher = r.User(username="mr_smith", password_hash=generate_password_hash("pass"),
                           is_teacher=True, first_login=False, educator_id="ED-001")
        u_teacher2 = r.User(username="ms_jones", password_hash=generate_password_hash("pass"),
                            is_teacher=True, first_login=False, educator_id="ED-002")
        r.db.session.add_all([u_admin, u_teacher, u_teacher2])
        r.db.session.commit()
        return {
            "admin_id": u_admin.id,
            "teacher_id": u_teacher.id,
            "teacher2_id": u_teacher2.id,
        }


def _reset():
    """Full reset: clear client session, rebuild DB."""
    with client.session_transaction() as sess:
        sess.clear()
    ensure()
    return _seed()


def _login_as(username, password):
    """Login helper."""
    resp = client.post("/login", data={"username": username, "password": password})
    return resp.status_code in (200, 302)


def _inject_session(user_id):
    """Directly inject user ID into session for tests."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["portal_mode"] = "teacher"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_model_creation():
    """Test that the TeacherAssignment model can be created and persisted."""
    users = _reset()
    with r.app.app_context():
        # Re-fetch user within context to avoid detached instance error
        teacher = r.User.query.get(users["teacher_id"])
        assignment = r.TeacherAssignment(
            user_id=teacher.id,
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
        r.db.session.add(assignment)
        r.db.session.commit()
        assert assignment.id is not None
        assert assignment.title == "Math Homework"
        assert assignment.assignment_type == "homework"
        assert assignment.is_active is True
        assert assignment.created_at is not None

        # Test to_dict
        d = assignment.to_dict()
        assert d["id"] == assignment.id
        assert d["title"] == "Math Homework"
        assert d["assignmentType"] == "homework"
        assert len(d["fileAttachments"]) == 1
        assert d["fileAttachments"][0]["original_name"] == "hw.pdf"
        assert len(d["links"]) == 1
        assert d["links"][0]["url"] == "https://example.com"
    print("  ✓ Model creation")


def test_page_renders():
    """Test that the teacher assignments page renders."""
    users = _reset()
    _inject_session(users["teacher_id"])
    resp = client.get("/teacher/assignments")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Assignments" in html
    print("  ✓ Page renders")


def test_page_requires_teacher():
    """Test that non-teachers get a redirect or 403 on the assignments page."""
    users = _reset()
    # Login as admin (not teacher)
    assert _login_as("admin", "admin")
    resp = client.get("/teacher/assignments")
    assert resp.status_code in (302, 403)
    print("  ✓ Page blocks non-teachers")


def test_api_list_empty():
    """Test that the list API returns an empty array for a teacher with no assignments."""
    users = _reset()
    _inject_session(users["teacher_id"])
    resp = client.get("/api/teacher/assignments")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []
    print("  ✓ Empty list")


def test_api_create():
    """Test creating an assignment via API."""
    users = _reset()
    _inject_session(users["teacher_id"])
    resp = client.post(
        "/api/teacher/assignments/save",
        data={
            "title": "Science Assignment",
            "description": "Write a report on ecosystems",
            "assignment_type": "assignment",
            "target_grade": "8",
            "target_class": "B",
            "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "links": json.dumps([
                {"url": "https://example.com/eco", "title": "Ecosystem Guide"}
            ]),
        },
    )
    assert resp.status_code == 200, f"Response: {resp.get_json()}"
    data = resp.get_json()
    assert data["success"] is True
    assert data["id"] is not None
    print("  ✓ Create assignment")


def test_api_create_requires_title():
    """Test that creating an assignment without a title returns 400."""
    users = _reset()
    _inject_session(users["teacher_id"])
    resp = client.post(
        "/api/teacher/assignments/save",
        data={"title": "", "description": "No title"},
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    print("  ✓ Title validation")


def test_api_list_with_data():
    """Test that the list API returns created assignments."""
    users = _reset()
    _inject_session(users["teacher_id"])
    # Create two assignments
    client.post("/api/teacher/assignments/save", data={
        "title": "Assignment 1", "description": "First"
    })
    client.post("/api/teacher/assignments/save", data={
        "title": "Assignment 2", "description": "Second",
        "assignment_type": "homework",
    })
    resp = client.get("/api/teacher/assignments")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert data[0]["title"] == "Assignment 2"
    assert data[0]["assignmentType"] == "homework"
    assert data[1]["title"] == "Assignment 1"
    print("  ✓ List assignments")


def test_api_update():
    """Test updating an existing assignment."""
    users = _reset()
    _inject_session(users["teacher_id"])
    # Create
    create_resp = client.post("/api/teacher/assignments/save", data={
        "title": "Original Title", "description": "Original description"
    })
    aid = create_resp.get_json()["id"]
    # Update
    update_resp = client.post("/api/teacher/assignments/save", data={
        "id": str(aid),
        "title": "Updated Title",
        "description": "Updated description",
        "assignment_type": "activity",
    })
    assert update_resp.status_code == 200
    data = update_resp.get_json()
    assert data["success"] is True
    # Verify via list
    resp = client.get("/api/teacher/assignments")
    assert resp.status_code == 200
    items = resp.get_json()
    updated = next(a for a in items if a["id"] == aid)
    assert updated["title"] == "Updated Title"
    assert updated["assignmentType"] == "activity"
    print("  ✓ Update assignment")


def test_api_delete():
    """Test soft-deleting an assignment."""
    users = _reset()
    _inject_session(users["teacher_id"])
    # Create
    create_resp = client.post("/api/teacher/assignments/save", data={
        "title": "To Delete"
    })
    aid = create_resp.get_json()["id"]
    # Delete
    delete_resp = client.post(f"/api/teacher/assignments/{aid}/delete")
    assert delete_resp.status_code == 200
    assert delete_resp.get_json()["success"] is True
    # Verify soft-deleted (still in list but isActive=False)
    resp = client.get("/api/teacher/assignments")
    items = resp.get_json()
    deleted = next(a for a in items if a["id"] == aid)
    assert deleted["isActive"] is False
    print("  ✓ Delete assignment")


def test_api_other_teacher_cannot_modify():
    """Test that a teacher cannot modify another teacher's assignment."""
    users = _reset()
    _inject_session(users["teacher_id"])
    # Teacher 1 creates
    create_resp = client.post("/api/teacher/assignments/save", data={
        "title": "Teacher 1 Assignment"
    })
    aid = create_resp.get_json()["id"]
    # Teacher 2 tries to update
    _inject_session(users["teacher2_id"])
    update_resp = client.post("/api/teacher/assignments/save", data={
        "id": str(aid),
        "title": "Hacked Title",
    })
    assert update_resp.status_code == 404
    # Teacher 2 tries to delete
    delete_resp = client.post(f"/api/teacher/assignments/{aid}/delete")
    assert delete_resp.status_code == 403
    print("  ✓ Teacher isolation")


def test_api_file_upload():
    """Test that file uploads work with assignment creation."""
    users = _reset()
    _inject_session(users["teacher_id"])
    data = {
        "title": "With Files",
        "description": "Assignment with file attachments",
    }
    # Create a mock file
    file_data = (BytesIO(b"fake pdf content"), "report.pdf")
    resp = client.post(
        "/api/teacher/assignments/save",
        data={**data, "files": file_data},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True
    # Verify file attachment is stored
    list_resp = client.get("/api/teacher/assignments")
    items = list_resp.get_json()
    created = next(a for a in items if a["title"] == "With Files")
    assert len(created["fileAttachments"]) == 1
    assert created["fileAttachments"][0]["original_name"] == "report.pdf"
    print("  ✓ File upload")


def test_api_requires_auth():
    """Test that unauthenticated requests are blocked."""
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/api/teacher/assignments")
    # Should be redirected to login or return 401/403
    assert resp.status_code in (302, 401, 403)
    print("  ✓ Auth guard")


if __name__ == "__main__":
    print("Teacher Assignment Tests:")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                print(f"  ✗ {name}: FAIL — {e}")
                raise
    print("\n✅ All teacher assignment tests passed!")
