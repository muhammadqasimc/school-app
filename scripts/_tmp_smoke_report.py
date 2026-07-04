import os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))
import app as app_mod
app = app_mod.app
app.config["TESTING"] = True
CANDIDATES = [
    ("/api/management-achievement-promotion-analysis?year=2026&term=1", lambda j: (j or {}).get("rows"), "rows"),
    ("/api/management-mark-schedules/filters?year=2026", lambda j: (j or {}).get("cycles") or (j or {}).get("grades") or j, "filters"),
    ("/api/management-report-filters?year=2026&term=1", lambda j: (j or {}).get("filters"), "filters"),
]
path, extract, label = random.choice(CANDIDATES)
with app.app_context():
    user = app_mod.User.query.filter_by(username=app_mod.ADMIN_USERNAME).first() or app_mod.User.query.filter_by(is_manager=True).first() or app_mod.User.query.first()
    if not user:
        print("No User"); sys.exit(2)
    print("Management access:", app_mod._management_user_can_access_reports(user))
    c = app.test_client()
    with c.session_transaction() as sess:
        sess["_user_id"] = str(user.id); sess["_fresh"] = True
    resp = c.get(path)
print("Route:", path)
print("User:", user.id, getattr(user,"username",None))
print("HTTP:", resp.status_code)
if resp.status_code != 200:
    print(resp.get_data(as_text=True)[:2000]); sys.exit(1)
body = resp.get_json()
chunk = extract(body)
print("Field:", label)
if isinstance(chunk, list):
    print("len:", len(chunk))
    if chunk: print("first keys:", list(chunk[0].keys())[:15] if isinstance(chunk[0], dict) else chunk[0])
elif isinstance(chunk, dict):
    print("keys:", list(chunk.keys())[:20])
else:
    print("chunk:", chunk)
