"""Integration tests for the announcement system."""
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
client = r.app.test_client()

from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text
from datetime import datetime


def ensure():
    with r.app.app_context():
        r.db.drop_all()
        r.db.create_all()
        insp = inspect(r.db.engine)
        cols = [c["name"] for c in insp.get_columns("teacher_announcement")]
        with r.db.engine.connect() as conn:
            if "scope" not in cols:
                conn.execute(text("ALTER TABLE teacher_announcement ADD COLUMN scope VARCHAR(16) DEFAULT 'teacher'"))
            if "priority" not in cols:
                conn.execute(text("ALTER TABLE teacher_announcement ADD COLUMN priority VARCHAR(16) DEFAULT 'normal'"))
            if "expires_at" not in cols:
                conn.execute(text("ALTER TABLE teacher_announcement ADD COLUMN expires_at DATETIME"))
            if "updated_at" not in cols:
                conn.execute(text("ALTER TABLE teacher_announcement ADD COLUMN updated_at DATETIME"))
            conn.commit()


def _seed():
    with r.app.app_context():
        u_admin = r.User(username="admin", password_hash=generate_password_hash("admin"),
                         learner_id="ADMIN", first_login=False)
        u_teacher = r.User(username="mr_smith", password_hash=generate_password_hash("pass"),
                           is_teacher=True, can_teacher_announcements=True, first_login=False, educator_id="ED-001")
        r.db.session.add_all([u_admin, u_teacher])
        r.db.session.commit()


def _login_as(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    return resp.status_code in (200, 302)


def _reset():
    """Full reset: clear client session, rebuild DB."""
    with client.session_transaction() as sess:
        sess.clear()
    ensure()
    _seed()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_teacher_create_announcement():
    _reset()
    assert _login_as("mr_smith", "pass")
    resp = client.post(
        "/api/teacher/announcements/save",
        data={
            "title": "Teacher Test",
            "body": "Body",
            "scope": "teacher",
            "priority": "high",
        },
    )
    data = resp.get_json()
    print(f"  ✓ Create: {resp.status_code} {data}")
    assert resp.status_code == 200
    assert data.get("success") is True


def test_teacher_list():
    _reset()
    assert _login_as("mr_smith", "pass")
    client.post("/api/teacher/announcements/save",
                data={"title": "First", "body": "B", "scope": "teacher", "priority": "high"})
    resp = client.get("/api/teacher/announcements")
    data = resp.get_json()
    rows = data.get("rows", [])
    assert resp.status_code == 200
    assert len(rows) >= 1
    assert rows[0]["title"] == "First"
    assert rows[0]["priority"] == "high"
    assert rows[0]["scope"] == "teacher"
    print(f"  ✓ List: {len(rows)} items")


def test_school_wide_api():
    _reset()
    assert _login_as("mr_smith", "pass")
    client.post("/api/teacher/announcements/save",
                data={"title": "Holiday", "body": "Closed", "scope": "school", "priority": "urgent"})
    resp = client.get("/api/announcements")
    data = resp.get_json()
    assert resp.status_code == 200
    rows = data if isinstance(data, list) else data.get("rows", data.get("announcements", []))
    titles = [a["title"] for a in rows]
    assert "Holiday" in titles, f"Not found in: {titles}"
    print(f"  ✓ School-wide API: {len(rows)} items")


def test_noticeboard_page_renders():
    _reset()
    assert _login_as("mr_smith", "pass")
    resp = client.get("/announcements")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "School Announcements" in html
    print(f"  ✓ Noticeboard page: 200")


def test_teacher_page_renders():
    _reset()
    assert _login_as("mr_smith", "pass")
    resp = client.get("/teacher/announcements")
    assert resp.status_code == 200
    print(f"  ✓ Teacher page: 200")


def test_admin_page_renders():
    _reset()
    assert _login_as("admin", "admin")
    resp = client.get("/admin/announcements")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Manage Announcements" in html
    print(f"  ✓ Admin page: 200")

    resp = client.post("/admin/announcements/create", data={
        "title": "Admin via Form",
        "body": "Content",
        "scope": "school",
        "priority": "low",
    }, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Admin via Form" in html
    print(f"  ✓ Admin create via form: 200")


def test_admin_create_via_api():
    _reset()
    assert _login_as("admin", "admin")
    resp = client.post("/api/announcements/create", data={
        "title": "Admin via API",
        "body": "Content",
        "scope": "school",
        "priority": "low",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert data.get("success") is True
    print(f"  ✓ Admin create via API: {data}")


if __name__ == "__main__":
    print("Announcement Tests:")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                print(f"  ✗ {name}: FAIL — {e}")
                raise
    print("\n✅ All announcement tests passed!")
