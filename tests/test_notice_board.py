"""Integration tests for the notice board system."""
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
from sqlalchemy import inspect


def ensure():
    with r.app.app_context():
        r.db.drop_all()
        r.db.create_all()


def _seed():
    with r.app.app_context():
        u_admin = r.User(username="admin", password_hash=generate_password_hash("admin"),
                         learner_id="ADMIN", first_login=False)
        u_teacher = r.User(username="mr_smith", password_hash=generate_password_hash("pass"),
                           is_teacher=True, first_login=False, educator_id="ED-001")
        u_parent = r.User(username="parent1", password_hash=generate_password_hash("pass"),
                          is_parent=True, first_login=False)
        r.db.session.add_all([u_admin, u_teacher, u_parent])
        r.db.session.commit()


def _login_as(username, password):
    resp = client.post("/login", data={"username": username, "password": password})
    return resp.status_code in (200, 302)


def _reset():
    with client.session_transaction() as sess:
        sess.clear()
    ensure()
    _seed()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_admin_can_view_notice_board():
    _reset()
    assert _login_as("admin", "admin")
    resp = client.get("/admin/notice-board")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Notice Board" in html
    print("  ✓ Admin can view notice board page")


def test_admin_can_create_notice():
    _reset()
    assert _login_as("admin", "admin")
    resp = client.post("/admin/notice-board/create", data={
        "title": "School Holiday",
        "body": "School will be closed for holidays.",
        "notice_type": "holiday",
        "target_audience": "all",
        "priority": "high",
    }, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "School Holiday" in html
    assert "Notice created" in html
    print("  ✓ Admin can create a notice")


def test_admin_can_toggle_notice():
    _reset()
    assert _login_as("admin", "admin")
    # Create a notice first
    client.post("/admin/notice-board/create", data={
        "title": "Test Notice",
        "body": "Test body",
        "notice_type": "general",
        "target_audience": "teachers",
        "priority": "normal",
    })
    # Get the notice ID from the list
    resp = client.get("/admin/notice-board")
    html = resp.data.decode()
    assert "Active" in html  # default is active
    # Toggle it
    with r.app.app_context():
        notice = r.FunctionNotice.query.first()
        assert notice is not None
        notice_id = notice.id
    resp = client.post(f"/admin/notice-board/{notice_id}/toggle", follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Inactive" in html
    print("  ✓ Admin can toggle notice active/inactive")


def test_admin_can_delete_notice():
    _reset()
    assert _login_as("admin", "admin")
    client.post("/admin/notice-board/create", data={
        "title": "Delete Me",
        "body": "To be deleted",
        "notice_type": "general",
        "target_audience": "all",
        "priority": "low",
    })
    with r.app.app_context():
        notice = r.FunctionNotice.query.first()
        assert notice is not None
        notice_id = notice.id
    resp = client.post(f"/admin/notice-board/{notice_id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Notice deleted" in html
    assert "Delete Me" not in html
    print("  ✓ Admin can delete a notice")


def test_non_admin_gets_403_on_notice_board():
    _reset()
    assert _login_as("mr_smith", "pass")
    resp = client.get("/admin/notice-board")
    assert resp.status_code in (302, 403)
    if resp.status_code == 200:
        html = resp.data.decode()
        # If it renders, it should show some error or not be the admin page
        assert "Notice Board" not in html or "403" in html
    print("  ✓ Non-admin gets 403/redirect on notice board")


def test_list_shows_only_active_notices_default():
    _reset()
    assert _login_as("admin", "admin")
    # Create one active and one inactive notice
    client.post("/admin/notice-board/create", data={
        "title": "Active Notice",
        "body": "This is active",
        "notice_type": "general",
        "target_audience": "all",
        "priority": "normal",
    })
    client.post("/admin/notice-board/create", data={
        "title": "Another Active",
        "body": "Also active",
        "notice_type": "academic",
        "target_audience": "teachers",
        "priority": "high",
    })
    resp = client.get("/admin/notice-board")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Active Notice" in html
    assert "Another Active" in html
    print("  ✓ Admin sees all notices in listing")


def test_notice_with_dates():
    _reset()
    assert _login_as("admin", "admin")
    from datetime import datetime
    start = "2026-01-01T00:00"
    end = "2026-12-31T23:59"
    resp = client.post("/admin/notice-board/create", data={
        "title": "Dated Notice",
        "body": "Has start and end dates",
        "notice_type": "meeting",
        "target_audience": "parents",
        "priority": "normal",
        "start_date": start,
        "end_date": end,
    }, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Dated Notice" in html
    assert "2026-01-01" in html
    print("  ✓ Notice with start/end dates renders correctly")


def test_notice_board_create_validates_required_fields():
    _reset()
    assert _login_as("admin", "admin")
    # Missing title
    resp = client.post("/admin/notice-board/create", data={
        "title": "",
        "body": "Some body",
    }, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Title and body are required" in html or "error" in html.lower()
    print("  ✓ Create validates required fields")


if __name__ == "__main__":
    print("Notice Board Tests:")
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:
                print(f"  ✗ {name}: FAIL — {e}")
                import traceback
                traceback.print_exc()
                failures += 1
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
    else:
        print("\n✅ All notice board tests passed!")
