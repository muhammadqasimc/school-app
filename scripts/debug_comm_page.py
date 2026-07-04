import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app as m


def main():
    flask_app = m.app
    with flask_app.app_context():
        admin = m.User.query.filter_by(username="admin").first()
        if not admin:
            print("NO_ADMIN")
            return
        client = flask_app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True

        resp = client.get("/admin/communication")
        html = resp.get_data(as_text=True)
        print("STATUS", resp.status_code)
        start = html.find('id="filterGrade"')
        print("HAS_FILTER", start >= 0)
        if start >= 0:
            snippet = html[start:start + 1200]
            print(snippet)
        print("OPTION_COUNT", html.count("<option value="))


if __name__ == "__main__":
    main()
