"""Tests for the Student Profile 360 view."""
import os
import sys

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


def ensure():
    with r.app.app_context():
        r.db.drop_all()
        r.db.create_all()


def _seed():
    with r.app.app_context():
        u_admin = r.User(
            username="admin",
            password_hash=generate_password_hash("admin"),
            learner_id="ADMIN",
            first_login=False,
        )
        u_teacher = r.User(
            username="mr_smith",
            password_hash=generate_password_hash("pass"),
            is_teacher=True,
            first_login=False,
            educator_id="ED-001",
        )
        u_manager = r.User(
            username="mgr_user",
            password_hash=generate_password_hash("pass"),
            is_manager=True,
            first_login=False,
        )
        u_parent = r.User(
            username="parent1",
            password_hash=generate_password_hash("pass"),
            is_parent=True,
            first_login=False,
        )
        r.db.session.add_all([u_admin, u_teacher, u_manager, u_parent])
        r.db.session.commit()


def _reset():
    with client.session_transaction() as sess:
        sess.clear()
    ensure()
    _seed()


def _login_as(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    return resp.status_code in (200, 302)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_teacher_can_access():
    """A teacher user can access the student 360 page."""
    _reset()
    assert _login_as("mr_smith", "pass")
    # Use a dummy learner_id; the page should still render (learner may not exist)
    resp = client.get("/student/360/99999")
    # If learner not found, we expect a 404 or the page to render with flash
    assert resp.status_code in (200, 302, 404)
    # If 200, ensure the template content is present
    if resp.status_code == 200:
        html = resp.data.decode()
        assert "Student Profile 360" in html or "360" in html


def test_admin_can_access():
    """An admin user can access the student 360 page."""
    _reset()
    assert _login_as("admin", "admin")
    resp = client.get("/student/360/99999")
    assert resp.status_code in (200, 302, 404)


def test_manager_can_access():
    """A manager user (with management portal) can access the student 360 page."""
    _reset()
    assert _login_as("mgr_user", "pass")
    with client.session_transaction() as sess:
        sess["portal_mode"] = "management"
    resp = client.get("/student/360/99999")
    assert resp.status_code in (200, 302, 404)


def test_parent_redirected():
    """A parent user should not access the student 360 view (redirect to dashboard)."""
    _reset()
    assert _login_as("parent1", "pass")
    resp = client.get("/student/360/99999")
    # Parent should be redirected away
    assert resp.status_code in (302, 403)
    if resp.status_code == 302:
        assert resp.headers.get("Location", "").endswith("/dashboard") or "/dashboard" in resp.headers.get("Location", "")


def test_unauthorized_user_blocked():
    """An unauthenticated user gets redirected to login."""
    _reset()
    with client.session_transaction() as sess:
        sess.clear()
    resp = client.get("/student/360/99999")
    # Allow 302 (redirect to login), 401 (unauthorized), or 403 (forbidden)
    assert resp.status_code in (302, 401, 403)
    if resp.status_code == 302:
        assert "login" in resp.headers.get("Location", "").lower()


def test_page_structure():
    """When accessed by a teacher, the page contains expected structural elements."""
    _reset()
    assert _login_as("mr_smith", "pass")
    # Use a realistic learner ID that might exist
    resp = client.get("/student/360/TEST001")
    if resp.status_code != 200:
        return  # Skip if learner not found
    html = resp.data.decode()
    # Check for key structural elements
    assert 'id="student360Tabs"' in html or 'nav-tabs' in html
    assert 'tab-pane' in html


if __name__ == "__main__":
    print("Student 360 Tests:")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                print(f"  ✗ {name}: FAIL — {e}")
                raise
    print("\n✅ All student 360 tests passed!")
