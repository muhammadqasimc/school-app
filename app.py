import warnings

# Requests emits RequestsDependencyWarning during import when urllib3/chardet skew is detected.
# Apply before any package that transitively imports `requests` (e.g. Flask extensions).
warnings.filterwarnings(
    "ignore",
    message=r".*urllib3.*doesn't match a supported version.*",
    category=Warning,
)

from flask import Flask, Response, render_template, request, redirect, url_for, flash, session, jsonify, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text, inspect
import secrets
import os
import re
import string
import logging
import json
import threading
import time
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from collections import defaultdict, Counter
from dotenv import load_dotenv
import base64
import requests
from io import BytesIO

load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'), override=True)

from mdb_repo import MDBRepository, expand_legacy_row_key_aliases
import management_report_handlers as mrh

# Validate required environment variables at startup (production only)
if os.environ.get('FLASK_ENV') == 'production':
    required_env_vars = ['ADMIN_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
# Use SQLite for app data (users, auth, messages, etc.)
# School data comes directly from the MDB file via MDBRepository
_db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dashboard.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{_db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MDB_FILE_PATH'] = os.environ.get('MDB_FILE_PATH', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'KISMET_JUNE_2026.mdb'))
app.config['MDB_PASSWORD'] = os.environ.get('MDB_PASSWORD', '').strip() or None
app.config['SYNC_INTERVAL_SECONDS'] = int(os.environ.get('SYNC_INTERVAL_SECONDS', '120'))
app.config['ENABLE_SYNC_THREAD'] = os.environ.get('ENABLE_SYNC_THREAD', 'false').strip().lower() in {'1', 'true', 'yes', 'on'}
app.config['POSTGRES_MDB_COMPAT_MODE'] = True
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'slideshow')
app.config['PROFILE_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'profiles')
app.config['DISCIPLINARY_IMAGE_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'disciplinary', 'images')
app.config['DISCIPLINARY_PDF_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'disciplinary', 'pdfs')
app.config['DETENTION_PDF_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'detention')
app.config['CHAT_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'chat')
app.config['SICK_NOTE_UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'sick_notes')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
# Only send session cookie over HTTPS in production
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
# WhatsApp Web service (whatsapp-web.js) - primary OTP channel; SMS used as fallback
app.config['WHATSAPP_SERVICE_URL'] = os.environ.get('WHATSAPP_SERVICE_URL', 'http://127.0.0.1:3001').rstrip('/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
CHAT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}
SICK_NOTE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf'}
SICK_NOTE_MAX_BYTES = 6 * 1024 * 1024  # 6 MiB
CHAT_MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024

# Lightweight in-process cache for expensive management endpoints.
# Keep TTL very short so UI feels instant while staying near-real-time.
_MGMT_CACHE = {}
_MGMT_CACHE_TTL_SECONDS = 8
_FINANCE_CACHE = {}
_FINANCE_CACHE_TTL_SECONDS = 45


def _mgmt_cache_get(key):
    entry = _MGMT_CACHE.get(key)
    if not entry:
        return None
    expires_at = entry.get('expires_at')
    if not expires_at or datetime.now() > expires_at:
        _MGMT_CACHE.pop(key, None)
        return None
    return entry.get('payload')


def _mgmt_cache_set(key, payload, ttl_seconds=_MGMT_CACHE_TTL_SECONDS):
    _MGMT_CACHE[key] = {
        'expires_at': datetime.now() + timedelta(seconds=int(ttl_seconds)),
        'payload': payload,
    }


def _finance_cache_get(key):
    entry = _FINANCE_CACHE.get(key)
    if not entry:
        return None
    expires_at = entry.get("expires_at")
    if not expires_at or datetime.now() > expires_at:
        _FINANCE_CACHE.pop(key, None)
        return None
    return entry.get("payload")


def _finance_cache_set(key, payload, ttl_seconds=_FINANCE_CACHE_TTL_SECONDS):
    _FINANCE_CACHE[key] = {
        "expires_at": datetime.now() + timedelta(seconds=int(ttl_seconds)),
        "payload": payload,
    }


def _pg_compat_sql_debug_enabled() -> bool:
    """Set PG_COMPAT_SQL_DEBUG=1 to log failed EMS→PostgreSQL probe queries (noisy)."""
    return os.environ.get("PG_COMPAT_SQL_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _log_pg_compat_failure(where: str, exc: Exception, sql: str | None = None) -> None:
    msg = str(exc or "").strip()
    short = (msg[:800] + "…") if len(msg) > 800 else msg
    try:
        app.logger.warning("PostgreSQL compat %s: %s", where, short)
    except Exception:
        pass
    if sql and _pg_compat_sql_debug_enabled():
        s = str(sql).strip()
        if len(s) > 4000:
            s = s[:4000] + "…"
        try:
            app.logger.warning("PostgreSQL compat SQL (debug): %s", s)
        except Exception:
            pass


# Admin credentials from environment (ADMIN_PASSWORD required in production)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or (None if os.environ.get('FLASK_ENV') == 'production' else 'Mq12345678@')
if ADMIN_PASSWORD is None:
    raise ValueError("ADMIN_PASSWORD environment variable must be set in production")


def is_admin_user(user) -> bool:
    return bool(
        getattr(user, "is_authenticated", False)
        and getattr(user, "username", None) == ADMIN_USERNAME
    )


def is_manager_user(user) -> bool:
    return bool(getattr(user, "is_authenticated", False) and getattr(user, "is_manager", False))


def is_teacher_user(user) -> bool:
    return bool(getattr(user, "is_authenticated", False) and getattr(user, "is_teacher", False))


def is_analytics_user(user) -> bool:
    """Analytics / district-style accounts (legacy: learner_id ALL)."""
    if not getattr(user, "is_authenticated", False):
        return False
    if is_admin_user(user):
        return True
    try:
        return str(getattr(user, "learner_id", "") or "").strip().upper() == "ALL"
    except Exception:
        return False


def is_guardian_parent_account(user) -> bool:
    """Parents/guardians (hide sensitive disciplinary PDFs); not staff accounts."""
    if not getattr(user, "is_authenticated", False):
        return False
    if is_admin_user(user) or is_teacher_user(user) or is_manager_user(user):
        return False
    return bool(getattr(user, "is_parent", False))


csrf = CSRFProtect(app)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')


@app.context_processor
def inject_admin_flag():
    """Expose portal flags in templates so navbar/UX can adapt."""
    try:
        from flask_login import current_user
        is_admin = (
            getattr(current_user, 'is_authenticated', False)
            and getattr(current_user, 'username', None) == ADMIN_USERNAME
        )
        is_manager = bool(
            getattr(current_user, 'is_authenticated', False)
            and getattr(current_user, 'is_manager', False)
        )
        is_teacher = bool(
            getattr(current_user, 'is_authenticated', False)
            and getattr(current_user, 'is_teacher', False)
        )

        portal_mode = session.get("portal_mode", "parent")
        is_graphs_unrestricted = is_admin or (is_manager and portal_mode == "management")
        teacher_active = bool(is_teacher and portal_mode == "teacher")

        mgmt_active = bool(is_manager and portal_mode == "management")
        # If not in Management Portal mode, keep normal dashboard behavior.
        # Admins always have unrestricted reporting access.
        can_view_academics = True
        can_view_disciplinary = True
        can_view_attendance = True
        can_view_finance = True
        if not is_admin and mgmt_active:
            can_view_academics = bool(getattr(current_user, 'mgmt_can_view_academics', True))
            can_view_disciplinary = bool(getattr(current_user, 'mgmt_can_view_disciplinary', True))
            can_view_attendance = bool(getattr(current_user, 'mgmt_can_view_attendance', True))
            can_view_finance = bool(getattr(current_user, 'mgmt_can_view_finance', True))
        can_teacher_attendance = bool(getattr(current_user, 'can_teacher_attendance', True))
        can_teacher_discipline = bool(getattr(current_user, 'can_teacher_discipline', True))
        can_teacher_assessments = bool(getattr(current_user, 'can_teacher_assessments', True))
        can_teacher_reports = bool(getattr(current_user, 'can_teacher_reports', True))
        can_teacher_message_parents = bool(getattr(current_user, 'can_teacher_message_parents', False))
        can_teacher_announcements = bool(getattr(current_user, 'can_teacher_announcements', False))
        hide_disciplinary_pdfs = is_guardian_parent_account(current_user)
        can_access_asset_inventory = bool(
            is_admin or is_manager or is_teacher
        )
    except Exception:
        is_admin = False
        is_manager = False
        is_teacher = False
        teacher_active = False
        is_graphs_unrestricted = False
        can_view_academics = True
        can_view_disciplinary = True
        can_view_attendance = True
        can_view_finance = True
        can_teacher_attendance = False
        can_teacher_discipline = False
        can_teacher_assessments = False
        can_teacher_reports = False
        can_teacher_message_parents = False
        can_teacher_announcements = False
        hide_disciplinary_pdfs = False
        can_access_asset_inventory = False
    return dict(
        is_admin=is_admin,
        is_manager=is_manager,
        is_teacher=is_teacher,
        teacher_active=teacher_active,
        graphs_unrestricted=is_graphs_unrestricted,
        can_view_academics=can_view_academics,
        can_view_disciplinary=can_view_disciplinary,
        can_view_attendance=can_view_attendance,
        can_view_finance=can_view_finance,
        can_teacher_attendance=can_teacher_attendance,
        can_teacher_discipline=can_teacher_discipline,
        can_teacher_assessments=can_teacher_assessments,
        can_teacher_reports=can_teacher_reports,
        can_teacher_message_parents=can_teacher_message_parents,
        can_teacher_announcements=can_teacher_announcements,
        hide_disciplinary_pdfs=hide_disciplinary_pdfs,
        can_access_asset_inventory=can_access_asset_inventory,
    )


@app.context_processor
def inject_route_helpers():
    """Let templates hide nav links when optional routes are not registered."""

    def endpoint_available(name: str) -> bool:
        return bool(name and name in app.view_functions)

    return dict(endpoint_available=endpoint_available)


limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Logging (no sensitive data in messages)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
app.logger.setLevel(logging.INFO)


def sanitize_for_logging(data):
    """Remove sensitive information from data before logging."""
    sensitive_keys = {'password', 'token', 'learner_id', 'id', 'csrf_token'}
    if isinstance(data, dict):
        return {k: '***' if k.lower() in sensitive_keys else v for k, v in data.items()}
    return data


def validate_password_strength(password):
    """Validate password meets security requirements."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    common_passwords = ['password', '123456', 'admin', 'qwerty', 'admin123']
    if password.lower() in common_passwords:
        errors.append("Password is too common")
    return len(errors) == 0, errors


PHONE_E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")


def normalize_phone(raw_phone: str) -> str:
    """
    Normalize phone input.

    Accepts common SA formats like:
    - 0821234567
    - 821234567
    - 27821234567
    - +27821234567
    - 00 27 82 123 4567

    Returns E.164 for SA numbers when possible (e.g. +27821234567),
    otherwise returns a cleaned string (may include leading +).
    """
    if raw_phone is None:
        return ""
    phone = str(raw_phone).strip()
    phone = re.sub(r"[\s\-()]+", "", phone)
    # Allow leading 00 -> +
    if phone.startswith("00"):
        phone = "+" + phone[2:]

    # Strip to digits, keep leading +
    if phone.startswith("+"):
        digits = re.sub(r"\D", "", phone[1:])
        phone = "+" + digits
    else:
        digits = re.sub(r"\D", "", phone)
        phone = digits

    # South Africa normalization to E.164
    if phone.startswith("+"):
        if phone.startswith("+27") and len(phone) == 12 and phone[3] != "0":
            return phone
        # If +2708... fix to +278...
        if phone.startswith("+270") and len(phone) >= 13:
            return "+27" + phone[4:]
        return phone

    # digits-only paths
    if phone.startswith("0") and len(phone) == 10:
        return "+27" + phone[1:]
    if phone.startswith("27") and len(phone) == 11:
        return "+" + phone
    if len(phone) == 9 and phone.startswith("8"):
        return "+27" + phone
    return phone


def is_valid_phone(phone: str) -> bool:
    phone = normalize_phone(phone)
    return bool(PHONE_E164_RE.match(phone or ""))


def phone_lookup_variants(raw_phone: str) -> list[str]:
    """
    Build possible stored representations for matching MDB values.
    Your MDB often stores digits-only (no +27), while we store/send E.164.
    """
    normalized = normalize_phone(raw_phone)
    if not normalized:
        return []

    variants: list[str] = []

    def add(v: str):
        v = str(v).strip()
        if v and v not in variants:
            variants.append(v)

    add(normalized)

    # Digits-only versions (common in MDB)
    digits = re.sub(r"\D", "", normalized)
    if digits:
        add(digits)

    # SA-specific alternate forms
    if normalized.startswith("+27"):
        local = "0" + normalized[3:]
        add(local)
        add("27" + normalized[3:])
        add(normalized[1:])  # without '+'
        add(normalized.replace("+", "00", 1))
    elif digits.startswith("27") and len(digits) == 11:
        add("+" + digits)
        add("0" + digits[2:])
    elif digits.startswith("0") and len(digits) == 10:
        add("+27" + digits[1:])
        add("27" + digits[1:])

    return variants


@app.after_request
def set_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https: blob:; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "connect-src 'self';"
    )
    return response


db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Standard login page

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access"""
    flash('Please login to access this page', 'error')
    return redirect(url_for('login'))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Legacy username (LearnerID / admin)
    phone = db.Column(db.String(32), unique=True, nullable=True)  # Parent login identifier
    password_hash = db.Column(db.String(255), nullable=False)
    dashboard_token = db.Column(db.String(64), nullable=True)  # No longer unique, not used anymore
    first_login = db.Column(db.Boolean, default=True)
    learner_id = db.Column(db.String(50))  # Legacy single-learner binding (Learner_Info.ID)
    is_parent = db.Column(db.Boolean, default=False)
    is_manager = db.Column(db.Boolean, default=False)  # Management Portal access
    is_teacher = db.Column(db.Boolean, default=False)
    educator_id = db.Column(db.String(64), unique=True, nullable=True)
    teacher_role = db.Column(db.String(32), default='Teacher')  # Teacher | HOD | Principal
    teacher_status = db.Column(db.String(32), default='Active')
    can_teacher_attendance = db.Column(db.Boolean, default=True)
    can_teacher_discipline = db.Column(db.Boolean, default=True)
    can_teacher_assessments = db.Column(db.Boolean, default=True)
    can_teacher_reports = db.Column(db.Boolean, default=True)
    can_teacher_message_parents = db.Column(db.Boolean, default=False)
    can_teacher_announcements = db.Column(db.Boolean, default=False)
    mgmt_can_view_academics = db.Column(db.Boolean, default=True)
    mgmt_can_view_disciplinary = db.Column(db.Boolean, default=True)
    mgmt_can_view_attendance = db.Column(db.Boolean, default=True)
    mgmt_can_view_finance = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserLearner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    learner_id = db.Column(db.String(50), nullable=False)  # Learner_Info.ID (matches ReportMarks.LearnerID)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'learner_id', name='uq_user_learner'),)


class OtpChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(32), nullable=False, index=True)
    purpose = db.Column(db.String(32), nullable=False, index=True)  # "register"
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    attempts_remaining = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sent_at = db.Column(db.DateTime, nullable=True)
    send_count = db.Column(db.Integer, default=0)


class DashboardAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accessed_at = db.Column(db.DateTime, default=datetime.utcnow)

class SlideshowImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(500))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    profile_photo = db.Column(db.String(255), nullable=True)  # Filename of profile photo
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserTeacherAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    class_id = db.Column(db.String(64), nullable=False, index=True)
    grade = db.Column(db.String(32), nullable=True)
    subject = db.Column(db.String(128), nullable=True)
    academic_year = db.Column(db.String(8), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'class_id', 'subject', 'academic_year', name='uq_teacher_assignment'),
    )


class TeacherAuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    action = db.Column(db.String(64), nullable=False, index=True)
    module = db.Column(db.String(64), nullable=False, index=True)
    payload_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class TeacherTermLock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    academic_year = db.Column(db.String(8), nullable=False, index=True)
    term = db.Column(db.String(16), nullable=False, index=True)
    attendance_locked = db.Column(db.Boolean, default=False)
    discipline_locked = db.Column(db.Boolean, default=False)
    assessments_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('academic_year', 'term', name='uq_teacher_term_lock'),)


class TeacherAnnouncement(db.Model):
    __tablename__ = 'teacher_announcement'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    target_grade = db.Column(db.String(32), nullable=True)
    target_class = db.Column(db.String(64), nullable=True)
    scope = db.Column(db.String(16), nullable=False, default='teacher', index=True)  # teacher|school
    priority = db.Column(db.String(16), nullable=False, default='normal')  # low|normal|high|urgent
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeacherWriteEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    module = db.Column(db.String(32), nullable=False, index=True)
    idempotency_key = db.Column(db.String(128), nullable=False, index=True)
    response_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'module', 'idempotency_key', name='uq_teacher_write_event'),)


class ChatThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_type = db.Column(db.String(24), nullable=False, default='direct', index=True)  # direct|group|escalation
    learner_id = db.Column(db.String(50), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(16), nullable=False, default='active', index=True)  # active|archived
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)


class ChatParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    role_in_thread = db.Column(db.String(32), nullable=True)
    can_post = db.Column(db.Boolean, default=True)
    last_read_message_id = db.Column(db.Integer, nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_muted = db.Column(db.Boolean, default=False)
    __table_args__ = (db.UniqueConstraint('thread_id', 'user_id', name='uq_chat_participant'),)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id'), nullable=False, index=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    body = db.Column(db.Text, nullable=True)
    message_type = db.Column(db.String(16), nullable=False, default='text', index=True)  # text|file|system
    moderation_status = db.Column(db.String(16), nullable=False, default='visible', index=True)  # visible|hidden
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    edited_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)


class ChatAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'), nullable=False, index=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False, unique=True)
    mime_type = db.Column(db.String(128), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=False, default=0)
    storage_relpath = db.Column(db.String(512), nullable=False)
    scan_status = db.Column(db.String(24), nullable=False, default='not_scanned')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class ChatMessageReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True, index=True)
    __table_args__ = (db.UniqueConstraint('message_id', 'user_id', name='uq_chat_message_receipt'),)


class ProfileChangeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    learner_id = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False, default='pending', index=True)  # pending|approved|rejected
    parent_comment = db.Column(db.Text, nullable=True)
    admin_comment = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True, index=True)
    reviewed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)


class ProfileChangeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('profile_change_request.id'), nullable=False, index=True)
    entity = db.Column(db.String(32), nullable=False, index=True)  # learner_info|parent_info
    record_key = db.Column(db.String(64), nullable=False, index=True)  # learner id or parent id
    field_name = db.Column(db.String(64), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class DisciplinaryDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disciplinary_record_id = db.Column(db.Integer, nullable=False, index=True)
    learner_id = db.Column(db.String(50), nullable=False, index=True)
    pdf_filename = db.Column(db.String(255), nullable=False)
    pdf_relpath = db.Column(db.String(512), nullable=False)
    image_relpaths_json = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    created_by_name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class SickNoteSubmission(db.Model):
    """Parent-uploaded doctor's / sick notes for admin review."""
    id = db.Column(db.Integer, primary_key=True)
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    learner_id = db.Column(db.String(50), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    storage_relpath = db.Column(db.String(512), nullable=False)
    mime_type = db.Column(db.String(128), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=False, default=0)
    parent_note = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class DetentionNoticeBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(32), nullable=False, index=True)
    phase_name = db.Column(db.String(64), nullable=False)
    data_year = db.Column(db.String(8), nullable=False, index=True)
    detention_date = db.Column(db.DateTime, nullable=False, index=True)
    educator_name = db.Column(db.String(120), nullable=False)
    learner_count = db.Column(db.Integer, nullable=False, default=0)
    learner_ids_json = db.Column(db.Text, nullable=True)
    notifications_filename = db.Column(db.String(255), nullable=False)
    notifications_relpath = db.Column(db.String(512), nullable=False)
    attendance_filename = db.Column(db.String(255), nullable=False)
    attendance_relpath = db.Column(db.String(512), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    created_by_name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class CommunicationDeliveryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32), nullable=False, index=True)  # custom|discipline|finance
    reference_type = db.Column(db.String(32), nullable=True, index=True)  # learner|incident|none
    reference_id = db.Column(db.String(64), nullable=True, index=True)
    recipient_name = db.Column(db.String(160), nullable=True)
    recipient_phone = db.Column(db.String(32), nullable=False, index=True)
    channel = db.Column(db.String(16), nullable=False, index=True)  # sms|whatsapp
    message_snapshot = db.Column(db.Text, nullable=False)
    sent_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    sent_by_username = db.Column(db.String(80), nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.String(24), nullable=False, default='sent', index=True)  # sent|failed
    error_message = db.Column(db.Text, nullable=True)
    batch_id = db.Column(db.String(64), nullable=False, index=True)


# -----------------------------------------------------------------------------
# School asset inventory (staff-only: admin, managers, teachers — not parents)
# -----------------------------------------------------------------------------

class SchoolAssetCategory(db.Model):
    __tablename__ = 'school_asset_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    sort_index = db.Column(db.Integer, default=0)


class SchoolAssetModel(db.Model):
    """Product line / asset model grouping common specs (Snipe-style models)."""

    __tablename__ = 'school_asset_model'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('school_asset_category.id'), nullable=True, index=True)
    item_type = db.Column(db.String(24), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    manufacturer = db.Column(db.String(160), nullable=True)
    description = db.Column(db.Text, nullable=True)
    low_stock_threshold = db.Column(db.Integer, nullable=True)
    default_location = db.Column(db.String(200), nullable=True)
    is_requestable = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SchoolAssetCustomField(db.Model):
    """Per-model dynamic attribute definitions (stored values live on SchoolAssetItem.custom_values_json)."""

    __tablename__ = 'school_asset_custom_field'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('school_asset_model.id'), nullable=False, index=True)
    field_key = db.Column(db.String(64), nullable=False)
    field_label = db.Column(db.String(120), nullable=False)
    field_type = db.Column(db.String(16), nullable=False, default='text')  # text|number|bool|date
    is_required = db.Column(db.Boolean, default=False)
    sort_index = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('model_id', 'field_key', name='uq_asset_custom_field_model_key'),)


class SchoolAssetItem(db.Model):
    __tablename__ = 'school_asset_item'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('school_asset_model.id'), nullable=False, index=True)
    tag = db.Column(db.String(80), nullable=False, unique=True, index=True)
    serial_number = db.Column(db.String(120), nullable=True, index=True)
    scan_token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    quantity_on_hand = db.Column(db.Integer, nullable=False, default=1)
    ops_status = db.Column(db.String(24), nullable=False, default='ready', index=True)
    archived_reason = db.Column(db.String(32), nullable=True)
    physical_location = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_requestable_override = db.Column(db.Boolean, nullable=True)
    custom_values_json = db.Column(db.Text, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SchoolAssetCheckout(db.Model):
    __tablename__ = 'school_asset_checkout'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('school_asset_item.id'), nullable=False, index=True)
    assignee_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    checked_out_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    checked_out_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expected_return_at = db.Column(db.DateTime, nullable=True, index=True)
    checkin_at = db.Column(db.DateTime, nullable=True, index=True)
    acceptance_signature_png = db.Column(db.Text, nullable=True)
    checkout_notes = db.Column(db.String(500), nullable=True)


class SchoolAssetMaintenance(db.Model):
    __tablename__ = 'school_asset_maintenance'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('school_asset_item.id'), nullable=False, index=True)
    logged_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    summary = db.Column(db.String(200), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    cost_cents = db.Column(db.Integer, nullable=True)
    serviced_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class SchoolAssetActivity(db.Model):
    __tablename__ = 'school_asset_activity'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('school_asset_item.id'), nullable=True, index=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    action = db.Column(db.String(48), nullable=False, index=True)
    summary = db.Column(db.String(500), nullable=False)
    payload_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)


class SchoolAssetRequest(db.Model):
    __tablename__ = 'school_asset_request'

    id = db.Column(db.Integer, primary_key=True)
    requester_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('school_asset_item.id'), nullable=True, index=True)
    model_id = db.Column(db.Integer, db.ForeignKey('school_asset_model.id'), nullable=True, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(16), nullable=False, default='pending', index=True)
    decided_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    decided_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class MessageTemplate(db.Model):
    __tablename__ = 'message_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(32), nullable=False, default='general', index=True)  # attendance|behavior|academic|general
    body = db.Column(db.Text, nullable=False)
    placeholders_json = db.Column(db.Text, nullable=True)  # JSON list like ["parent_name","learner_name","grade"]
    is_active = db.Column(db.Boolean, default=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------------------------------------------------------
# Lightweight SQLAlchemy schema bootstrap
# ---------------------------------------------------------------------------
def ensure_app_schema():
    """Create SQLAlchemy models for whichever DB URI is configured."""
    try:
        db.create_all()
        ensure_school_asset_item_columns()
        ensure_announcement_columns()
        ensure_pg_compat_views()
        _sync_postgres_id_sequences()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        app.logger.error("Schema ensure failed: %s", str(e), exc_info=True)
        return False


def ensure_school_asset_item_columns():
    """
    Add newer inventory columns when the DB was created before they existed.
    (create_all does not ALTER existing PostgreSQL tables.)
    """
    try:
        uri = str(app.config.get("SQLALCHEMY_DATABASE_URI") or "").lower()
        if not uri.startswith("postgresql"):
            return True
        if not pg_table_exists("school_asset_item"):
            return True
        row = db.session.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'school_asset_item'
                  AND column_name = 'serial_number'
                LIMIT 1
                """
            )
        ).first()
        if row:
            return True
        db.session.execute(
            text("ALTER TABLE school_asset_item ADD COLUMN serial_number VARCHAR(120)")
        )
        db.session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_school_asset_item_serial_number "
                "ON school_asset_item (serial_number)"
            )
        )
        app.logger.info("PostgreSQL: added school_asset_item.serial_number")
        return True
    except Exception as e:
        app.logger.warning("ensure_school_asset_item_columns: %s", e)
        return False


def ensure_announcement_columns():
    """Add scope/priority/expires_at/updated_at columns to teacher_announcement if missing."""
    try:
        tn = "teacher_announcement"
        # Use SQLAlchemy inspector to check existing columns
        from sqlalchemy import inspect as sa_inspect
        insp = sa_inspect(db.engine)
        existing = {c["name"] for c in insp.get_columns(tn)} if insp.has_table(tn) else set()
        if not existing:
            return True  # table doesn't exist yet — create_all will handle it

        uri = str(app.config.get("SQLALCHEMY_DATABASE_URI") or "").lower()
        is_pg = uri.startswith("postgresql")

        additions = {
            "scope": "VARCHAR(16) NOT NULL DEFAULT 'teacher'",
            "priority": "VARCHAR(16) NOT NULL DEFAULT 'normal'",
            "expires_at": "DATETIME",
            "updated_at": "DATETIME",
        }

        for col_name, col_type in additions.items():
            if col_name in existing:
                continue
            safe_col = _safe_identifier(col_name)
            if is_pg:
                # PostgreSQL: use IF NOT NULL / DEFAULT pattern
                db.session.execute(text(f"ALTER TABLE {tn} ADD COLUMN {safe_col} {col_type}"))
            else:
                # SQLite ignores most column constraints in ALTER, so we keep it simple
                db.session.execute(text(f"ALTER TABLE {tn} ADD COLUMN {safe_col} {col_type}"))
            app.logger.info(f"Added teacher_announcement.{col_name}")

        # Create indexes for new indexed columns
        if "scope" not in existing and is_pg:
            db.session.execute(
                text(f"CREATE INDEX IF NOT EXISTS ix_teacher_announcement_scope ON {tn} (scope)")
            )
        if "expires_at" not in existing and is_pg:
            db.session.execute(
                text(f"CREATE INDEX IF NOT EXISTS ix_teacher_announcement_expires_at ON {tn} (expires_at)")
            )

        return True
    except Exception as e:
        app.logger.warning("ensure_announcement_columns: %s", e)
        return False


def ensure_sqlite_schema():
    """Backward-compatible alias for older test helpers."""
    return ensure_app_schema()


def pg_table_exists(table_name: str) -> bool:
    try:
        t = str(table_name or "").strip()
        if not t:
            return False
        q = """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema='public' AND (table_name = :t OR table_name = :tl)
            LIMIT 1
        """
        row = db.session.execute(text(q), {"t": t, "tl": t.lower()}).first()
        return bool(row)
    except Exception:
        return False


_SAFE_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

def _safe_identifier(name: str) -> str:
    """Validate SQL identifier (table/column name) is safe."""
    if not _SAFE_IDENTIFIER_RE.match(str(name or "")):
        raise ValueError(f"Unsafe SQL identifier: {name!r}")
    return name

def ensure_pg_compat_views():
    """
    Create lowercase compatibility views for mixed-case MDB mirror tables.
    This allows legacy Access-style unquoted identifiers to resolve in PostgreSQL.
    """
    try:
        rows = db.session.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_type='BASE TABLE'
                ORDER BY table_name
                """
            )
        ).fetchall()
        for (table_name_raw,) in rows:
            table_name = str(table_name_raw or "")
            lower_name = table_name.lower()
            if not table_name or table_name == lower_name:
                continue
            cols = db.session.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema='public' AND table_name=:t
                    ORDER BY ordinal_position
                    """
                ),
                {"t": table_name},
            ).fetchall()
            if not cols:
                continue
            select_cols = []
            for (col_raw,) in cols:
                col = str(col_raw or "")
                if not col:
                    continue
                qcol = '"' + col.replace('"', '""') + '"'
                qalias = '"' + col.lower().replace('"', '""') + '"'
                select_cols.append(f"{qcol} AS {qalias}")
            if not select_cols:
                continue
            qlower = '"' + lower_name.replace('"', '""') + '"'
            qtable = '"' + table_name.replace('"', '""') + '"'
            _safe_identifier(lower_name)
            _safe_identifier(table_name)
            for sc in select_cols:
                pass  # already double-quote escaped from DB metadata
            db.session.execute(text(f"DROP VIEW IF EXISTS {qlower} CASCADE"))
            db.session.execute(text(f"CREATE VIEW {qlower} AS SELECT {', '.join(select_cols)} FROM {qtable}"))
    except Exception as e:
        app.logger.warning("Failed to ensure PostgreSQL compatibility views: %s", str(e))


def _sync_postgres_id_sequences():
    """
    Keep PostgreSQL autoincrement sequences aligned with existing rows.
    Prevents duplicate key errors when manual DB edits/imports moved IDs ahead of sequence state.
    """
    db_uri = str(app.config.get('SQLALCHEMY_DATABASE_URI') or '').lower()
    if not db_uri.startswith('postgresql'):
        return
    for table in db.metadata.sorted_tables:
        id_col = table.columns.get('id')
        if id_col is None or not bool(id_col.primary_key):
            continue
        table_name = str(table.name).replace('"', '""')
        col_name = str(id_col.name).replace('"', '""')
        literal_table = f'"{table_name}"'
        db.session.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{literal_table}', '{col_name}'),
                    COALESCE((SELECT MAX("{col_name}") FROM "{table_name}"), 1),
                    COALESCE((SELECT MAX("{col_name}") FROM "{table_name}"), 0) > 0
                )
                """
            )
        )


# MDB Database Connection
class MDBConnection:
    """MDB database connection that reads directly from the MDB file using MDBRepository.
    Provides the same execute_query/execute_non_query interface as the original class
    that translated Access SQL to PostgreSQL, but now queries the MDB directly."""

    _SAFE_WRITE_TABLES = {
        "DisciplinaryLearnerMisconduct",
        "DisciplinaryRecords",
        "Learner_Info",
        "Parent_Info",
        "Absentees",
        "ReportMarks",
    }

    def __init__(self, mdb_path, password=None):
        self.mdb_path = mdb_path
        self.password = password
        self.compat_mode = True
        self._repo = None

    @property
    def repo(self):
        if self._repo is None:
            self._repo = MDBRepository(self.mdb_path)
        return self._repo

    def connect(self):
        # MDB is read directly via mdbtools, no connection needed
        return os.path.isfile(self.mdb_path)

    def get_tables(self):
        return self.repo.get_tables()

    def execute_query(self, query, params=None):
        try:
            if params is None:
                params = ()
            elif not isinstance(params, tuple):
                params = tuple(params)
            return self.repo.execute_query(str(query), params) or []
        except Exception as e:
            _log_pg_compat_failure("execute_query", e, sql=query)
            return []

    def execute_non_query(self, query, params=None) -> int:
        try:
            if params is None:
                params = ()
            return self.repo.execute_non_query(str(query), tuple(params))
        except Exception as e:
            _log_pg_compat_failure("execute_non_query", e, sql=query)
            return 0

    def close(self):
        pass

# Initialize MDB connection
mdb_conn = MDBConnection(app.config['MDB_FILE_PATH'], app.config.get('MDB_PASSWORD'))
mdb_repo = mdb_conn.repo

_sync_service = None
_sync_thread = None
_admin_sync_ui_lock = threading.RLock()
_admin_sync_ui_state = {
    "running": False,
    "started_at": None,
    "finished_at": None,
    "total_tables": 0,
    "completed_tables": 0,
    "current_table": "",
    "last_error": "",
    "logs": [],
}

DEFAULT_SYNC_TABLE_CONFIG = [
    {
        "table_name": "Learner_Info",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "ReportMarks",
        "primary_key": "Id",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Educatorgroups",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": ["ID", "EducatorId", "Grade", "TimetableClass", "GroupName"],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "AbsenteesReasons",
        "primary_key": "ReasonID",
        "updated_at_col": "",
        "columns": ["ReasonID", "Reason"],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Staff_CalendarTerms",
        "primary_key": "TermID",
        "updated_at_col": "",
        "columns": ["TermID", "CurrentYear", "Term", "StartDate", "EndDate"],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Staff_CalendarWeekSetup",
        "primary_key": "WeekID",
        "updated_at_col": "",
        "columns": ["WeekID", "TermID", "Holiday"],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "StaffAbsentees",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": ["ID", "Staffid", "DateAbsent", "Reason", "ReasonOther"],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "GLTrans",
        "primary_key": "TransID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Parent_Info",
        "primary_key": "ParentID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Parent_Child",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "LearnerPromotion",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "ReportCycles",
        "primary_key": "CycleId",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Subjects",
        "primary_key": "Id",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Absentees",
        "primary_key": "Id",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "DisciplinaryRecords",
        "primary_key": "id",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "DisciplinaryLearnerMisconduct",
        "primary_key": "Id",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Educators",
        "primary_key": "EdID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "StaffMembers",
        "primary_key": "StaffID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Fees",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "DebtorsTrans",
        "primary_key": "TransID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Journals",
        "primary_key": "ID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
    {
        "table_name": "Receipt_Info",
        "primary_key": "ReceiptID",
        "updated_at_col": "",
        "columns": [],
        "mode": "full_refresh",
        "bidirectional": False,
    },
]


_SQL_KEYWORDS = frozenset({
    "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "IS", "NULL",
    "AS", "ON", "TOP", "DISTINCT", "JOIN", "LEFT", "RIGHT", "INNER",
    "OUTER", "CROSS", "FULL", "ORDER", "GROUP", "BY", "HAVING", "LIMIT",
    "OFFSET", "UNION", "ALL", "ANY", "EXISTS", "CASE", "WHEN", "THEN",
    "ELSE", "END", "COALESCE", "CAST", "EXTRACT", "SUM", "AVG", "COUNT",
    "MIN", "MAX", "UPPER", "LOWER", "POSITION", "CURRENT_TIMESTAMP",
    "CURRENT_DATE", "TRUE", "FALSE", "YEAR", "MONTH", "DAY", "UCASE",
    "LCASE", "IIF", "ISNULL", "INSTR", "NOW", "DATE", "CSTR", "TEXT",
    "BETWEEN", "LIKE", "ESCAPE", "DESC", "ASC",
    "TRIM", "NULLS", "LAST",
})


def _replace_cstr_with_cast(sql: str) -> str:
    """Replace CSTR(expr) with CAST(expr AS TEXT) using paren-depth tracking.

    The old regex-based approach used ``[^)]+?`` which broke on nested
    parentheses (e.g. CSTR(EXTRACT(YEAR FROM a.DateAbsent))).  This version
    scans character-by-character to find the matching closing paren.
    """
    result: list[str] = []
    i = 0
    while i < len(sql):
        m = re.search(r"\bCSTR\s*\(", sql[i:], re.IGNORECASE)
        if not m:
            result.append(sql[i:])
            break
        # Text before CSTR
        result.append(sql[i : i + m.start()])
        # Balanced-paren scan for the closing ')'
        inner_start = i + m.end()
        depth = 1
        j = inner_start
        while j < len(sql) and depth > 0:
            ch = sql[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth > 0:
                j += 1
        if depth != 0:
            # Unmatched — emit as-is
            result.append(sql[i + m.start() : j + 1])
            i = j + 1
            continue
        inner = sql[inner_start:j]
        result.append(f"CAST({inner} AS TEXT)")
        i = j + 1
    return "".join(result)


def _quote_bare_ems_identifiers(sql: str) -> str:
    """Quote any bare PascalCase identifier that is NOT already quoted,
    NOT a SQL keyword, NOT inside a single-quoted string literal, and NOT
    preceded by a ``.`` (already table-qualified).

    This catches column names that survive the earlier translation steps
    without quotes — for example ``CAST(ID AS TEXT)`` where ``ID`` would
    otherwise be lowercased by PostgreSQL.
    """
    out: list[str] = []
    i = 0
    while i < len(sql):
        # Skip single-quoted string literals entirely
        sq = sql.find("'", i)
        # Skip double-quoted identifiers entirely
        dq = sql.find('"', i)

        # Find the earliest of: string literal, double-quoted, or end
        next_special = None
        if sq != -1 and (next_special is None or sq < next_special):
            next_special = sq
        if dq != -1 and (next_special is None or dq < next_special):
            next_special = dq

        if next_special is None:
            # No more quotes — process rest and stop
            out.append(_quote_bare_identifiers_in_span(sql[i:]))
            break

        # Process up to the quote boundary
        out.append(_quote_bare_identifiers_in_span(sql[i:next_special]))

        # Emit the quote and consume until its match
        if next_special == dq:
            close_dq = sql.find('"', dq + 1)
            if close_dq == -1:
                close_dq = len(sql) - 1
            out.append(sql[dq : close_dq + 1])
            i = close_dq + 1
        else:
            close_sq = sql.find("'", sq + 1)
            if close_sq == -1:
                close_sq = len(sql) - 1
            out.append(sql[sq : close_sq + 1])
            i = close_sq + 1

    return "".join(out)


def _quote_bare_identifiers_in_span(span: str) -> str:
    """Quote PascalCase identifiers in a span that contains no quote characters."""
    # Tokenize: split on boundaries between word / non-word
    tokens: list[str] = re.split(r"(\W+)", span)
    for idx, tok in enumerate(tokens):
        # Must be a word, start uppercase, length ≥2, not a keyword
        if not re.fullmatch(r"[A-Z][a-zA-Z0-9_]+", tok):
            continue
        if tok.upper() in _SQL_KEYWORDS:
            continue
        # Preceded by dot means table-qualified — skip
        if idx > 0 and tokens[idx - 1].endswith("."):
            continue
        # Already quoted?  (shouldn't happen since we split on non-word, but guard)
        if not tok.startswith('"'):
            tokens[idx] = f'"{tok}"'
    return "".join(tokens)


def _ems_compat_table_names() -> frozenset[str]:
    """Table names created by sync / EMS that must stay quoted in PostgreSQL."""
    names = {str(x["table_name"]) for x in DEFAULT_SYNC_TABLE_CONFIG if x.get("table_name")}
    extra = os.environ.get("PG_COMPAT_EXTRA_TABLES", "")
    for raw in extra.split(","):
        t = raw.strip()
        if t:
            names.add(t)
    return frozenset(names)


def _quote_known_ems_tables(sql: str) -> str:
    """
    Quote bare EMS table identifiers for PostgreSQL.

    SyncService creates mixed-case tables with quoted identifiers (e.g. "ReportMarks").
    Legacy SQL often uses unquoted `FROM ReportMarks rm`; PostgreSQL folds those to
    lowercase and they no longer match `"ReportMarks"`, so queries return no rows
    and compat mode swallowed errors unless PG_COMPAT_SQL_DEBUG was on.
    """
    q = str(sql or "")
    for name in sorted(_ems_compat_table_names(), key=len, reverse=True):
        if not name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            continue
        esc = re.escape(name)
        pat_kw = re.compile(rf"\b(FROM|JOIN|INTO|UPDATE)\s+{esc}\b(?=\s)", re.IGNORECASE)
        q = pat_kw.sub(lambda m, n=name: f'{m.group(1)} "{n}"', q)
        pat_comma = re.compile(
            rf"(,\s*)({esc})(?=\s+[A-Za-z_][A-Za-z0-9_]*(?:\s|$|,|\)|;))",
            re.IGNORECASE,
        )
        q = pat_comma.sub(lambda m, n=name: f'{m.group(1)}"{n}"', q)
    return q


_PG_EMS_SKIP_LOWERCASE_COLS = frozenset(
    {
        "on",
        "as",
        "or",
        "and",
        "not",
        "in",
        "is",
        "to",
        "at",
        "by",
        "end",
        "then",
        "else",
        "when",
        "case",
        "from",
        "join",
        "into",
        "over",
        "null",
        "true",
        "false",
        "asc",
        "desc",
        "using",
        "like",
        "between",
    }
)


def _quote_qualified_ems_columns(sql: str) -> str:
    """
    Quote `alias.Column` when Column is not all-lowercase. Synced EMS columns are stored
    as mixed-case identifiers (e.g. "ReportId"); bare `rm.ReportId` is lowercased by
    PostgreSQL and fails to resolve.
    """
    q = str(sql or "")
    pat = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b")

    def repl(m) -> str:
        alias, col = m.group(1), m.group(2)
        if col.islower() and col.lower() in _PG_EMS_SKIP_LOWERCASE_COLS:
            return m.group(0)
        if col != col.lower():
            return f'{alias}."{col}"'
        return m.group(0)

    return pat.sub(repl, q)


def get_sync_service():
    global _sync_service
    if _sync_service is not None:
        return _sync_service
    try:
        from sync_service import SyncService, parse_sync_config
    except Exception as e:
        app.logger.warning("Sync service unavailable (legacy MDB dependency missing): %s", str(e))
        return None
    pg_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not pg_url or not str(pg_url).startswith("postgresql"):
        app.logger.info("Sync service skipped: SQLALCHEMY_DATABASE_URI is not PostgreSQL.")
        return None
    cfg_raw = os.environ.get("SYNC_TABLE_CONFIG", "").strip()
    if not cfg_raw:
        cfg_raw = json.dumps(DEFAULT_SYNC_TABLE_CONFIG)
        app.logger.info("SYNC_TABLE_CONFIG not set; using built-in default sync config.")
    table_cfg = parse_sync_config(cfg_raw)
    if not table_cfg:
        app.logger.info("Sync service skipped: SYNC_TABLE_CONFIG is empty.")
        return None
    _sync_service = SyncService(
        mdb_path=app.config["MDB_FILE_PATH"],
        mdb_password=app.config.get("MDB_PASSWORD"),
        postgres_url=pg_url,
        table_configs=table_cfg,
        max_retries=int(os.environ.get("SYNC_MDB_MAX_RETRIES", "5")),
        retry_base_ms=int(os.environ.get("SYNC_MDB_RETRY_BASE_MS", "300")),
        progress_log=_admin_sync_ui_log,
    )
    return _sync_service


@app.cli.command("sync-once")
def sync_once_command():
    svc = get_sync_service()
    if not svc:
        print("Sync service not configured.")
        return
    svc.sync_once()
    print("Sync complete.")


@app.cli.command("sync-daemon")
def sync_daemon_command():
    svc = get_sync_service()
    if not svc:
        print("Sync service not configured.")
        return
    interval = int(app.config.get("SYNC_INTERVAL_SECONDS", 120))
    svc.run_forever(interval_seconds=interval)


def start_sync_background_thread():
    global _sync_thread
    if not app.config.get("ENABLE_SYNC_THREAD"):
        return
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return
    svc = get_sync_service()
    if not svc:
        return
    if _sync_thread and _sync_thread.is_alive():
        return
    _sync_thread = threading.Thread(
        target=svc.run_forever,
        kwargs={"interval_seconds": int(app.config.get("SYNC_INTERVAL_SECONDS", 120))},
        daemon=True,
        name="mdb-postgres-sync-worker",
    )
    _sync_thread.start()


def _admin_sync_ui_log(message: str, level: str = "info") -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": str(level or "info"),
        "message": str(message or ""),
    }
    with _admin_sync_ui_lock:
        logs = list(_admin_sync_ui_state.get("logs") or [])
        logs.append(entry)
        # Keep memory bounded.
        _admin_sync_ui_state["logs"] = logs[-500:]

# ---------------------------------------------------------------------------
# Parent ↔ Learner resolution (from MDB)
# ---------------------------------------------------------------------------
def lookup_learners_by_parent_phone(phone: str) -> list[str]:
    """
    Return Learner_Info.ID values (as strings) associated with this parent phone.

    This function supports two modes:
    - If env vars are provided, use them:
      - PARENT_PHONE_TABLE, PARENT_PHONE_COLUMN, PARENT_LEARNER_ID_COLUMN
    - Otherwise, attempt a few common table/column names heuristically.
    """
    variants = phone_lookup_variants(phone)
    if not variants:
        return []

    # Preferred path for this school's schema:
    # Parent_Info (Tel1/Tel2/Tel3/SpouseCell) -> Parent_Child (ChildId is Learner_Info.ID)
    learner_ids: list[str] = []
    use_pg_repo = True
    parent_phone_cols = ["Tel1", "Tel2", "Tel3", "SpouseCell"]
    for vphone in variants:
        try:
            if use_pg_repo:
                learner_ids = mdb_repo.map_parent_phone_to_learner_keys(vphone)
                if learner_ids:
                    break
            # Prefer ChildId (Learner_Info.ID used elsewhere in this app)
            for col in parent_phone_cols:
                q = (
                    "SELECT DISTINCT pc.ChildId AS LearnerKey "
                    "FROM Parent_Info pi INNER JOIN Parent_Child pc ON pc.ParentId = pi.ParentID "
                    f"WHERE pi.[{col}] = ?"
                )
                rows = mdb_conn.execute_query(q, (vphone,))
                if rows:
                    for r in rows:
                        v = r.get("LearnerKey")
                        if v is not None and str(v).strip():
                            learner_ids.append(str(v).strip())
                if learner_ids:
                    break

            # Fallback: if only Learnerid (accession) is populated
            if not learner_ids:
                for col in parent_phone_cols:
                    q = (
                        "SELECT DISTINCT pc.Learnerid AS LearnerKey "
                        "FROM Parent_Info pi INNER JOIN Parent_Child pc ON pc.ParentId = pi.ParentID "
                        f"WHERE pi.[{col}] = ?"
                    )
                    rows = mdb_conn.execute_query(q, (vphone,))
                    if rows:
                        for r in rows:
                            v = r.get("LearnerKey")
                            if v is not None and str(v).strip():
                                learner_ids.append(str(v).strip())
                    if learner_ids:
                        break
        except Exception:
            continue

        if learner_ids:
            break

    configured = (
        os.environ.get("PARENT_PHONE_TABLE"),
        os.environ.get("PARENT_PHONE_COLUMN"),
        os.environ.get("PARENT_LEARNER_ID_COLUMN"),
    )
    candidates: list[tuple[str, str, str]] = []
    if all(configured):
        candidates.append((configured[0], configured[1], configured[2]))
    else:
        candidates.extend(
            [
                ("Learner_Info", "Cell", "ID"),
                ("Learner_Info", "CellNo", "ID"),
                ("Learner_Info", "Phone", "ID"),
                ("Learner_Info", "ParentCell", "ID"),
                ("Learner_Info", "ParentPhone", "ID"),
                ("Parents", "Cell", "LearnerID"),
                ("Parents", "Phone", "LearnerID"),
                ("Parent_Info", "Cell", "LearnerID"),
                ("Guardian_Info", "Cell", "LearnerID"),
                ("NextOfKin", "Cell", "LearnerID"),
            ]
        )

    for table, phone_col, learner_col in candidates:
        try:
            _safe_identifier(table)
            _safe_identifier(phone_col)
            _safe_identifier(learner_col)
            for vphone in variants:
                if use_pg_repo:
                    try:
                        rows = mdb_repo.generic_phone_lookup(table, phone_col, learner_col, vphone)
                        if rows:
                            learner_ids.extend(rows)
                            break
                    except Exception:
                        pass
                q = f"SELECT DISTINCT [{learner_col}] AS LearnerKey FROM [{table}] WHERE [{phone_col}] = ?"
                rows = mdb_conn.execute_query(q, (vphone,))
                if rows:
                    for r in rows:
                        v = r.get("LearnerKey")
                        if v is not None and str(v).strip():
                            learner_ids.append(str(v).strip())
                if learner_ids:
                    break
        except Exception:
            continue

        if learner_ids:
            break

    # If any keys are actually LearnerID (accession number) instead of Learner_Info.ID,
    # map them to Learner_Info.ID.
    mapped: list[str] = []
    for lid in learner_ids:
        s = str(lid).strip()
        if not s:
            continue
        # 1) Try as Learner_Info.ID
        if s.isdigit():
            try:
                if use_pg_repo and mdb_repo.learner_id_exists(s):
                    mapped.append(str(s).strip())
                    continue
                qid = "SELECT TOP 1 [ID] FROM Learner_Info WHERE [ID] = ?"
                rows_id = mdb_conn.execute_query(qid, (int(s),))
                if rows_id and rows_id[0].get("ID") is not None:
                    mapped.append(str(rows_id[0]["ID"]).strip())
                    continue
            except Exception:
                pass
        # 2) Fallback as accession
        try:
            if use_pg_repo:
                row = mdb_repo.learner_by_id_or_code(s)
                if row and row.get("ID") is not None:
                    mapped.append(str(row["ID"]).strip())
                    continue
            q = "SELECT TOP 1 [ID] FROM Learner_Info WHERE [LearnerID] = ? OR [AccessionNo] = ?"
            rows = mdb_conn.execute_query(q, (s, s))
            if rows and rows[0].get("ID") is not None:
                mapped.append(str(rows[0]["ID"]).strip())
        except Exception:
            continue

    # Preserve both raw keys and resolved Learner_Info.ID keys.
    # Some tables store learner references as LearnerID/accession style strings
    # while others store Learner_Info.ID.
    combined = []
    for x in (learner_ids or []):
        sx = str(x or "").strip()
        if sx:
            combined.append(sx)
    for x in (mapped or []):
        sx = str(x or "").strip()
        if sx:
            combined.append(sx)
            # Expand mapped ID to learner code as well.
            try:
                row = mdb_repo.learner_by_id_or_code(sx)
                if row:
                    code = str(row.get("LearnerID") or "").strip()
                    if code:
                        combined.append(code)
                    acc = str(row.get("AccessionNo") or "").strip()
                    if acc:
                        combined.append(acc)
            except Exception:
                pass

    unique = []
    seen = set()
    for x in combined:
        if x not in seen:
            seen.add(x)
            unique.append(x)
    return unique


def get_linked_learner_ids_for_user(user: User) -> list[str]:
    links = UserLearner.query.filter_by(user_id=user.id).all()
    ids = [str(l.learner_id).strip() for l in links if l.learner_id]
    # Fallback to legacy single learner_id
    if not ids and user.learner_id:
        ids = [str(user.learner_id).strip()]
    return [x for x in ids if x]


def get_active_learner_id_for_request(user: User) -> str | None:
    ids = get_linked_learner_ids_for_user(user)
    if not ids:
        return None
    selected = session.get("active_learner_id")
    if selected and str(selected) in ids:
        return str(selected)
    # Default to first linked learner
    session["active_learner_id"] = ids[0]
    return ids[0]


def fetch_learner_info_by_id(learner_id: str) -> dict | None:
    ident = str(learner_id).strip() if learner_id is not None else ""
    if not ident:
        return None

    def _shape(r: dict) -> dict:
        return {
            "id": r.get("ID"),
            "learner_id": r.get("LearnerID"),
            "name": r.get("FName", "") or "",
            "surname": r.get("SName", "") or "",
            "grade": r.get("Grade", "") or "",
        }

    try:
        pg_row = mdb_repo.learner_by_id_or_code(ident)
        if pg_row:
            return _shape(pg_row)
    except Exception:
        pass

    # Try as Learner_Info.ID
    if ident.isdigit():
        try:
            q = "SELECT TOP 1 [ID], [LearnerID], [FName], [SName], [Grade] FROM Learner_Info WHERE [ID] = ?"
            rows = mdb_conn.execute_query(q, (int(ident),))
            if rows:
                return _shape(rows[0])
        except Exception:
            pass

    # Fallback: LearnerID / AccessionNo
    q2 = "SELECT TOP 1 [ID], [LearnerID], [FName], [SName], [Grade] FROM Learner_Info WHERE [LearnerID] = ? OR [AccessionNo] = ?"
    rows2 = mdb_conn.execute_query(q2, (ident, ident))
    if rows2:
        return _shape(rows2[0])
    return None


def build_learner_lookup_by_any_id(rows: list[dict]) -> dict:
    """
    Build a learner lookup keyed by both Learner_Info.ID and Learner_Info.LearnerID.
    This avoids cross-table key mismatches where some tables reference ID while
    others reference LearnerID.
    """
    lookup = {}
    for r in rows or []:
        info = {
            "id": str(r.get("ID", "") or "").strip(),
            "learner_id": str(r.get("LearnerID", "") or "").strip(),
            "name": str(r.get("FName", "") or "").strip(),
            "surname": str(r.get("SName", "") or "").strip(),
            "grade": str(r.get("Grade", "") or "").strip(),
            "gender": str(r.get("Gender", "") or "").strip(),
            "status": str(r.get("Status", "") or "").strip(),
        }
        if info["id"]:
            lookup[info["id"]] = info
        if info["learner_id"]:
            lookup[info["learner_id"]] = info
    return lookup


def get_learner_match_candidates(learner_ref: str | int | None) -> list[str]:
    """
    Resolve a learner reference into candidate keys usable across MDB tables.
    Returns unique string values including both Learner_Info.ID and LearnerID.
    """
    raw = str(learner_ref or '').strip()
    if not raw:
        return []
    vals = []
    info = fetch_learner_info_by_id(raw)
    if info:
        # Canonical learner key for cross-table matching is Learner_Info.ID.
        # This prevents collisions where one learner's LearnerID equals another learner's ID.
        lid = str(info.get('id', '') or '').strip()
        learner_code = str(info.get('learner_id', '') or '').strip()
        if lid:
            vals.append(lid)

        # Only include LearnerID as a fallback when it is not another learner's ID.
        if learner_code and learner_code != lid:
            include_learner_code = True
            try:
                collision_rows = mdb_conn.execute_query(
                    "SELECT TOP 1 [ID], [LearnerID] FROM Learner_Info WHERE CSTR([ID]) = ?",
                    (learner_code,),
                ) or []
                if collision_rows:
                    other_id = str(collision_rows[0].get('ID', '') or '').strip()
                    if other_id and other_id != lid:
                        include_learner_code = False
            except Exception:
                # Fail-safe: avoid broad matching if we cannot verify collision safety.
                include_learner_code = False
            if include_learner_code:
                vals.append(learner_code)
    else:
        vals.append(raw)
    # preserve order, remove duplicates
    seen = set()
    out = []
    for v in vals:
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


def _learner_match_candidates_with_lookup(
    learner_ref: str | int | None, by_any_id: dict | None
) -> list[str]:
    """
    Same candidate keys as get_learner_match_candidates, but uses an in-memory
    Learner_Info index when provided (no per-call DB).
    """
    if not by_any_id:
        return get_learner_match_candidates(learner_ref)
    raw = str(learner_ref or "").strip()
    if not raw:
        return []
    info = by_any_id.get(raw)
    if info:
        vals: list[str] = []
        lid = str(info.get("id") or "").strip()
        learner_code = str(info.get("learner_id") or "").strip()
        if lid:
            vals.append(lid)
        if learner_code and learner_code != lid:
            vals.append(learner_code)
        seen: set[str] = set()
        out: list[str] = []
        for v in vals:
            if not v or v in seen:
                continue
            seen.add(v)
            out.append(v)
        return out
    return get_learner_match_candidates(learner_ref)


LEARNER_PROFILE_LEARNER_FIELDS = [
    ("LearnerID", "Learner ID"),
    ("AccessionNo", "Accession No"),
    ("FName", "First Name"),
    ("SName", "Surname"),
    ("Gender", "Gender"),
    ("DOB", "Date of Birth"),
    ("Grade", "Grade"),
    ("Class", "Class"),
    ("Status", "Status"),
    ("Guardian", "Guardian"),
    ("ParentTitle", "Parent Title"),
    ("ParentSname", "Parent Surname"),
    ("ParentInitials", "Parent Initials"),
]

LEARNER_PROFILE_PARENT_FIELDS = [
    ("Title", "Title"),
    ("FName", "First Name"),
    ("SName", "Surname"),
    ("IDNo", "ID Number"),
    ("Tel1", "Primary Phone"),
    ("Tel2", "Secondary Phone"),
    ("EMail", "Email"),
    ("Occupation", "Occupation"),
    ("WorkTel", "Work Telephone"),
    ("Address1", "Address Line 1"),
    ("Address2", "Address Line 2"),
    ("Address3", "Address Line 3"),
    ("Address4", "Address Line 4"),
    ("PCode", "Postal Code"),
]

LEARNER_PROFILE_SPOUSE_FIELDS = [
    ("Spouse", "Spouse Surname"),
    ("SpouseFname", "Spouse First Name"),
    ("SpouseGender", "Spouse Gender"),
    ("SpouseID", "Spouse ID"),
    ("SpouseCell", "Spouse Cell"),
    ("SpouseEmail", "Spouse Email"),
    ("SpouseOccupation", "Spouse Occupation"),
    ("SpouseWorkTel", "Spouse Work Telephone"),
]


def _to_text_or_empty(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value).strip()


def _safe_mdb_field_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(name or "").strip()))


def _mdb_get_learner_profile_row(learner_id: str) -> dict:
    ident = str(learner_id or "").strip()
    if not ident:
        return {}
    try:
        rows = mdb_conn.execute_query(
            "SELECT TOP 1 * FROM Learner_Info WHERE CSTR([ID]) = ? OR CSTR([LearnerID]) = ? OR [AccessionNo] = ?",
            (ident, ident, ident),
        )
        return rows[0] if rows else {}
    except Exception:
        return {}


def _mdb_get_parent_profile_row(learner_id: str) -> dict:
    ident = str(learner_id or "").strip()
    if not ident:
        return {}
    params = (ident, ident, ident)
    for col in ("ChildId", "ChildID", "Learnerid"):
        try:
            rows = mdb_conn.execute_query(
                f"""
                SELECT TOP 1 pi.*, pc.[{col}] AS LinkedLearner
                FROM Parent_Info pi
                INNER JOIN Parent_Child pc ON pc.ParentId = pi.ParentID
                WHERE CSTR(pc.[{col}]) = ? OR CSTR(pc.[{col}]) = ? OR CSTR(pc.[{col}]) = ?
                ORDER BY pi.ParentID DESC
                """,
                params,
            )
            if rows:
                return rows[0]
        except Exception:
            continue
    return {}


def _fields_present(row: dict, candidates: list[tuple[str, str]]) -> list[tuple[str, str]]:
    if not row:
        return []
    out = []
    for key, label in candidates:
        if key in row:
            out.append((key, label))
    return out


def _profile_change_items_for_request(request_id: int) -> list[ProfileChangeItem]:
    return (
        ProfileChangeItem.query
        .filter_by(request_id=request_id)
        .order_by(ProfileChangeItem.entity.asc(), ProfileChangeItem.field_name.asc())
        .all()
    )


def send_whatsapp_otp(phone: str, otp: str) -> bool:
    """
    Send OTP via WhatsApp Web service (whatsapp-web.js).
    Returns True if sent successfully, False otherwise (caller should fall back to SMS).
    """
    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        return False
    base_url = app.config.get('WHATSAPP_SERVICE_URL', '').strip()
    if not base_url:
        return False
    msg = f"Kismet Parent Portal OTP: {otp}. Expires in 10 minutes."
    try:
        resp = requests.post(
            f"{base_url}/send",
            json={"to": phone, "message": msg},
            timeout=15,
        )
    except Exception as e:
        app.logger.warning("WhatsApp OTP send failed (will fall back to SMS): %s", str(e))
        return False
    if resp.status_code != 200:
        app.logger.warning("WhatsApp OTP send failed status=%s (will fall back to SMS)", resp.status_code)
        return False
    try:
        data = resp.json()
        if not data.get("success"):
            app.logger.warning("WhatsApp OTP send rejected: %s (will fall back to SMS)", data.get("error", "unknown"))
            return False
    except Exception:
        return False
    return True


def send_otp(phone: str, otp: str) -> None:
    """
    Send OTP: try WhatsApp first (if service is configured and ready), then fall back to SMS.
    Raises on failure only if SMS also fails (or SMS provider not configured).
    """
    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        raise ValueError("Invalid phone number format")
    if send_whatsapp_otp(phone, otp):
        app.logger.info("OTP sent via WhatsApp to %s", phone)
        return
    app.logger.info("WhatsApp not available or failed; falling back to SMS for %s", phone)
    send_sms_otp(phone, otp)


def send_sms_otp(phone: str, otp: str) -> None:
    """
    Send OTP via SMSPortal.

    Uses REST API `POST https://rest.smsportal.com/v3/BulkMessages` with Basic Auth
    per SMSPortal docs:
    - API Keys management: `https://docs.smsportal.com/docs/api-keys`
    - Send endpoint: `https://docs.smsportal.com/reference/bulkmessages_postv3`
    """
    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        raise ValueError("Invalid phone number format")
    app.logger.info("SMS OTP generated for %s: %s", phone, otp)

    client_id = os.environ.get("SMSPORTAL_CLIENT_ID", "").strip()
    api_secret = os.environ.get("SMSPORTAL_API_SECRET", "").strip()
    sender_id = os.environ.get("SMSPORTAL_SENDER_ID", "").strip() or None
    test_mode = os.environ.get("SMSPORTAL_TEST_MODE", "false").strip().lower() in ("1", "true", "yes", "y")

    # If creds aren't configured yet, behave like dev stub (but don't break registration).
    if not client_id or not api_secret:
        app.logger.error("SMSPortal credentials not configured; cannot send OTP SMS.")
        raise RuntimeError("SMS provider not configured")

    msg = f"Kismet Parent Portal OTP: {otp}. Expires in 10 minutes."
    payload = {
        "sendOptions": {
            "allowContentTrimming": True,
            "testMode": test_mode,
        },
        "messages": [
            {
                "destination": phone,
                "content": msg,
                "customerId": f"otp-register-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            }
        ],
    }
    if sender_id:
        payload["sendOptions"]["senderId"] = sender_id

    basic = base64.b64encode(f"{client_id}:{api_secret}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = "https://rest.smsportal.com/v3/BulkMessages"
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception as e:
        app.logger.error("SMSPortal request failed: %s", str(e), exc_info=True)
        raise

    if resp.status_code != 200:
        app.logger.error("SMSPortal send failed: status=%s body=%s", resp.status_code, resp.text[:2000])
        raise RuntimeError(f"SMS send failed (HTTP {resp.status_code})")

    # SMSPortal returns a Response object with statusCode + errors array
    try:
        data = resp.json()
    except Exception:
        data = None

    if isinstance(data, dict):
        status_code = data.get("statusCode")
        errors = data.get("errors") or []
        if status_code and int(status_code) >= 400:
            app.logger.error("SMSPortal send error statusCode=%s errors=%s", status_code, errors)
            raise RuntimeError("SMS send rejected by provider")
        if errors:
            app.logger.warning("SMSPortal send returned errors: %s", errors)
    return


def send_sms_message(phone: str, message: str) -> None:
    """Send an arbitrary SMS via SMSPortal (same API as OTP, custom content)."""
    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        raise ValueError("Invalid phone number format")
    client_id = os.environ.get("SMSPORTAL_CLIENT_ID", "").strip()
    api_secret = os.environ.get("SMSPORTAL_API_SECRET", "").strip()
    sender_id = os.environ.get("SMSPORTAL_SENDER_ID", "").strip() or None
    test_mode = os.environ.get("SMSPORTAL_TEST_MODE", "false").strip().lower() in ("1", "true", "yes", "y")
    if not client_id or not api_secret:
        raise RuntimeError("SMS provider not configured")
    payload = {
        "sendOptions": {"allowContentTrimming": True, "testMode": test_mode},
        "messages": [{"destination": phone, "content": message[:160], "customerId": f"comm-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"}],
    }
    if sender_id:
        payload["sendOptions"]["senderId"] = sender_id
    basic = base64.b64encode(f"{client_id}:{api_secret}".encode("utf-8")).decode("ascii")
    headers = {"Authorization": f"Basic {basic}", "Content-Type": "application/json", "Accept": "application/json"}
    resp = requests.post("https://rest.smsportal.com/v3/BulkMessages", headers=headers, json=payload, timeout=15)
    if resp.status_code != 200:
        app.logger.error("SMSPortal send failed: status=%s body=%s", resp.status_code, resp.text[:500])
        raise RuntimeError(f"SMS send failed (HTTP {resp.status_code})")
    data = resp.json() if resp.text else {}
    if isinstance(data, dict) and data.get("statusCode") and int(data.get("statusCode", 0)) >= 400:
        raise RuntimeError("SMS send rejected by provider")


def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send an arbitrary text message via WhatsApp Web service. Returns True if sent, False otherwise."""
    phone = normalize_phone(phone)
    if not is_valid_phone(phone):
        return False
    base_url = app.config.get("WHATSAPP_SERVICE_URL", "").strip()
    if not base_url:
        return False
    try:
        resp = requests.post(f"{base_url}/send", json={"to": phone, "message": message}, timeout=15)
    except Exception as e:
        app.logger.warning("WhatsApp send failed: %s", str(e))
        return False
    if resp.status_code != 200:
        return False
    try:
        data = resp.json()
        return data.get("success") is True
    except Exception:
        return False


def require_inventory_staff():
    """Return a Flask redirect response if the user may not access inventory routes; else None."""
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if not (is_admin_user(current_user) or is_manager_user(current_user) or is_teacher_user(current_user)):
        flash("You do not have access to asset inventory.", "error")
        return redirect(url_for("dashboard"))
    return None


def _parse_grade_int(grade_value) -> int | None:
    m = re.search(r"(\d+)", str(grade_value or "").strip())
    return int(m.group(1)) if m else None


def _detention_phase_allowed(phase_key: str, grade_num: int) -> bool:
    pk = str(phase_key or "").strip().lower()
    if pk == "foundation":
        return grade_num == 3
    if pk == "primary":
        return 4 <= grade_num <= 7
    if pk in ("highschool", "high_school"):
        return 8 <= grade_num <= 12
    return False


def _fetch_detention_candidates(
    phase: str,
    year: str,
    threshold: int,
    grades: list[int] | None = None,
) -> list[dict]:
    """Learners at disciplinary balance >= threshold for the given data year and phase."""
    year_s = str(year).strip()
    th = max(0, int(threshold))
    phase_key = str(phase or "").strip().lower()
    grades_set: set[int] | None = None
    if grades:
        grades_set = {int(g) for g in grades}
    try:
        summary_rows = mdb_conn.execute_query(
            """
            SELECT
                CSTR(dr.Learnerid) AS LearnerKey,
                SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) AS TotalDemerit,
                SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) AS TotalMerit,
                SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) - SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) AS Balance
            FROM DisciplinaryRecords dr
            WHERE CSTR(dr.Datayear) = ?
            GROUP BY CSTR(dr.Learnerid)
            HAVING SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) - SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) >= ?
            ORDER BY SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) - SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) DESC
            """,
            (year_s, th),
        ) or []
    except Exception:
        app.logger.exception("detention candidate summary query failed")
        return []

    try:
        learner_rows = mdb_conn.execute_query(
            """
            SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Gender], [Status]
            FROM Learner_Info
            """
        ) or []
    except Exception:
        learner_rows = []
    lookup = build_learner_lookup_by_any_id(learner_rows)

    out: list[dict] = []
    for row in summary_rows:
        learner_key = str(row.get("LearnerKey") or "").strip()
        if not learner_key:
            continue
        info = lookup.get(learner_key)
        if not info:
            continue
        if str(info.get("status") or "").strip().upper() != "C":
            continue
        g = _parse_grade_int(info.get("grade"))
        if g is None or not _detention_phase_allowed(phase_key, g):
            continue
        if grades_set is not None and g not in grades_set:
            continue
        try:
            bal = float(row.get("Balance") or 0)
        except (TypeError, ValueError):
            bal = 0.0
        lid = str(info.get("id") or "").strip()
        if not lid:
            continue
        out.append(
            {
                "id": lid,
                "fname": str(info.get("name") or ""),
                "sname": str(info.get("surname") or ""),
                "grade": str(info.get("grade") or ""),
                "balance": bal,
            }
        )
    return out


def _fetch_demerit_rows_for_learners(learner_ids: list[str], year: str, chunk_size: int = 80) -> dict[str, list[dict]]:
    """Map learner key -> discipline rows (normalized keys) for Communication / admin tools."""
    ids = [str(x).strip() for x in (learner_ids or []) if str(x).strip()]
    if not ids:
        return {}
    y = str(year or "").strip()
    out: dict[str, list[dict]] = {}
    for i in range(0, len(ids), max(1, int(chunk_size))):
        chunk = ids[i : i + max(1, int(chunk_size))]
        ph = "(" + ",".join(["?"] * len(chunk)) + ")"
        try:
            q = f"""
                SELECT dr.*, CSTR(li.[ID]) AS LearnerIDText, CSTR(li.[LearnerID]) AS AccessionText
                FROM DisciplinaryRecords dr
                LEFT JOIN Learner_Info li ON CSTR(li.[ID]) = CSTR(dr.Learnerid) OR CSTR(li.[LearnerID]) = CSTR(dr.Learnerid)
                WHERE CSTR(dr.Datayear) = ? AND (CSTR(dr.Learnerid) IN {ph} OR CSTR(li.[ID]) IN {ph})
            """
            params = tuple([y] + chunk + chunk)
            rows = mdb_conn.execute_query(q, params) or []
        except Exception:
            try:
                q2 = f"""
                    SELECT * FROM DisciplinaryRecords dr
                    WHERE CSTR(dr.Datayear) = ? AND CSTR(dr.Learnerid) IN {ph}
                """
                rows = mdb_conn.execute_query(q2, tuple([y] + chunk)) or []
            except Exception:
                rows = []
        for r in rows:
            lid_raw = str(r.get("Learnerid") or r.get("LearnerID") or r.get("learnerid") or "").strip()
            candidates = set(get_learner_match_candidates(lid_raw))
            for lk in list(candidates) + chunk:
                if lk in chunk or lk in ids:
                    candidates.add(lk)
            if not candidates:
                continue
            misconduct = ""
            for k in r:
                if str(k).lower() == "misconductdescription":
                    misconduct = str(r.get(k) or "")
                    break
            level = ""
            for k in r:
                if str(k).lower() == "levelmisconduct":
                    level = str(r.get(k) or "")
                    break
            auth = ""
            for k in r:
                if str(k).lower() == "authorisedby":
                    auth = str(r.get(k) or "")
                    break
            incident_dt = r.get("IncidentDate") or r.get("Date") or r.get("incidentdate")
            dem = r.get("Demerit") if r.get("Demerit") is not None else r.get("demerit")
            mer = r.get("Merit") if r.get("Merit") is not None else r.get("merit")
            shaped = {
                "MisconductDescription": misconduct,
                "LevelMisconduct": level,
                "AuthorisedBy": auth,
                "IncidentDate": incident_dt,
                "Demerit": dem,
                "Merit": mer,
            }
            for target in candidates:
                if target in ids:
                    out.setdefault(target, []).append(shaped)
                    break
            else:
                out.setdefault(lid_raw or chunk[0], []).append(shaped)
    return out


def _get_parent_phones_from_mdb(learner_ids: list[str]) -> list[tuple[str, str]]:
    """Return (e164_phone, parent_display_name) pairs for messaging (best-effort)."""
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for lid in learner_ids or []:
        row = _mdb_get_parent_profile_row(str(lid).strip())
        if not row:
            continue
        name = " ".join(
            x for x in (str(row.get("Title") or "").strip(), str(row.get("FName") or "").strip(), str(row.get("SName") or "").strip()) if x
        ).strip() or "Parent"
        for col in ("Tel1", "Tel2", "Tel3", "SpouseCell", "WorkTel"):
            raw = row.get(col)
            if raw is None or str(raw).strip() == "":
                continue
            try:
                p = normalize_phone(str(raw))
            except Exception:
                continue
            if not is_valid_phone(p):
                continue
            if p in seen:
                continue
            seen.add(p)
            pairs.append((p, name))
    return pairs


def _finance_payload_for_learner(*, learner_id: str, target_year: int) -> dict | None:
    """Outstanding fee summary for finance messages; None if unavailable."""
    ident = str(learner_id or "").strip()
    if not ident:
        return None
    y = str(int(target_year))

    info = fetch_learner_info_by_id(ident) or {}
    grade = str(info.get("grade") or "").strip()
    annual_fee = _finance_fee_amount_for_grade(grade, y)

    # Build candidate account keys for DebtorsTrans.DebAcc.
    # DebAcc can match: Learner_Info.ID, LearnerID, or AccessionNo
    cand_keys: set[str] = set()
    cand_keys.add(_mdb_norm_debtor_key(ident))
    # Add the internal ID if fetch_learner_info_by_id resolved to a different key
    internal_id = str(info.get("id") or "").strip()
    if internal_id and internal_id != ident:
        cand_keys.add(_mdb_norm_debtor_key(internal_id))
    for raw in (str(info.get("learner_id") or "").strip(),):
        if raw:
            cand_keys.add(_mdb_norm_debtor_key(raw))
            if raw.isdigit():
                cand_keys.add(str(int(raw)))
    try:
        acc_rows = mdb_conn.execute_query(
            "SELECT [AccessionNo] FROM Learner_Info WHERE CSTR([ID]) = ? AND [AccessionNo] IS NOT NULL AND [AccessionNo] <> ''",
            (internal_id or ident,),
        ) or []
        if acc_rows:
            acc = _mdb_norm_debtor_key(str(acc_rows[0].get("AccessionNo") or ""))
            if acc:
                cand_keys.add(acc)
    except Exception:
        pass

    # Fetch all DebtorsTrans transactions for this year
    total_debit = 0.0
    total_credit = 0.0
    transactions: list[dict] = []
    try:
        parts = " OR ".join([f"CSTR([DebAcc]) = ?"] * len(cand_keys))
        rows = mdb_conn.execute_query(
            f"""
            SELECT [DebAcc], [DebitAmount], [CreditAmt], [Desc], [Date], [Year], [TransID]
            FROM DebtorsTrans
            WHERE CSTR([Year]) = ? AND ({parts})
            ORDER BY [Date] ASC
            """,
            tuple([y] + sorted(cand_keys)),
        ) or []
        for tr in rows:
            d_amt = float(tr.get("DebitAmount") or 0)
            c_amt = float(tr.get("CreditAmt") or 0)
            total_debit += d_amt
            total_credit += c_amt
            transactions.append({
                "Date": tr.get("Date") or "",
                "Description": tr.get("Desc") or "",
                "Debit": d_amt,
                "Credit": c_amt,
                "Year": tr.get("Year") or y,
            })
    except Exception:
        pass

    # Also fetch discount/journal entries from Journals table (keyed by Dept)
    try:
        j_parts = " OR ".join([f"CSTR([Dept]) = ?"] * len(cand_keys))
        j_rows = mdb_conn.execute_query(
            f"""
            SELECT [Date], [Description], [DebitAmount], [CreditAmount], [Year], [JournalNumber]
            FROM Journals
            WHERE CSTR([Year]) = ? AND ({j_parts})
            ORDER BY [Date] ASC
            """,
            tuple([y] + sorted(cand_keys)),
        ) or []
        for jr in j_rows:
            d_amt = float(jr.get("DebitAmount") or 0)
            c_amt = float(jr.get("CreditAmount") or 0)
            if d_amt == 0 and c_amt == 0:
                continue
            total_debit += d_amt
            total_credit += c_amt
            transactions.append({
                "Date": jr.get("Date") or "",
                "Description": str(jr.get("Description") or ""),
                "Debit": d_amt,
                "Credit": c_amt,
                "Year": jr.get("Year") or y,
            })
    except Exception:
        pass

    # Compute balance: use annual fee as the expected debit when no debits exist
    if total_debit <= 0:
        balance = annual_fee - total_credit
    else:
        balance = total_debit - total_credit
    outstanding = max(0.0, balance)
    return {
        "annualFee": annual_fee,
        "totalOwed": total_debit,
        "totalPaid": total_credit,
        "balance": balance,
        "outstanding": outstanding,
        "currentYearBalance": balance,
        "isPaid": balance <= 0.01,
        "status": "Paid" if balance <= 0.01 else "Outstanding",
        "transactions": transactions,
        "grade": grade,
        "currentYear": int(target_year),
    }


def _mdb_norm_debtor_key(raw) -> str:
    """Normalize a debtor key by stripping trailing '.0' if present."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if len(s) > 2 and s.endswith(".0") and s[:-2].replace("-", "").isdigit():
        s = s[:-2]
    return s


def _finance_fee_amount_for_grade(grade, fee_year: str) -> float:
    """Resolve annual school fee for a grade from the Fees table."""
    g = str(grade or "").strip()
    if not g:
        return 0.0
    try:
        rows = mdb_conn.execute_query("SELECT [Fees] FROM [Fees] WHERE [Grade] = ? AND [Year] = ?", (g, str(fee_year))) or []
        if rows:
            return float(rows[0].get("Fees") or 0)
        rows = mdb_conn.execute_query("SELECT TOP 1 [Fees] FROM [Fees] WHERE [Grade] = ? ORDER BY [Year] DESC", (g,)) or []
        if rows:
            return float(rows[0].get("Fees") or 0)
    except Exception:
        pass
    return 11900.0


def _finance_parent_names_map(child_ids: list[str]) -> dict[str, str]:
    """Map Learner_Info.ID (string) to best-effort parent/guardian display name."""
    out: dict[str, str] = {}
    ids = [str(x).strip() for x in child_ids if str(x).strip()]
    if not ids:
        return out
    placeholders = ",".join(["?"] * len(ids))
    params = tuple(int(x) if x.isdigit() else x for x in ids)
    for col in ("ChildId", "ChildID"):
        try:
            q = (
                f"SELECT pc.[{col}] AS CID, pi.[FName], pi.[SName], pi.[SpouseFname], pi.[Spouse] "
                f"FROM Parent_Info pi INNER JOIN Parent_Child pc ON pc.[ParentId] = pi.[ParentID] "
                f"WHERE pc.[{col}] IN ({placeholders})"
            )
            rows = mdb_conn.execute_query(q, params) or []
            for r in rows:
                cid = r.get("CID")
                if cid is None:
                    continue
                sn = str(r.get("SName") or "").strip()
                fn = str(r.get("FName") or "").strip()
                sf = str(r.get("SpouseFname") or "").strip()
                sp = str(r.get("Spouse") or "").strip()
                if fn and sn:
                    out[str(cid)] = f"{fn} {sn}"
                elif sf and sp:
                    out[str(cid)] = f"{sf} {sp}"
                elif fn:
                    out[str(cid)] = fn
                elif sf:
                    out[str(cid)] = sf
        except Exception:
            continue
    return out


# Routes
@app.route('/')
def index():
    # Get active slideshow images
    slideshow_images = SlideshowImage.query.filter_by(is_active=True).order_by(SlideshowImage.display_order).all()
    return render_template('index.html', slideshow_images=slideshow_images)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        if current_user.username == ADMIN_USERNAME:
            return redirect(url_for('admin_dashboard'))
        if is_teacher_user(current_user):
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        # Check for admin credentials first
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Find or create admin user
            admin_user = User.query.filter_by(username=ADMIN_USERNAME).first()
            if not admin_user:
                # Create admin user if it doesn't exist
                admin_user = User(
                    username=ADMIN_USERNAME,
                    password_hash=generate_password_hash(ADMIN_PASSWORD),
                    learner_id='ADMIN',  # Special ID for admin
                    first_login=False,
                    dashboard_token=None  # NULL since we're not using tokens anymore
                )
                db.session.add(admin_user)
                db.session.commit()
            
            login_user(admin_user)
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Parent login uses phone; legacy uses username.
        raw = str(username).strip()
        phone = normalize_phone(raw)
        user = None
        if is_valid_phone(raw):
            # Normalize to E.164 and try a few variants just in case older records were stored differently.
            variants = phone_lookup_variants(raw)
            for v in variants:
                user = User.query.filter_by(phone=normalize_phone(v)).first()
                if user:
                    break
        if not user:
            user = User.query.filter_by(username=raw).first()

        educator_identity = resolve_teacher_identity(identifier=raw, phone=raw)
        if educator_identity:
            teacher_user = get_or_create_teacher_user(educator_identity)
            if teacher_user and teacher_user.first_login:
                session["teacher_bootstrap_id"] = educator_identity["educator_id"]
                flash('Complete first-time teacher setup to verify OTP and create your password.', 'success')
                return redirect(url_for('teacher_bootstrap'))
            user = teacher_user or user
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            # Check if first login
            if user.first_login:
                return redirect(url_for('reset_password'))
            
            # Log access
            access = DashboardAccess(user_id=user.id)
            db.session.add(access)
            db.session.commit()
            
            flash('Login successful!', 'success')
            if is_manager_user(user):
                # Managers can choose which portal to use after login.
                # Default to parent (restricted) until they pick Management Portal.
                session["portal_mode"] = "parent"
                return redirect(url_for('portal_select'))
            if is_teacher_user(user):
                session["portal_mode"] = "teacher"
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


def find_user_by_phone_identifier(raw_phone: str):
    """Resolve a user by phone using normalized variants."""
    raw_phone = str(raw_phone or "").strip()
    if not raw_phone:
        return None
    variants = phone_lookup_variants(raw_phone)
    for variant in variants:
        user = User.query.filter_by(phone=normalize_phone(variant)).first()
        if user:
            return user
    return None


def normalize_educator_id(raw) -> str:
    return str(raw or "").strip().upper()


def _digits_only(value: str) -> str:
    return re.sub(r"\D+", "", str(value or ""))


def _phone_digit_variants(raw_phone: str) -> set[str]:
    out = set()
    for v in phone_lookup_variants(raw_phone):
        d = _digits_only(v)
        if d:
            out.add(d)
            if len(d) >= 9:
                out.add(d[-9:])
    d0 = _digits_only(raw_phone)
    if d0:
        out.add(d0)
        if len(d0) >= 9:
            out.add(d0[-9:])
    return out


def _looks_phone_column(name: str) -> bool:
    n = str(name or "").strip().lower()
    return any(k in n for k in ("cell", "phone", "tel", "mobile", "contact", "whatsapp"))


def _row_phone_matches(row: dict, phone_digits_variants: set[str]) -> bool:
    for k, v in (row or {}).items():
        if not _looks_phone_column(k):
            continue
        d = _digits_only(v)
        if not d:
            continue
        if d in phone_digits_variants:
            return True
        if len(d) >= 9 and d[-9:] in phone_digits_variants:
            return True
    return False


def get_educator_identity_by_edid(edid_raw: str):
    edid = normalize_educator_id(edid_raw)
    if not edid:
        return None
    rows = []
    try:
        row = mdb_repo.educator_by_edid(edid)
        if row:
            rows = [row]
    except Exception:
        rows = []
    if not rows:
        rows = mdb_conn.execute_query(
            """
            SELECT TOP 1 [EdID], [FName], [SName], [Actual], [Status], [RegisterClass]
            FROM [Educators]
            WHERE UCASE(CSTR([EdID])) = ?
            """,
            (edid,),
        ) or []
    if not rows:
        return None
    row = rows[0]
    role = str(row.get("Actual") or "Teacher").strip()
    status = str(row.get("Status") or "Active").strip() or "Active"
    first = str(row.get("FName") or "").strip()
    surname = str(row.get("SName") or "").strip()
    return {
        "educator_id": normalize_educator_id(row.get("EdID")),
        "first_name": first,
        "surname": surname,
        "display_name": " ".join([x for x in (first, surname) if x]).strip() or normalize_educator_id(row.get("EdID")),
        "role": role if role else "Teacher",
        "status": status,
        "register_class": str(row.get("RegisterClass") or "").strip(),
    }


def get_staff_identity_by_staffid(staff_id_raw: str):
    staff_id = str(staff_id_raw or "").strip()
    if not staff_id:
        return None
    rows = []
    try:
        row = mdb_repo.staff_by_staffid(staff_id)
        if row:
            rows = [row]
    except Exception:
        rows = []
    if not rows:
        rows = mdb_conn.execute_query(
            """
            SELECT TOP 1 [StaffID], [FName], [SName], [PersonnelCategory], [Status]
            FROM [StaffMembers]
            WHERE CSTR([StaffID]) = ?
            """,
            (staff_id,),
        ) or []
    if not rows:
        return None
    r = rows[0]
    sid = str(r.get("StaffID", "") or "").strip()
    first = str(r.get("FName") or "").strip()
    surname = str(r.get("SName") or "").strip()
    return {
        "educator_id": f"S-{sid}",
        "first_name": first,
        "surname": surname,
        "display_name": " ".join([x for x in (first, surname) if x]).strip() or f"Staff {sid}",
        "role": str(r.get("PersonnelCategory") or "Teacher").strip() or "Teacher",
        "status": str(r.get("Status") or "Active").strip() or "Active",
        "register_class": "",
    }


_STAFF_MEMBERS_PHONE_COLS_CACHE: list[str] | None = None


def _staff_members_phone_columns() -> list[str]:
    """Phone-like columns on public StaffMembers (uses quoted PascalCase in PostgreSQL)."""
    global _STAFF_MEMBERS_PHONE_COLS_CACHE
    if _STAFF_MEMBERS_PHONE_COLS_CACHE is not None:
        return _STAFF_MEMBERS_PHONE_COLS_CACHE
    out: list[str] = []
    try:
        insp = inspect(db.engine)
        for tname in ("StaffMembers", "staffmembers"):
            try:
                cols = insp.get_columns(tname, schema="public")
            except Exception:
                cols = []
            if cols:
                for c in cols:
                    name = str(c.get("name") or "")
                    if _looks_phone_column(name):
                        out.append(name)
                break
    except Exception:
        out = []
    _STAFF_MEMBERS_PHONE_COLS_CACHE = out
    return out


def get_staff_identity_by_phone(phone_raw: str, first_name: str = "", surname: str = ""):
    """
    Attempt non-educator onboarding from StaffMembers using flexible phone columns.
    Falls back to name-only match when phone columns are unavailable.
    """
    phone_digits_variants = _phone_digit_variants(phone_raw)
    first_upper = str(first_name or "").strip().upper()
    surname_upper = str(surname or "").strip().upper()
    phone_variants = phone_lookup_variants(phone_raw)

    # PostgreSQL: probe columns discovered via metadata (no guessed lowercase names).
    for col in _staff_members_phone_columns():
        safe = col.replace('"', '""')
        sql = text(
            f'SELECT "StaffID", "FName", "SName", "PersonnelCategory", "Status" '
            f'FROM "StaffMembers" WHERE CAST("{safe}" AS TEXT) = :p LIMIT 1'
        )
        for p in phone_variants:
            try:
                row = db.session.execute(sql, {"p": str(p)}).mappings().first()
            except Exception:
                row = None
            if not row:
                continue
            r = dict(row)
            expand_legacy_row_key_aliases(r)
            sid = str(r.get("StaffID") or "").strip()
            if not sid:
                continue
            fn = str(r.get("FName") or "").strip()
            sn = str(r.get("SName") or "").strip()
            return {
                "educator_id": f"S-{sid}",
                "first_name": fn,
                "surname": sn,
                "display_name": " ".join([x for x in (fn, sn) if x]).strip() or f"Staff {sid}",
                "role": str(r.get("PersonnelCategory") or "Teacher").strip() or "Teacher",
                "status": str(r.get("Status") or "Active").strip() or "Active",
                "register_class": "",
            }

    # Fallback: scan rows via compat driver (Access / translated LIMIT).
    try:
        rows = mdb_conn.execute_query("SELECT TOP 5000 * FROM StaffMembers") or []
        for r in rows:
            if not _row_phone_matches(r, phone_digits_variants):
                continue
            sid = str(r.get("StaffID", "") or "").strip()
            if not sid:
                continue
            return {
                "educator_id": f"S-{sid}",
                "first_name": str(r.get("FName") or "").strip(),
                "surname": str(r.get("SName") or "").strip(),
                "display_name": " ".join([str(r.get("FName") or "").strip(), str(r.get("SName") or "").strip()]).strip() or f"Staff {sid}",
                "role": str(r.get("PersonnelCategory") or "Teacher").strip() or "Teacher",
                "status": str(r.get("Status") or "Active").strip() or "Active",
                "register_class": "",
            }
    except Exception:
        pass

    if first_upper and surname_upper:
        try:
            rows = mdb_conn.execute_query(
                """
                SELECT TOP 1 [StaffID], [FName], [SName], [PersonnelCategory], [Status]
                FROM StaffMembers
                WHERE UCASE([FName]) = ? AND UCASE([SName]) = ?
                """,
                (first_upper, surname_upper),
            ) or []
            if rows:
                r = rows[0]
                sid = str(r.get("StaffID", "") or "").strip()
                return {
                    "educator_id": f"S-{sid}",
                    "first_name": str(r.get("FName") or "").strip(),
                    "surname": str(r.get("SName") or "").strip(),
                    "display_name": " ".join([str(r.get("FName") or "").strip(), str(r.get("SName") or "").strip()]).strip() or f"Staff {sid}",
                    "role": str(r.get("PersonnelCategory") or "Teacher").strip() or "Teacher",
                    "status": str(r.get("Status") or "Active").strip() or "Active",
                    "register_class": "",
                }
        except Exception:
            return None
    return None


def get_educator_identity_by_phone(phone_raw: str):
    phone_digits_variants = _phone_digit_variants(phone_raw)
    try:
        rows = mdb_conn.execute_query("SELECT TOP 5000 * FROM Educators") or []
        for r in rows:
            if not _row_phone_matches(r, phone_digits_variants):
                continue
            edid = normalize_educator_id(r.get("EdID"))
            if not edid:
                continue
            first = str(r.get("FName") or "").strip()
            surname = str(r.get("SName") or "").strip()
            return {
                "educator_id": edid,
                "first_name": first,
                "surname": surname,
                "display_name": " ".join([x for x in (first, surname) if x]).strip() or edid,
                "role": str(r.get("Actual") or "Teacher").strip() or "Teacher",
                "status": str(r.get("Status") or "Active").strip() or "Active",
                "register_class": str(r.get("RegisterClass") or "").strip(),
            }
    except Exception:
        return None
    return None


def resolve_teacher_identity(identifier: str = "", phone: str = "", first_name: str = "", surname: str = ""):
    identity = None
    if identifier:
        identity = get_educator_identity_by_edid(identifier)
        if not identity:
            identity = get_staff_identity_by_staffid(identifier)
    if not identity and phone:
        identity = get_educator_identity_by_phone(phone)
    if not identity and phone:
        identity = get_staff_identity_by_phone(phone, first_name=first_name, surname=surname)
    return identity


def get_or_create_teacher_user(identity: dict):
    edid = normalize_educator_id(identity.get("educator_id"))
    if not edid:
        return None
    user = User.query.filter_by(educator_id=edid).first()
    if not user:
        username = f"teacher_{edid.lower()}"
        existing = User.query.filter_by(username=username).first()
        if existing:
            username = f"{username}_{secrets.token_hex(3)}"
        user = User(
            username=username,
            password_hash=generate_password_hash(secrets.token_urlsafe(18)),
            first_login=True,
            is_teacher=True,
            educator_id=edid,
            teacher_role=str(identity.get("role") or "Teacher")[:32],
            teacher_status=str(identity.get("status") or "Active")[:32],
        )
        db.session.add(user)
        db.session.commit()
    else:
        user.is_teacher = True
        user.teacher_role = str(identity.get("role") or user.teacher_role or "Teacher")[:32]
        user.teacher_status = str(identity.get("status") or user.teacher_status or "Active")[:32]
        if not user.educator_id:
            user.educator_id = edid
        db.session.commit()
    return user


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        phone = normalize_phone(request.form.get('phone', ''))
        if not is_valid_phone(phone):
            flash('Please enter a valid cellphone number (E.164 format recommended, e.g. +2782xxxxxxx).', 'error')
            return render_template('register_phone.html')

        learner_ids = lookup_learners_by_parent_phone(phone)
        if not learner_ids:
            flash('This cellphone number was not found in our records. Please contact the school to update your details.', 'error')
            return render_template('register_phone.html')

        # Rate limit OTP issuance per phone
        existing_recent = (
            OtpChallenge.query.filter_by(phone=phone, purpose="register")
            .filter(OtpChallenge.expires_at > datetime.utcnow())
            .order_by(OtpChallenge.created_at.desc())
            .first()
        )
        if existing_recent and existing_recent.last_sent_at and (datetime.utcnow() - existing_recent.last_sent_at) < timedelta(seconds=45):
            flash('Please wait a moment before requesting another OTP.', 'error')
            return redirect(url_for('register_verify'))

        otp = f"{secrets.randbelow(1000000):06d}"
        otp_hash = generate_password_hash(otp)
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        ch = OtpChallenge(
            phone=phone,
            purpose="register",
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts_remaining=5,
            last_sent_at=datetime.utcnow(),
            send_count=(existing_recent.send_count + 1) if existing_recent else 1,
        )
        db.session.add(ch)
        db.session.commit()

        try:
            send_otp(phone, otp)
        except Exception:
            app.logger.error("OTP send failed for phone=%s", phone, exc_info=True)
            flash('We could not send an OTP right now. Please try again in a minute.', 'error')
            return render_template('register_phone.html')

        session["register_phone"] = phone
        flash('OTP sent. Please enter the code you received (WhatsApp or SMS).', 'success')
        return redirect(url_for('register_verify'))

    return render_template('register_phone.html')


@app.route('/register/verify', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def register_verify():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    phone = normalize_phone(session.get("register_phone", ""))
    if not phone:
        return redirect(url_for('register'))

    if request.method == 'POST':
        code = str(request.form.get('otp', '')).strip()
        if not re.fullmatch(r"\d{6}", code or ""):
            flash('Please enter the 6-digit OTP.', 'error')
            return render_template('register_verify.html', phone=phone)

        ch = (
            OtpChallenge.query.filter_by(phone=phone, purpose="register")
            .order_by(OtpChallenge.created_at.desc())
            .first()
        )
        if not ch or ch.expires_at <= datetime.utcnow():
            flash('OTP expired. Please request a new OTP.', 'error')
            return redirect(url_for('register'))

        if ch.verified_at is not None:
            session["register_verified"] = True
            return redirect(url_for('register_set_password'))

        if ch.attempts_remaining <= 0:
            flash('Too many incorrect attempts. Please request a new OTP.', 'error')
            return redirect(url_for('register'))

        if not check_password_hash(ch.otp_hash, code):
            ch.attempts_remaining = max(0, (ch.attempts_remaining or 0) - 1)
            db.session.commit()
            flash('Incorrect OTP. Please try again.', 'error')
            return render_template('register_verify.html', phone=phone)

        ch.verified_at = datetime.utcnow()
        db.session.commit()
        session["register_verified"] = True
        flash('OTP verified. Please create a password.', 'success')
        return redirect(url_for('register_set_password'))

    return render_template('register_verify.html', phone=phone)


@app.route('/register/set-password', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def register_set_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    phone = normalize_phone(session.get("register_phone", ""))
    verified = bool(session.get("register_verified"))
    if not phone or not verified:
        return redirect(url_for('register'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register_set_password.html', phone=phone)

        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            flash('; '.join(errors), 'error')
            return render_template('register_set_password.html', phone=phone)

        learner_ids = lookup_learners_by_parent_phone(phone)
        if not learner_ids:
            flash('We could not match your cellphone to any learners anymore. Please contact the school.', 'error')
            return redirect(url_for('register'))

        # Create or update parent user
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(
                username=f"parent_{secrets.token_hex(8)}",
                phone=phone,
                password_hash=generate_password_hash(new_password),
                first_login=False,
                learner_id=None,
                is_parent=True,
                dashboard_token=None,
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.password_hash = generate_password_hash(new_password)
            user.first_login = False
            user.is_parent = True
            db.session.commit()

        # Upsert learner links
        existing = {l.learner_id for l in UserLearner.query.filter_by(user_id=user.id).all()}
        for lid in learner_ids:
            if lid not in existing:
                db.session.add(UserLearner(user_id=user.id, learner_id=lid))
        db.session.commit()

        # Set active learner in session
        session["active_learner_id"] = learner_ids[0]

        login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register_set_password.html', phone=phone)


@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        phone = normalize_phone(request.form.get('phone', ''))
        if not is_valid_phone(phone):
            flash('Please enter a valid cellphone number (E.164 format recommended, e.g. +2782xxxxxxx).', 'error')
            return render_template('forgot_password_phone.html')

        user = find_user_by_phone_identifier(phone)
        if not user:
            flash('No account found for this cellphone number.', 'error')
            return render_template('forgot_password_phone.html')

        existing_recent = (
            OtpChallenge.query.filter_by(phone=phone, purpose="forgot_password")
            .filter(OtpChallenge.expires_at > datetime.utcnow())
            .order_by(OtpChallenge.created_at.desc())
            .first()
        )
        if existing_recent and existing_recent.last_sent_at and (datetime.utcnow() - existing_recent.last_sent_at) < timedelta(seconds=45):
            flash('Please wait a moment before requesting another OTP.', 'error')
            return redirect(url_for('forgot_password_verify'))

        otp = f"{secrets.randbelow(1000000):06d}"
        otp_hash = generate_password_hash(otp)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        ch = OtpChallenge(
            phone=phone,
            purpose="forgot_password",
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts_remaining=5,
            last_sent_at=datetime.utcnow(),
            send_count=(existing_recent.send_count + 1) if existing_recent else 1,
        )
        db.session.add(ch)
        db.session.commit()

        try:
            send_otp(phone, otp)
        except Exception:
            app.logger.error("Forgot-password OTP send failed for phone=%s", phone, exc_info=True)
            flash('We could not send an OTP right now. Please try again in a minute.', 'error')
            return render_template('forgot_password_phone.html')

        session["forgot_phone"] = phone
        session["forgot_verified"] = False
        flash('OTP sent. Please enter the code you received (WhatsApp or SMS).', 'success')
        return redirect(url_for('forgot_password_verify'))

    return render_template('forgot_password_phone.html')


@app.route('/forgot-password/verify', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def forgot_password_verify():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    phone = normalize_phone(session.get("forgot_phone", ""))
    if not phone:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        code = str(request.form.get('otp', '')).strip()
        if not re.fullmatch(r"\d{6}", code or ""):
            flash('Please enter the 6-digit OTP.', 'error')
            return render_template('forgot_password_verify.html', phone=phone)

        ch = (
            OtpChallenge.query.filter_by(phone=phone, purpose="forgot_password")
            .order_by(OtpChallenge.created_at.desc())
            .first()
        )
        if not ch or ch.expires_at <= datetime.utcnow():
            flash('OTP expired. Please request a new OTP.', 'error')
            return redirect(url_for('forgot_password'))

        if ch.verified_at is not None:
            session["forgot_verified"] = True
            return redirect(url_for('forgot_password_set_password'))

        if ch.attempts_remaining <= 0:
            flash('Too many incorrect attempts. Please request a new OTP.', 'error')
            return redirect(url_for('forgot_password'))

        if not check_password_hash(ch.otp_hash, code):
            ch.attempts_remaining = max(0, (ch.attempts_remaining or 0) - 1)
            db.session.commit()
            flash('Incorrect OTP. Please try again.', 'error')
            return render_template('forgot_password_verify.html', phone=phone)

        ch.verified_at = datetime.utcnow()
        db.session.commit()
        session["forgot_verified"] = True
        flash('OTP verified. Please set a new password.', 'success')
        return redirect(url_for('forgot_password_set_password'))

    return render_template('forgot_password_verify.html', phone=phone)


@app.route('/forgot-password/set-password', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def forgot_password_set_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    phone = normalize_phone(session.get("forgot_phone", ""))
    verified = bool(session.get("forgot_verified"))
    if not phone or not verified:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('forgot_password_set_password.html', phone=phone)

        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            flash('; '.join(errors), 'error')
            return render_template('forgot_password_set_password.html', phone=phone)

        user = find_user_by_phone_identifier(phone)
        if not user:
            flash('No account found for this cellphone number.', 'error')
            session.pop("forgot_phone", None)
            session.pop("forgot_verified", None)
            return redirect(url_for('forgot_password'))

        user.password_hash = generate_password_hash(new_password)
        user.first_login = False
        db.session.commit()

        session.pop("forgot_phone", None)
        session.pop("forgot_verified", None)

        flash('Password updated successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password_set_password.html', phone=phone)


@app.route('/reset-password', methods=['GET', 'POST'])
@login_required
def reset_password():
    user = current_user
    
    if not user.first_login:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html')
        
        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            flash('; '.join(errors), 'error')
            return render_template('reset_password.html')
        
        user.password_hash = generate_password_hash(new_password)
        user.first_login = False
        db.session.commit()
        
        flash('Password reset successfully. Please login again.', 'success')
        logout_user()
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    if is_teacher_user(user) and session.get("portal_mode") == "teacher":
        return redirect(url_for('teacher_dashboard'))
    # Managers can directly hit `/dashboard`, but this should always behave like the Parent Portal.
    if is_manager_user(user):
        session["portal_mode"] = "parent"
    user_is_analytics = is_analytics_user(user)
    active_learner_id = get_active_learner_id_for_request(user)
    linked_ids = get_linked_learner_ids_for_user(user)
    linked_learners = []
    for lid in linked_ids:
        info = fetch_learner_info_by_id(lid)
        if info:
            linked_learners.append(info)
        else:
            linked_learners.append({"id": lid, "learner_id": lid, "name": "", "surname": "", "grade": ""})

    learner_info = fetch_learner_info_by_id(active_learner_id) if active_learner_id else None
    if user_is_analytics:
        learner_info = {
            "id": "ALL",
            "learner_id": "ALL",
            "name": "All",
            "surname": "Learners",
            "grade": "All Grades",
        }
    elif not active_learner_id:
        flash('No learners are linked to your account. Please contact the school.', 'error')
    return render_template('dashboard.html', user=user, learner_info=learner_info, linked_learners=linked_learners, active_learner_id=active_learner_id)


@app.route("/dashboard/select-learner", methods=["POST"])
@login_required
def select_learner():
    """Switch active child for parent dashboard (multi-learner accounts)."""
    want = str(request.form.get("learner_id") or "").strip()
    linked = get_linked_learner_ids_for_user(current_user)
    linked_set = {str(x).strip() for x in linked if x}
    if want and want in linked_set:
        session["active_learner_id"] = want
    else:
        flash("That learner is not linked to your account.", "error")
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/portals")
@login_required
def portal_select():
    if not is_manager_user(current_user):
        return redirect(url_for("dashboard"))
    return render_template("portal_select.html")


@app.route("/portals/parent", methods=["POST"])
@login_required
def choose_parent_portal():
    if not is_manager_user(current_user):
        return redirect(url_for("dashboard"))
    session["portal_mode"] = "parent"
    flash("Using Parent Dashboard (restricted view).", "success")
    return redirect(url_for("dashboard"))


@app.route("/portals/management", methods=["POST"])
@login_required
def choose_management_portal():
    if not is_manager_user(current_user):
        return redirect(url_for("dashboard"))
    session["portal_mode"] = "management"
    flash("Using Management Portal.", "success")
    return redirect(url_for("management_dashboard"))


@app.route("/portals/teacher", methods=["POST"])
@login_required
def choose_teacher_portal():
    if not is_teacher_user(current_user):
        flash("Teacher portal is not available for this account.", "error")
        return redirect(url_for("portal_select"))
    session["portal_mode"] = "teacher"
    flash("Using Teacher Portal.", "success")
    return redirect(url_for("teacher_dashboard"))


@app.route("/teacher")
@login_required
def teacher_dashboard():
    if not is_teacher_user(current_user):
        flash("Teacher portal is only for educator accounts.", "error")
        return redirect(url_for("dashboard"))
    session["portal_mode"] = "teacher"
    return render_template("teacher/dashboard.html", teacher_scope={})


@app.route("/announcements")
@login_required
def announcements_page():
    """School-wide announcements page for all users."""
    return render_template("announcements.html")


@app.route("/teacher/announcements")
@login_required
def teacher_announcements_page():
    """Teacher announcement management page."""
    if not is_teacher_user(current_user):
        flash("Teacher portal is only for educator accounts.", "error")
        return redirect(url_for("dashboard"))
    session["portal_mode"] = "teacher"
    return render_template("teacher/announcements.html")


# ---------------------------------------------------------------------------
# Teacher Portal — Page routes
# ---------------------------------------------------------------------------
@app.route("/teacher/classes")
@login_required
def teacher_classes_page():
    """Teacher classes/roster page."""
    if not is_teacher_user(current_user):
        abort(403)
    session["portal_mode"] = "teacher"
    return render_template("teacher/classes.html")


@app.route("/teacher/attendance")
@login_required
def teacher_attendance_page():
    """Teacher attendance page."""
    if not is_teacher_user(current_user):
        abort(403)
    session["portal_mode"] = "teacher"
    return render_template("teacher/attendance.html")


# ---------------------------------------------------------------------------
# Teacher Portal — API routes
# ---------------------------------------------------------------------------
@app.route("/api/teacher/dashboard")
@login_required
def api_teacher_dashboard():
    """Return KPI data for the teacher dashboard."""
    if not is_teacher_user(current_user):
        abort(403)
    uid = current_user.id

    # Count assigned classes and distinct grades from UserTeacherAssignment
    assignments = UserTeacherAssignment.query.filter_by(
        user_id=uid, is_active=True
    ).all()
    assigned_classes = len(set(a.class_id for a in assignments if a.class_id))
    assigned_grades = len(set(a.grade for a in assignments if a.grade))

    # Learner count — approximate from MDB
    learner_count = 0
    try:
        rows = mdb_conn.execute_query(
            "SELECT COUNT(*) AS cnt FROM [Learner_Info]"
        )
        if rows:
            learner_count = int(rows[0].get("cnt", 0) or 0)
    except Exception:
        pass

    # Pending attendance — count from Absentees in current year
    pending_attendance = 0
    try:
        rows = mdb_conn.execute_query(
            "SELECT COUNT(*) AS cnt FROM [Absentees] WHERE [Datayear] = ?",
            (str(datetime.now().year),),
        )
        if rows:
            pending_attendance = int(rows[0].get("cnt", 0) or 0)
    except Exception:
        pass

    # Pending assessments — count from ReportMarks in current year
    pending_assessments = 0
    try:
        mark_rows = mdb_conn.execute_query(
            "SELECT COUNT(*) AS cnt FROM [ReportMarks] WHERE [Datayear] = ?",
            (str(datetime.now().year),),
        )
        if mark_rows:
            pending_assessments = int(mark_rows[0].get("cnt", 0) or 0)
    except Exception:
        pass

    # Recent discipline — count from DisciplinaryLearnerMisconduct
    recent_discipline = 0
    try:
        disc_rows = mdb_conn.execute_query(
            "SELECT COUNT(*) AS cnt FROM [DisciplinaryLearnerMisconduct]"
        )
        if disc_rows:
            recent_discipline = int(disc_rows[0].get("cnt", 0) or 0)
    except Exception:
        pass

    return jsonify({
        "kpis": {
            "assignedClasses": assigned_classes,
            "assignedGrades": assigned_grades,
            "learnerCount": learner_count,
            "pendingAttendance": pending_attendance,
            "pendingAssessments": pending_assessments,
            "recentDiscipline": recent_discipline,
        }
    })


@app.route("/api/teacher/classes")
@login_required
def api_teacher_classes():
    """Return the current teacher's class/subject assignments."""
    if not is_teacher_user(current_user):
        abort(403)
    assignments = UserTeacherAssignment.query.filter_by(
        user_id=current_user.id, is_active=True
    ).all()
    return jsonify({
        "assignments": [
            {
                "classId": a.class_id or "",
                "grade": a.grade or "",
                "subject": a.subject or "",
                "academicYear": a.academic_year or "",
            }
            for a in assignments
        ]
    })


@app.route("/api/teacher/roster")
@login_required
def api_teacher_roster():
    """Return learners filtered by grade and/or class_id for roster view."""
    if not is_teacher_user(current_user):
        abort(403)
    grade = request.args.get("grade", "").strip()
    class_id = request.args.get("class_id", "").strip()

    sql = "SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class] FROM [Learner_Info] WHERE 1=1"
    params: list[str] = []
    if grade:
        sql += " AND CSTR([Grade]) = ?"
        params.append(grade)
    if class_id:
        sql += " AND CSTR([Class]) = ?"
        params.append(class_id)

    try:
        rows = mdb_conn.execute_query(sql, tuple(params)) or []
    except Exception:
        rows = []

    return jsonify({
        "learners": [
            {
                "learnerId": str(r.get("LearnerID", r.get("ID", "")) or ""),
                "name": str(r.get("FName", "") or ""),
                "surname": str(r.get("SName", "") or ""),
                "grade": str(r.get("Grade", "") or ""),
                "classId": str(r.get("Class", "") or ""),
            }
            for r in rows
        ]
    })


@app.route("/api/teacher/attendance")
@login_required
def api_teacher_attendance():
    """Return attendance records."""
    if not is_teacher_user(current_user):
        abort(403)
    sql = (
        "SELECT TOP 200 [Learnerid], [DateAbsent], [Grade], [Class], [ReasonOther] "
        "FROM [Absentees] ORDER BY [DateAbsent] DESC"
    )
    try:
        rows = mdb_conn.execute_query(sql) or []
    except Exception:
        rows = []
    return jsonify({"rows": rows})


@app.route("/api/teacher/discipline")
@login_required
def api_teacher_discipline():
    """Return discipline records."""
    if not is_teacher_user(current_user):
        abort(403)
    sql = (
        "SELECT TOP 200 [Date], [Learnerid], [Type], [Demerit], [Merit], [Comment] "
        "FROM [DisciplinaryLearnerMisconduct] ORDER BY [Date] DESC"
    )
    try:
        rows = mdb_conn.execute_query(sql) or []
    except Exception:
        rows = []
    return jsonify({"rows": rows})


@app.route("/api/teacher/assessments")
@login_required
def api_teacher_assessments():
    """Return assessment records and available subjects."""
    if not is_teacher_user(current_user):
        abort(403)
    # Fetch assessment rows
    sql = (
        "SELECT TOP 200 [LearnerID], [SubjectId], [SubjectName], [Mark], [TotalMark], [Datayear], [ReportId] "
        "FROM [ReportMarks] ORDER BY [Datayear] DESC"
    )
    try:
        rows = mdb_conn.execute_query(sql) or []
    except Exception:
        rows = []

    # Fetch subjects for dropdown
    subjects_sql = "SELECT [ID], [Name] FROM [Subjects]"
    try:
        subjects = mdb_conn.execute_query(subjects_sql) or []
    except Exception:
        subjects = []

    return jsonify({
        "rows": rows,
        "subjects": [{"Id": str(s.get("ID", "") or ""), "Name": str(s.get("Name", "") or "")} for s in subjects],
    })


@app.route("/api/teacher/reports/export")
@login_required
def api_teacher_reports_export():
    """Export a CSV report of learners with attendance, discipline, and assessment counts for the teacher's scope."""
    if not is_teacher_user(current_user):
        abort(403)
    academic_year = request.args.get("academic_year", "").strip() or str(datetime.now().year)
    grade = request.args.get("grade", "").strip()
    class_id = request.args.get("class_id", "").strip()

    # Build learner query
    sql = "SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class] FROM [Learner_Info] WHERE 1=1"
    params: list[str] = []
    if grade:
        sql += " AND CSTR([Grade]) = ?"
        params.append(grade)
    if class_id:
        sql += " AND CSTR([Class]) = ?"
        params.append(class_id)

    try:
        learners = mdb_conn.execute_query(sql, tuple(params)) or []
    except Exception:
        learners = []

    import csv
    from io import StringIO

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["LearnerID", "Name", "Surname", "Grade", "Class", "AttendanceCount", "DisciplineCount", "AssessmentCount"])

    for l in learners:
        lid = str(l.get("LearnerID", l.get("ID", "")) or "")
        # Attendance count for this learner
        att_count = 0
        try:
            ar = mdb_conn.execute_query(
                "SELECT COUNT(*) AS cnt FROM [Absentees] WHERE CSTR([Learnerid]) = ? AND CSTR([Datayear]) = ?",
                (lid, academic_year),
            )
            if ar:
                att_count = int(ar[0].get("cnt", 0) or 0)
        except Exception:
            pass

        # Discipline count
        disc_count = 0
        try:
            dr = mdb_conn.execute_query(
                "SELECT COUNT(*) AS cnt FROM [DisciplinaryLearnerMisconduct] WHERE CSTR([Learnerid]) = ?",
                (lid,),
            )
            if dr:
                disc_count = int(dr[0].get("cnt", 0) or 0)
        except Exception:
            pass

        # Assessment count
        asm_count = 0
        try:
            ar2 = mdb_conn.execute_query(
                "SELECT COUNT(*) AS cnt FROM [ReportMarks] WHERE CSTR([LearnerID]) = ? AND CSTR([Datayear]) = ?",
                (lid, academic_year),
            )
            if ar2:
                asm_count = int(ar2[0].get("cnt", 0) or 0)
        except Exception:
            pass

        cw.writerow([
            lid,
            str(l.get("FName", "") or ""),
            str(l.get("SName", "") or ""),
            str(l.get("Grade", "") or ""),
            str(l.get("Class", "") or ""),
            att_count,
            disc_count,
            asm_count,
        ])

    csv_output = si.getvalue()
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=teacher_report_{academic_year}.csv"},
    )


@app.route("/api/teacher/messages/send", methods=["POST"])
@login_required
def api_teacher_messages_send():
    """Send a chat message. Creates a thread if needed."""
    if not is_teacher_user(current_user):
        abort(403)

    recipient_id = request.form.get("recipient_id", "").strip()
    learner_id = request.form.get("learner_id", "").strip()
    body = request.form.get("body", "").strip()
    thread_id = request.form.get("thread_id", "").strip()
    idempotency_key = request.form.get("idempotency_key", "").strip()

    if not body:
        return jsonify({"error": "Message body is required."}), 400

    # Idempotency check
    if idempotency_key:
        existing = TeacherWriteEvent.query.filter_by(
            user_id=current_user.id,
            module="messages_send",
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return jsonify({"message": "Already sent.", "idempotent": True})

    # Resolve thread
    thread = None
    if thread_id:
        thread = ChatThread.query.get(int(thread_id))
    elif recipient_id:
        # Look for existing direct thread between these two users + learner
        participants = (
            ChatParticipant.query
            .filter(ChatParticipant.user_id.in_([current_user.id, int(recipient_id)]))
            .group_by(ChatParticipant.thread_id)
            .having(db.func.count(ChatParticipant.thread_id) == 2)
            .all()
        )
        for p in participants:
            t = ChatThread.query.get(p.thread_id)
            if t and t.thread_type == "direct" and t.learner_id == (learner_id or None):
                thread = t
                break

    if not thread:
        thread = ChatThread(
            thread_type="direct" if not learner_id else "direct",
            learner_id=learner_id or None,
            title=body[:100],
            status="active",
            created_by_user_id=current_user.id,
        )
        db.session.add(thread)
        db.session.flush()
        # Add current user as participant
        db.session.add(ChatParticipant(
            thread_id=thread.id,
            user_id=current_user.id,
            can_post=True,
        ))
        if recipient_id:
            db.session.add(ChatParticipant(
                thread_id=thread.id,
                user_id=int(recipient_id),
                can_post=True,
            ))

    msg = ChatMessage(
        thread_id=thread.id,
        sender_user_id=current_user.id,
        body=body,
        message_type="text",
    )
    db.session.add(msg)

    if idempotency_key:
        db.session.add(TeacherWriteEvent(
            user_id=current_user.id,
            module="messages_send",
            idempotency_key=idempotency_key,
            response_json=json.dumps({"message_id": msg.id}),
        ))

    db.session.commit()

    return jsonify({
        "message": "Message sent.",
        "thread_id": thread.id,
        "message_id": msg.id,
    })


# --- Message Templates API ---


@app.route("/api/message-templates", methods=["GET"])
@login_required
def api_message_templates_list():
    """List active message templates, optionally filtered by category."""
    category = request.args.get("category", "").strip()
    query = MessageTemplate.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    templates = query.order_by(MessageTemplate.category, MessageTemplate.name).all()
    return jsonify({
        "templates": [{
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "body": t.body,
            "placeholders": json.loads(t.placeholders_json) if t.placeholders_json else [],
        } for t in templates]
    })


@app.route("/api/message-templates", methods=["POST"])
@login_required
def api_message_templates_create():
    """Create a new message template (admin only)."""
    if not is_admin_user(current_user):
        abort(403)
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "general").strip()
    body = (data.get("body") or "").strip()
    placeholders = data.get("placeholders") or []
    if not name or not body:
        return jsonify({"error": "Name and body are required."}), 400
    valid_categories = {"attendance", "behavior", "academic", "general"}
    if category not in valid_categories:
        return jsonify({"error": f"Invalid category. Must be one of: {', '.join(sorted(valid_categories))}"}), 400
    tpl = MessageTemplate(
        name=name,
        category=category,
        body=body,
        placeholders_json=json.dumps(placeholders) if placeholders else None,
        created_by_user_id=current_user.id,
    )
    db.session.add(tpl)
    db.session.commit()
    return jsonify({"ok": True, "template": {"id": tpl.id, "name": tpl.name, "category": tpl.category}}), 201


@app.route("/api/message-templates/<int:template_id>", methods=["PUT"])
@login_required
def api_message_templates_update(template_id):
    """Update a message template (admin only)."""
    if not is_admin_user(current_user):
        abort(403)
    tpl = db.session.get(MessageTemplate, template_id)
    if not tpl:
        return jsonify({"error": "Template not found."}), 404
    data = request.get_json(force=True)
    if "name" in data:
        tpl.name = (data["name"] or "").strip()
    if "category" in data:
        cat = (data["category"] or "").strip()
        valid_categories = {"attendance", "behavior", "academic", "general"}
        if cat not in valid_categories:
            return jsonify({"error": f"Invalid category."}), 400
        tpl.category = cat
    if "body" in data:
        tpl.body = (data["body"] or "").strip()
    if "placeholders" in data:
        tpl.placeholders_json = json.dumps(data["placeholders"]) if data["placeholders"] else None
    if "is_active" in data:
        tpl.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/message-templates/<int:template_id>", methods=["DELETE"])
@login_required
def api_message_templates_delete(template_id):
    """Soft-delete (deactivate) a message template (admin only)."""
    if not is_admin_user(current_user):
        abort(403)
    tpl = db.session.get(MessageTemplate, template_id)
    if not tpl:
        return jsonify({"error": "Template not found."}), 404
    tpl.is_active = False
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/teacher/message-templates", methods=["GET"])
@login_required
def api_teacher_message_templates():
    """Teacher-facing list of message templates with placeholders info."""
    if not is_teacher_user(current_user):
        abort(403)
    category = request.args.get("category", "").strip()
    query = MessageTemplate.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    templates = query.order_by(MessageTemplate.category, MessageTemplate.name).all()
    return jsonify({
        "templates": [{
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "body": t.body,
            "placeholders": json.loads(t.placeholders_json) if t.placeholders_json else [],
        } for t in templates]
    })


# ---------------------------------------------------------------------------
# Teacher Portal — Save API stubs (referenced by templates)
# ---------------------------------------------------------------------------


@app.route("/api/teacher/attendance/save", methods=["POST"])
@login_required
def api_teacher_attendance_save():
    """Save an attendance record."""
    if not is_teacher_user(current_user):
        abort(403)
    learner_id = request.form.get("learner_id", "").strip()
    date_absent = request.form.get("date_absent", "").strip()
    academic_year = request.form.get("academic_year", "").strip()
    term = request.form.get("term", "").strip()
    reason_id = request.form.get("reason_id", "").strip()
    reason_other = request.form.get("reason_other", "").strip()
    idempotency_key = request.form.get("idempotency_key", "").strip()

    if not learner_id or not date_absent:
        return jsonify({"error": "Learner ID and date are required."}), 400

    if idempotency_key:
        existing = TeacherWriteEvent.query.filter_by(
            user_id=current_user.id, module="attendance_save",
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return jsonify({"message": "Already saved.", "idempotent": True})

    # Record audit trail
    audit = TeacherAuditLog(
        user_id=current_user.id, action="save_attendance", module="attendance",
        payload_json=json.dumps({
            "learner_id": learner_id, "date_absent": date_absent,
            "academic_year": academic_year, "term": term,
            "reason_id": reason_id, "reason_other": reason_other,
        }),
    )
    db.session.add(audit)

    if idempotency_key:
        db.session.add(TeacherWriteEvent(
            user_id=current_user.id, module="attendance_save",
            idempotency_key=idempotency_key,
            response_json=json.dumps({"learner_id": learner_id}),
        ))

    db.session.commit()
    return jsonify({"message": "Attendance recorded.", "learner_id": learner_id})


@app.route("/api/teacher/discipline/save", methods=["POST"])
@login_required
def api_teacher_discipline_save():
    """Save a discipline record."""
    if not is_teacher_user(current_user):
        abort(403)
    learner_id = request.form.get("learner_id", "").strip()
    date_str = request.form.get("date", "").strip()
    entry_type = request.form.get("type", "Demerit").strip()
    points = request.form.get("points", "1").strip()
    comment = request.form.get("comment", "").strip()
    academic_year = request.form.get("academic_year", "").strip()
    term = request.form.get("term", "").strip()
    idempotency_key = request.form.get("idempotency_key", "").strip()

    if not learner_id:
        return jsonify({"error": "Learner ID is required."}), 400

    if idempotency_key:
        existing = TeacherWriteEvent.query.filter_by(
            user_id=current_user.id, module="discipline_save",
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return jsonify({"message": "Already saved.", "idempotent": True})

    points_int = 0
    try:
        points_int = max(0, min(10, int(points)))
    except (ValueError, TypeError):
        pass

    audit = TeacherAuditLog(
        user_id=current_user.id, action="save_discipline", module="discipline",
        payload_json=json.dumps({
            "learner_id": learner_id, "date": date_str, "type": entry_type,
            "points": points_int, "comment": comment,
            "academic_year": academic_year, "term": term,
        }),
    )
    db.session.add(audit)

    if idempotency_key:
        db.session.add(TeacherWriteEvent(
            user_id=current_user.id, module="discipline_save",
            idempotency_key=idempotency_key,
            response_json=json.dumps({"learner_id": learner_id}),
        ))

    db.session.commit()
    return jsonify({"message": "Discipline recorded.", "learner_id": learner_id})


@app.route("/api/teacher/assessments/save", methods=["POST"])
@login_required
def api_teacher_assessments_save():
    """Save an assessment mark record."""
    if not is_teacher_user(current_user):
        abort(403)
    learner_id = request.form.get("learner_id", "").strip()
    subject_id = request.form.get("subject_id", "").strip()
    mark = request.form.get("mark", "").strip()
    total_mark = request.form.get("total_mark", "100").strip()
    academic_year = request.form.get("academic_year", "").strip()
    term = request.form.get("term", "").strip()
    idempotency_key = request.form.get("idempotency_key", "").strip()

    if not learner_id or not subject_id or not mark:
        return jsonify({"error": "Learner ID, subject, and mark are required."}), 400

    if idempotency_key:
        existing = TeacherWriteEvent.query.filter_by(
            user_id=current_user.id, module="assessments_save",
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return jsonify({"message": "Already saved.", "idempotent": True})

    audit = TeacherAuditLog(
        user_id=current_user.id, action="save_assessment", module="assessments",
        payload_json=json.dumps({
            "learner_id": learner_id, "subject_id": subject_id,
            "mark": mark, "total_mark": total_mark,
            "academic_year": academic_year, "term": term,
        }),
    )
    db.session.add(audit)

    if idempotency_key:
        db.session.add(TeacherWriteEvent(
            user_id=current_user.id, module="assessments_save",
            idempotency_key=idempotency_key,
            response_json=json.dumps({"learner_id": learner_id}),
        ))

    db.session.commit()
    return jsonify({"message": "Assessment saved.", "learner_id": learner_id})


# ---------------------------------------------------------------------------
# Teacher Portal — Learner Profiles routes
# ---------------------------------------------------------------------------


@app.route("/teacher/learner-profiles")
@login_required
def teacher_learner_profiles_page():
    """Teacher learner profiles page."""
    if not is_teacher_user(current_user):
        abort(403)
    session["portal_mode"] = "teacher"
    return render_template("teacher/learner_profiles.html")


@app.route("/api/teacher/learner-profiles/filters")
@login_required
def api_teacher_learner_profiles_filters():
    """Return grade, class, and learner filter options."""
    if not is_teacher_user(current_user):
        abort(403)
    grade = request.args.get("grade", "").strip()
    class_id = request.args.get("class_id", "").strip()

    # Fetch distinct grades
    grades = []
    classes = []
    learners = []
    try:
        if grade:
            sql = "SELECT DISTINCT CSTR([Grade]) AS g FROM [Learner_Info] WHERE CSTR([Grade]) = ? ORDER BY 1"
            rows = mdb_conn.execute_query(sql, (grade,)) or []
            grades = [r["g"] for r in rows if r.get("g")]
        else:
            sql = "SELECT DISTINCT CSTR([Grade]) AS g FROM [Learner_Info] ORDER BY 1"
            rows = mdb_conn.execute_query(sql) or []
            grades = [r["g"] for r in rows if r.get("g")]

        if grade:
            sql = "SELECT DISTINCT CSTR([Class]) AS c FROM [Learner_Info] WHERE CSTR([Grade]) = ? ORDER BY 1"
            params: list[str] = [grade]
            if class_id:
                sql = "SELECT DISTINCT CSTR([Class]) AS c FROM [Learner_Info] WHERE CSTR([Grade]) = ? AND CSTR([Class]) = ? ORDER BY 1"
                params.append(class_id)
            rows = mdb_conn.execute_query(sql, tuple(params)) or []
            classes = [r["c"] for r in rows if r.get("c")]

        # Learners for the dropdown
        sql = "SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class] FROM [Learner_Info]"
        where = []
        params = []
        if grade:
            where.append("CSTR([Grade]) = ?")
            params.append(grade)
        if class_id:
            where.append("CSTR([Class]) = ?")
            params.append(class_id)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY [SName], [FName]"
        rows = mdb_conn.execute_query(sql, tuple(params)) or []
        learners = [
            {"id": str(r.get("LearnerID", r.get("ID", "")) or ""),
             "label": f"{str(r.get('SName', '') or '')}, {str(r.get('FName', '') or '')} ({str(r.get('LearnerID', r.get('ID', '')) or '')})"}
            for r in rows
        ]
    except Exception:
        pass

    return jsonify({"grades": grades, "classes": classes, "learners": learners})


@app.route("/api/teacher/learner-profiles")
@login_required
def api_teacher_learner_profiles():
    """Return learner profiles with academic and discipline summaries."""
    if not is_teacher_user(current_user):
        abort(403)
    grade = request.args.get("grade", "").strip()
    class_id = request.args.get("class_id", "").strip()
    learner_id = request.args.get("learner_id", "").strip()

    sql = "SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class] FROM [Learner_Info] WHERE 1=1"
    params: list[str] = []
    if grade:
        sql += " AND CSTR([Grade]) = ?"
        params.append(grade)
    if class_id:
        sql += " AND CSTR([Class]) = ?"
        params.append(class_id)
    if learner_id:
        sql += " AND (CSTR([LearnerID]) = ? OR CSTR([ID]) = ?)"
        params.extend([learner_id, learner_id])

    try:
        rows = mdb_conn.execute_query(sql, tuple(params)) or []
    except Exception:
        rows = []

    result = []
    for r in rows:
        lid = str(r.get("LearnerID", r.get("ID", "")) or "")
        # Count discipline records for this learner
        disc_count = 0
        try:
            dr = mdb_conn.execute_query(
                "SELECT COUNT(*) AS cnt FROM [DisciplinaryLearnerMisconduct] WHERE CSTR([Learnerid]) = ?",
                (lid,),
            )
            if dr:
                disc_count = int(dr[0].get("cnt", 0) or 0)
        except Exception:
            pass

        # Average mark from ReportMarks
        avg_pct = 0
        try:
            ar = mdb_conn.execute_query(
                "SELECT AVG(CAST([Mark] AS FLOAT) / NULLIF(CAST([TotalMark] AS FLOAT), 0) * 100) AS avg_pct "
                "FROM [ReportMarks] WHERE CSTR([LearnerID]) = ? AND [TotalMark] > 0",
                (lid,),
            )
            if ar and ar[0].get("avg_pct") is not None:
                avg_pct = round(float(ar[0]["avg_pct"]), 1)
        except Exception:
            pass

        result.append({
            "id": str(r.get("ID", "") or ""),
            "learnerId": lid,
            "fname": str(r.get("FName", "") or ""),
            "sname": str(r.get("SName", "") or ""),
            "grade": str(r.get("Grade", "") or ""),
            "classId": str(r.get("Class", "") or ""),
            "disciplineCount": disc_count,
            "academicAvgPct": avg_pct,
        })

    return jsonify({"rows": result})


# ---------------------------------------------------------------------------
# Teacher Portal — Disciplinary Entry routes
# ---------------------------------------------------------------------------


@app.route("/teacher/disciplinary-entry")
@login_required
def teacher_disciplinary_entry_page():
    """Teacher disciplinary entry page."""
    if not is_teacher_user(current_user):
        abort(403)
    session["portal_mode"] = "teacher"
    return render_template("teacher/disciplinary_entry.html")


@app.route("/api/teacher/disciplinary-entry/options")
@login_required
def api_teacher_disciplinary_entry_options():
    """Return filter options for disciplinary entry form."""
    if not is_teacher_user(current_user):
        abort(403)
    grade = request.args.get("grade", "").strip()
    level = request.args.get("level", "").strip()

    grades = []
    levels = []
    learners = []
    misconducts = []

    try:
        # Distinct grades from Learner_Info
        sql = "SELECT DISTINCT CSTR([Grade]) AS g FROM [Learner_Info] ORDER BY 1"
        rows = mdb_conn.execute_query(sql) or []
        grades = [r["g"] for r in rows if r.get("g")]

        # Levels — try DisciplinaryLevels table, fallback to static
        try:
            lrows = mdb_conn.execute_query("SELECT DISTINCT [Level] FROM [DisciplinaryLevels] ORDER BY 1") or []
            if lrows:
                levels = [r["Level"] for r in lrows if r.get("Level")]
        except Exception:
            levels = ["Minor", "Moderate", "Serious"]

        # Learners filtered by grade
        sql2 = "SELECT [ID], [LearnerID], [FName], [SName], [Grade] FROM [Learner_Info] WHERE 1=1"
        params2: list[str] = []
        if grade:
            sql2 += " AND CSTR([Grade]) = ?"
            params2.append(grade)
        sql2 += " ORDER BY [SName], [FName]"
        lrows = mdb_conn.execute_query(sql2, tuple(params2)) or []
        learners = [
            {"id": str(r.get("LearnerID", r.get("ID", "")) or ""),
             "name": str(r.get("FName", "") or ""),
             "surname": str(r.get("SName", "") or ""),
             "grade": str(r.get("Grade", "") or "")}
            for r in lrows
        ]

        # Misconduct options
        try:
            mrows = mdb_conn.execute_query(
                "SELECT [ID], [Description], [Point] FROM [DisciplinaryMisconduct] ORDER BY [Description]"
            ) or []
            misconducts = [
                {"id": str(r.get("ID", "") or ""),
                 "description": str(r.get("Description", "") or ""),
                 "point": int(r.get("Point", 0) or 0)}
                for r in mrows
            ]
        except Exception:
            misconducts = [
                {"id": "1", "description": "Late coming", "point": 1},
                {"id": "2", "description": "Disruptive behaviour", "point": 2},
                {"id": "3", "description": "Incomplete homework", "point": 1},
                {"id": "4", "description": "Bullying", "point": 5},
                {"id": "5", "description": "Vandalism", "point": 5},
            ]
    except Exception:
        pass

    return jsonify({
        "grades": grades,
        "levels": levels,
        "learners": learners,
        "misconducts": misconducts,
    })


@app.route("/api/teacher/disciplinary-entry/save", methods=["POST"])
@login_required
def api_teacher_disciplinary_entry_save():
    """Save a disciplinary entry for selected learners."""
    if not is_teacher_user(current_user):
        abort(403)

    learner_ids = request.form.getlist("learner_ids")
    grade = request.form.get("grade", "").strip()
    level_misconduct = request.form.get("level_misconduct", "").strip()
    misconduct_id = request.form.get("misconduct_id", "").strip()
    notes = request.form.get("notes", "").strip()
    idempotency_key = request.form.get("idempotency_key", "").strip()

    if not learner_ids or not misconduct_id:
        return jsonify({"error": "Select at least one learner and a misconduct type."}), 400

    if idempotency_key:
        existing = TeacherWriteEvent.query.filter_by(
            user_id=current_user.id, module="disciplinary_entry_save",
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return jsonify({"message": "Already saved.", "idempotent": True})

    results = []
    for lid in learner_ids:
        audit = TeacherAuditLog(
            user_id=current_user.id, action="disciplinary_entry", module="discipline",
            payload_json=json.dumps({
                "learner_id": lid, "grade": grade,
                "level": level_misconduct, "misconduct_id": misconduct_id,
                "notes": notes,
            }),
        )
        db.session.add(audit)
        results.append({"learner_id": lid, "record_id": None})

    if idempotency_key:
        db.session.add(TeacherWriteEvent(
            user_id=current_user.id, module="disciplinary_entry_save",
            idempotency_key=idempotency_key,
            response_json=json.dumps({"count": len(learner_ids)}),
        ))

    db.session.commit()
    return jsonify({"message": f"Disciplinary entry recorded for {len(results)} learner(s).", "results": results})


@app.route("/teacher/messages")
@login_required
def teacher_messages_page():
    """Teacher chat/messages page."""
    if not is_teacher_user(current_user):
        abort(403)
    session["portal_mode"] = "teacher"
    return render_template("teacher/messages.html")


@app.route("/management")
@login_required
def management_dashboard():
    if not _management_user_can_access_reports(current_user):
        abort(403)
    session["portal_mode"] = "management"
    return render_template("management/dashboard_home.html", reports=MANAGEMENT_REPORT_REGISTRY)


@app.route("/admin", strict_slashes=False)
@login_required
def admin_dashboard():
    if not is_admin_user(current_user):
        abort(403)
    return render_template("admin/dashboard.html")


@app.route("/management/report/<report_key>")
@login_required
def management_report(report_key):
    if not _management_user_can_access_reports(current_user):
        abort(403)
    meta = MANAGEMENT_REPORTS_BY_KEY.get(report_key)
    if not meta:
        abort(404)
    session["portal_mode"] = "management"
    return render_template(meta["template"], report=meta)


@app.route('/parent/learner-profile')
@login_required
def parent_learner_profile():
    user = current_user
    if is_admin_user(user) or is_teacher_user(user):
        flash('This page is available for parent accounts only.', 'error')
        return redirect(url_for('dashboard'))

    learner_id = get_active_learner_id_for_request(user)
    if not learner_id:
        flash('No learners are linked to your account.', 'error')
        return redirect(url_for('dashboard'))

    learner_row = _mdb_get_learner_profile_row(learner_id)
    parent_row = _mdb_get_parent_profile_row(learner_id)
    learner_fields = _fields_present(learner_row, LEARNER_PROFILE_LEARNER_FIELDS)
    parent_fields = _fields_present(parent_row, LEARNER_PROFILE_PARENT_FIELDS)
    spouse_fields = _fields_present(parent_row, LEARNER_PROFILE_SPOUSE_FIELDS)

    requests_rows = (
        ProfileChangeRequest.query
        .filter_by(submitted_by_user_id=user.id, learner_id=str(learner_id))
        .order_by(ProfileChangeRequest.submitted_at.desc())
        .limit(20)
        .all()
    )
    has_pending = any(str(r.status or "").lower() == "pending" for r in requests_rows)

    return render_template(
        'parent/learner_profile.html',
        user=user,
        learner_info=fetch_learner_info_by_id(learner_id),
        learner_row=learner_row,
        parent_row=parent_row,
        learner_fields=learner_fields,
        parent_fields=parent_fields,
        spouse_fields=spouse_fields,
        requests_rows=requests_rows,
        has_pending=has_pending,
        active_learner_id=learner_id,
    )


@app.route('/parent/learner-profile/submit-change', methods=['POST'])
@login_required
def parent_submit_learner_profile_change():
    user = current_user
    if is_admin_user(user) or is_teacher_user(user):
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    learner_id = get_active_learner_id_for_request(user)
    linked_ids = get_linked_learner_ids_for_user(user)
    if not learner_id or learner_id not in linked_ids:
        flash('Invalid learner context.', 'error')
        return redirect(url_for('dashboard'))

    pending_exists = ProfileChangeRequest.query.filter_by(
        submitted_by_user_id=user.id,
        learner_id=str(learner_id),
        status='pending',
    ).first()
    if pending_exists:
        flash('A pending profile update request already exists for this learner.', 'error')
        return redirect(url_for('parent_learner_profile'))

    learner_row = _mdb_get_learner_profile_row(learner_id)
    parent_row = _mdb_get_parent_profile_row(learner_id)
    parent_id_key = str(parent_row.get("ParentID", "")).strip() if parent_row else ""

    learner_fields = _fields_present(learner_row, LEARNER_PROFILE_LEARNER_FIELDS)
    parent_fields = _fields_present(parent_row, LEARNER_PROFILE_PARENT_FIELDS)
    spouse_fields = _fields_present(parent_row, LEARNER_PROFILE_SPOUSE_FIELDS)

    changes: list[dict] = []
    for key, _label in learner_fields:
        form_key = f"learner__{key}"
        old_value = _to_text_or_empty(learner_row.get(key))
        new_value = _to_text_or_empty(request.form.get(form_key, ""))
        if old_value != new_value:
            changes.append(
                {
                    "entity": "learner_info",
                    "record_key": str(learner_id),
                    "field_name": key,
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )

    for key, _label in (parent_fields + spouse_fields):
        form_key = f"parent__{key}"
        old_value = _to_text_or_empty(parent_row.get(key) if parent_row else "")
        new_value = _to_text_or_empty(request.form.get(form_key, ""))
        if old_value != new_value:
            changes.append(
                {
                    "entity": "parent_info",
                    "record_key": parent_id_key,
                    "field_name": key,
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )

    if not changes:
        flash('No changes detected.', 'error')
        return redirect(url_for('parent_learner_profile'))

    if any(c["entity"] == "parent_info" and not c["record_key"] for c in changes):
        flash('Could not resolve parent record for approval workflow.', 'error')
        return redirect(url_for('parent_learner_profile'))

    parent_comment = str(request.form.get("parent_comment", "") or "").strip()[:4000]
    req = ProfileChangeRequest(
        submitted_by_user_id=user.id,
        learner_id=str(learner_id),
        status='pending',
        parent_comment=parent_comment,
    )
    db.session.add(req)
    db.session.flush()

    for c in changes:
        db.session.add(
            ProfileChangeItem(
                request_id=req.id,
                entity=c["entity"],
                record_key=str(c["record_key"]),
                field_name=str(c["field_name"]),
                old_value=c["old_value"],
                new_value=c["new_value"],
            )
        )
    db.session.commit()
    flash('Profile update request submitted for admin approval.', 'success')
    return redirect(url_for('parent_learner_profile'))


def _management_user_can_access_reports(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "username", None) == ADMIN_USERNAME:
        return True
    if getattr(user, "is_manager", False):
        return True
    if getattr(user, "is_teacher", False):
        return True
    return False


def _management_sort_year_strings(values: list[str]) -> list[str]:
    def sort_key(y: str):
        s = str(y).strip()
        if s.isdigit():
            return (0, int(s))
        try:
            return (0, int(float(s)))
        except ValueError:
            return (1, s)

    uniq: list[str] = []
    seen: set[str] = set()
    for v in values:
        vv = str(v).strip()
        if vv and vv not in seen:
            seen.add(vv)
            uniq.append(vv)
    uniq.sort(key=sort_key, reverse=True)
    return uniq


def _management_sort_term_strings(values: list[str]) -> list[str]:
    def sort_key(t: str):
        s = str(t).strip()
        if s.isdigit():
            return (0, int(s))
        try:
            return (0, int(float(s)))
        except ValueError:
            return (1, s)

    uniq: list[str] = []
    seen: set[str] = set()
    for v in values:
        vv = str(v).strip()
        if vv and vv not in seen:
            seen.add(vv)
            uniq.append(vv)
    uniq.sort(key=sort_key)
    return uniq


def _management_learner_promotion_year_columns() -> tuple[str, ...]:
    """Columns on LearnerPromotion holding the academic year. PostgreSQL mirror uses DataYear only."""
    if app.config.get("POSTGRES_MDB_COMPAT_MODE"):
        return ("DataYear",)
    return ("DataYear", "Datayear")


def _management_report_filters_payload(args: dict) -> dict:
    """Distinct years/terms (and related facets) from marks — full history, not latest year only."""
    year_sel = str(args.get("year") or "").strip()
    term_sel = str(args.get("term") or "").strip()
    phase_sel = str(args.get("phase") or "").strip().lower()

    y_rows = (
        mdb_conn.execute_query(
            """
            SELECT DISTINCT CSTR(rm.Datayear) AS Y
            FROM ReportMarks rm
            WHERE rm.Datayear IS NOT NULL
            """,
            (),
        )
        or []
    )
    years = _management_sort_year_strings(
        [str(r.get("Y") or r.get("y") or "").strip() for r in y_rows if str(r.get("Y") or r.get("y") or "").strip()]
    )

    if year_sel:
        t_rows = (
            mdb_conn.execute_query(
                """
                SELECT DISTINCT CSTR(rc.Term) AS T
                FROM ReportMarks rm, ReportCycles rc
                WHERE rm.ReportId = rc.CycleId
                  AND rm.Datayear IS NOT NULL
                  AND rc.Term IS NOT NULL
                  AND CSTR(rm.Datayear) = ?
                """,
                (year_sel,),
            )
            or []
        )
    else:
        t_rows = (
            mdb_conn.execute_query(
                """
                SELECT DISTINCT CSTR(rc.Term) AS T
                FROM ReportMarks rm, ReportCycles rc
                WHERE rm.ReportId = rc.CycleId
                  AND rm.Datayear IS NOT NULL
                  AND rc.Term IS NOT NULL
                """,
                (),
            )
            or []
        )
    terms = _management_sort_term_strings(
        [str(r.get("T") or r.get("t") or "").strip() for r in t_rows if str(r.get("T") or r.get("t") or "").strip()]
    )

    phases = ["Foundation", "Intermediate", "Senior", "FET"]

    grades: list[str] = []
    try:
        # PostgreSQL: DISTINCT requires ORDER BY to use select-list expressions (use alias G not lp.Grade).
        # LearnerPromotion year: DataYear on PG mirror; legacy Access may use Datayear (see _management_learner_promotion_year_columns).
        grade_attempts: list[tuple[str, tuple]] = []
        if not year_sel:
            grade_attempts.append(
                (
                    """
                    SELECT DISTINCT CSTR(lp.Grade) AS G
                    FROM LearnerPromotion lp
                    WHERE lp.Grade IS NOT NULL
                    ORDER BY G
                    """,
                    (),
                )
            )
        else:
            y_f = str(year_sel).strip()
            for ycol in _management_learner_promotion_year_columns():
                grade_attempts.append(
                    (
                        f"""
                    SELECT DISTINCT CSTR(lp.Grade) AS G
                    FROM LearnerPromotion lp
                    WHERE lp.Grade IS NOT NULL
                      AND CSTR(lp.{ycol}) = ?
                    ORDER BY G
                    """,
                        (y_f,),
                    )
                )
        seen_g: set[str] = set()
        for g_sql, g_params in grade_attempts:
            g_rows = mdb_conn.execute_query(g_sql, g_params) or []
            for r in g_rows:
                v = str(r.get("G") or r.get("g") or "").strip()
                if v and v not in seen_g:
                    seen_g.add(v)
                    grades.append(v)
    except Exception:
        grades = []

    def _grade_sort_key(g: str) -> int:
        m = re.search(r"(\d+)", str(g))
        return int(m.group(1)) if m else 999

    grades.sort(key=_grade_sort_key)

    pmap = {
        "foundation": {1, 2, 3},
        "intermediate": {4, 5, 6},
        "senior": {7, 8, 9},
        "fet": {10, 11, 12},
    }
    allowed = pmap.get(phase_sel)
    if allowed:
        grades = [g for g in grades if _grade_sort_key(g) in allowed]

    subjects: list[str] = []
    try:
        subj_sql = """
            SELECT DISTINCT s.Name AS N
            FROM ReportMarks rm, Subjects s
            WHERE rm.SubjectId = s.Id AND s.Name IS NOT NULL
        """
        subj_params: list = []
        if year_sel:
            subj_sql += " AND CSTR(rm.Datayear) = ?"
            subj_params.append(year_sel)
        if term_sel:
            subj_sql += """
              AND EXISTS (
                SELECT 1 FROM ReportCycles rcx
                WHERE rcx.CycleId = rm.ReportId AND CSTR(rcx.Term) = ?
              )
            """
            subj_params.append(term_sel)
        subj_sql += " ORDER BY N ASC"
        s_rows = mdb_conn.execute_query(subj_sql, tuple(subj_params)) or []
        seen_s: set[str] = set()
        for r in s_rows:
            raw = str(r.get("N") or r.get("n") or r.get("Name") or "").strip()
            v = _management_normalize_subject_label(raw)
            if v and v not in seen_s:
                seen_s.add(v)
                subjects.append(v)
    except Exception:
        subjects = []

    return {
        "years": years,
        "terms": terms,
        "phases": phases,
        "grades": grades,
        "subjects": subjects[:800],
    }


def _parent_portal_feature_allowed(flag: str) -> bool:
    if not getattr(current_user, "is_authenticated", False):
        return False
    if is_admin_user(current_user):
        return True
    if is_manager_user(current_user) and session.get("portal_mode") == "parent":
        return bool(getattr(current_user, flag, True))
    if is_teacher_user(current_user):
        return True
    return True


def _parent_learner_year_data() -> dict:
    """Query LearnerPromotion scoped to linked learners.
    Returns yearGradeMap (year→first_grade), gradeToYears (grade→[years]),
           learnerGrades (unique grades), learnerYears (unique years, desc)."""
    linked_ids = get_linked_learner_ids_for_user(current_user)
    if not linked_ids:
        return {"yearGradeMap": {}, "gradeToYears": {}, "learnerGrades": [], "learnerYears": []}

    resolved: set[str] = set()
    for lid in linked_ids:
        info = fetch_learner_info_by_id(lid)
        if info:
            pk = str(info.get("id") or "").strip()
            if pk:
                resolved.add(pk)

    if not resolved:
        return {"yearGradeMap": {}, "gradeToYears": {}, "learnerGrades": [], "learnerYears": []}

    ids_placeholders = ", ".join(["?"] * len(resolved))
    rows = (
        mdb_conn.execute_query(
            f"""
            SELECT CSTR(lp.DataYear) AS Y, CSTR(lp.Grade) AS G
            FROM LearnerPromotion lp
            WHERE lp.DataYear IS NOT NULL AND lp.Grade IS NOT NULL
              AND CSTR(lp.LearnerId) IN ({ids_placeholders})
            """,
            tuple(sorted(resolved)),
        )
        or []
    )

    def _grade_sort(g: str) -> int:
        m = re.search(r"(\d+)", str(g))
        return int(m.group(1)) if m else 999

    # year → set of grades, grade → set of years
    year_grades: dict[str, set[str]] = defaultdict(set)
    grade_years: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        y = str(r.get("Y") or r.get("y") or "").strip()
        g = str(r.get("G") or r.get("g") or "").strip()
        if y and g:
            year_grades[y].add(g)
            grade_years[g].add(y)

    # yearGradeMap: year → first grade (alphabetically sorted, for data-grade attribute)
    yg_map: dict[str, str] = {}
    for y, gs in year_grades.items():
        yg_map[y] = sorted(gs, key=_grade_sort)[0]

    # gradeToYears: grade → years sorted desc
    gy_map: dict[str, list[str]] = {}
    for g, ys in grade_years.items():
        gy_map[g] = sorted(ys, key=int, reverse=True)

    # All unique grades and years (sorted)
    all_grades = sorted(set(g for gs in year_grades.values() for g in gs), key=_grade_sort)
    all_years = sorted(set(year_grades.keys()), key=int, reverse=True)

    return {
        "yearGradeMap": yg_map,
        "gradeToYears": gy_map,
        "learnerGrades": all_grades,
        "learnerYears": all_years,
    }


def _parent_academics_filters_payload() -> dict:
    fb = _management_report_filters_payload(
        {"year": "", "term": "", "phase": "", "grade": "", "subject": "", "school": ""}
    )
    years_raw = fb.get("years") or []
    grades_all = [str(g).strip() for g in (fb.get("grades") or []) if str(g).strip()]
    terms_raw = fb.get("terms") or []
    subjects_raw = fb.get("subjects") or []

    # Learner-scoped data
    learner_data = _parent_learner_year_data()
    yg_map = learner_data["yearGradeMap"]
    grade_to_years = learner_data["gradeToYears"]
    learner_grades = learner_data["learnerGrades"]
    learner_years = learner_data["learnerYears"]
    is_system_admin = is_admin_user(current_user)

    # Parent users: scope years and grades to this learner's promotion records
    if not is_system_admin and yg_map:
        years_out = []
        learner_year_set = set(learner_years)
        for y in years_raw:
            ys = str(y).strip()
            if ys in learner_year_set:
                years_out.append({"value": ys, "label": ys, "grade": yg_map.get(ys, "")})
    else:
        years_out = []
        for y in years_raw:
            ys = str(y).strip()
            years_out.append({"value": ys, "label": ys, "grade": yg_map.get(ys, "")})

    if not is_system_admin and learner_grades:
        grades_out = [g for g in grades_all if g in set(learner_grades)]
    else:
        grades_out = grades_all

    terms_out = []
    for t in terms_raw:
        ts = str(t).strip()
        try:
            cn = int(float(ts)) if ts.replace(".", "", 1).isdigit() else 0
        except ValueError:
            cn = 0
        terms_out.append({"value": ts, "label": f"Term {ts}" if ts.isdigit() else ts, "cycleNo": cn})
    terms_out.sort(key=lambda x: int(x.get("cycleNo") or 0))

    subjects_out = [{"value": s, "label": s} for s in subjects_raw if str(s).strip()]

    return {
        "years": years_out,
        "terms": terms_out,
        "subjects": subjects_out,
        "grades": grades_out,
        "yearGradeMap": yg_map,
        "gradeToYears": grade_to_years,
    }


def _academics_row_percentage(row: dict) -> float:
    try:
        m = float(row.get("Mark") or 0)
        t = float(row.get("TotalMark") or 0)
        if t <= 0:
            return 0.0
        return float(Decimal(str(100.0 * m / t)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
    except (TypeError, ValueError):
        return 0.0


def _academics_apply_learner_scope(query: str, params: list, req_learner_id: str) -> tuple[str, list]:
    if is_analytics_user(current_user):
        return query, params
    admin_like = is_admin_user(current_user) or (
        is_manager_user(current_user) and session.get("portal_mode") == "management"
    )
    if admin_like:
        if not str(req_learner_id or "").strip():
            return query, params
        cands = get_learner_match_candidates(req_learner_id)
        if not cands:
            return query + " AND 1=0 ", params
        parts = " OR ".join(["CSTR(rm.LearnerID) = ?"] * len(cands))
        return query + f" AND ({parts}) ", params + list(cands)
    lid = get_active_learner_id_for_request(current_user)
    if not lid:
        return query + " AND 1=0 ", params
    cands = get_learner_match_candidates(lid)
    if not cands:
        return query + " AND 1=0 ", params
    parts = " OR ".join(["CSTR(rm.LearnerID) = ?"] * len(cands))
    return query + f" AND ({parts}) ", params + list(cands)


def _term_display(val) -> str:
    s = str(val or "").strip()
    if s.isdigit():
        return f"Term {s}"
    return s or "—"


@app.route("/api/learner-profile")
@login_required
def api_learner_profile():
    if is_analytics_user(current_user):
        return jsonify(
            {
                "name": "All",
                "surname": "Learners",
                "id": "ALL",
                "learner_id": "ALL",
                "grade": "All Grades",
            }
        )
    lid = get_active_learner_id_for_request(current_user)
    if not lid:
        return jsonify({"error": "No learner linked to this account."}), 400
    info = fetch_learner_info_by_id(lid)
    if not info:
        return jsonify({"error": "Learner not found."}), 404
    return jsonify(
        {
            "name": str(info.get("name") or ""),
            "surname": str(info.get("surname") or ""),
            "id": str(info.get("id") or ""),
            "learner_id": str(info.get("learner_id") or ""),
            "grade": str(info.get("grade") or ""),
        }
    )


@app.route("/api/academics-filters")
@login_required
def api_academics_filters():
    if not _parent_portal_feature_allowed("mgmt_can_view_academics"):
        abort(403)
    try:
        return jsonify(_parent_academics_filters_payload())
    except Exception:
        app.logger.exception("academics-filters failed")
        return jsonify({"years": [], "terms": [], "subjects": [], "grades": [], "yearGradeMap": {}})


@app.route("/api/academics")
@login_required
def api_academics():
    if not _parent_portal_feature_allowed("mgmt_can_view_academics"):
        abort(403)
    grade = request.args.get("grade", "").strip()
    year = request.args.get("year", "").strip()
    term = request.args.get("term", "").strip()
    subject = request.args.get("subject", "").strip()
    admin_lid = request.args.get("learner_id", "").strip()
    flt: dict = {}
    if year:
        flt["year"] = year
    if term:
        flt["term"] = term
    if grade:
        flt["grade"] = grade
    if subject:
        flt["subject"] = subject
    try:
        query = """
        SELECT rm.Datayear AS Year, rc.Term AS Term, s.Name AS Subject,
               rm.Mark AS Mark, rm.TotalMark AS TotalMark, CSTR(rm.LearnerID) AS LearnerID
        FROM ReportMarks rm, ReportCycles rc, Subjects s
        WHERE rm.ReportId = rc.CycleId
          AND rm.SubjectId = s.Id
        """
        params: list = []
        if flt.get("year"):
            query += " AND CSTR(rm.Datayear) = ?"
            params.append(flt["year"])
        else:
            # For parent/teacher (learner-scoped), show all years the learner has data.
            # For admin/analytics, default to the latest global year.
            if is_analytics_user(current_user) or is_admin_user(current_user) or (
                is_manager_user(current_user) and session.get("portal_mode") == "management"
            ):
                query += " AND rm.Datayear = (SELECT MAX(rm2.Datayear) FROM ReportMarks rm2)"
        if flt.get("term"):
            query += " AND CSTR(rc.Term) = ?"
            params.append(flt["term"])
        if flt.get("grade"):
            query += """
                AND EXISTS (
                    SELECT 1
                    FROM LearnerPromotion lp
                    WHERE CSTR(lp.LearnerId) = CSTR(rm.LearnerID)
                      AND CAST(lp.DataYear AS TEXT) = CAST(rm.Datayear AS TEXT)
                      AND CSTR(lp.Grade) = ?
                )
            """
            params.append(flt["grade"])
        if flt.get("subject"):
            query += " AND (s.Name = ? OR s.Name LIKE ?)"
            params.append(flt["subject"])
            params.append(f"{flt['subject']}%")
        query, params = _academics_apply_learner_scope(query, params, admin_lid)
        query += " ORDER BY rm.Datayear DESC, rc.Term ASC"
        rows = mdb_conn.execute_query(query, tuple(params)) or []
        out = []
        for r in rows:
            pct = _academics_row_percentage(r)
            out.append(
                {
                    "Year": r.get("Year"),
                    "Term": _term_display(r.get("Term")),
                    "Subject": _management_normalize_subject_label(str(r.get("Subject") or "")),
                    "Mark": r.get("Mark"),
                    "TotalMark": r.get("TotalMark"),
                    "LearnerID": r.get("LearnerID"),
                    "Percentage": pct,
                }
            )
        return jsonify(out)
    except Exception:
        app.logger.exception("api/academics failed")
        return jsonify({"error": "Could not load academics."}), 500


@app.route("/api/subject-details")
@login_required
def api_subject_details():
    if not _parent_portal_feature_allowed("mgmt_can_view_academics"):
        abort(403)
    subj = request.args.get("subject", "").strip()
    year = request.args.get("year", "").strip()
    term_q = request.args.get("term", "").strip()
    admin_lid = request.args.get("learner_id", "").strip()
    if not subj or not year:
        return jsonify([])
    flt = {"year": year, "subject": subj}
    if term_q:
        m = re.match(r"Term\s+(\d+)", term_q, flags=re.IGNORECASE)
        flt["term"] = m.group(1) if m else term_q
    try:
        q0 = """
        SELECT rm.Datayear AS Year, rc.Term AS Term, s.Name AS Subject,
               rm.Mark AS Mark, rm.TotalMark AS TotalMark
        FROM ReportMarks rm, ReportCycles rc, Subjects s
        WHERE rm.ReportId = rc.CycleId
          AND rm.SubjectId = s.Id
        """
        params: list = []
        q0 += " AND CSTR(rm.Datayear) = ?"
        params.append(year)
        q0 += " AND (s.Name = ? OR s.Name LIKE ?)"
        params.extend([subj, f"{subj}%"])
        if flt.get("term"):
            q0 += " AND CSTR(rc.Term) = ?"
            params.append(flt["term"])
        q0, params = _academics_apply_learner_scope(q0, params, admin_lid)
        rows = mdb_conn.execute_query(q0, tuple(params)) or []
        out = []
        for r in rows:
            pct = _academics_row_percentage(r)
            out.append(
                {
                    "AssessmentDate": "",
                    "AssessmentType": "Report mark",
                    "Score": r.get("Mark"),
                    "Grade": "—",
                    "Percentage": pct,
                }
            )
        return jsonify(out)
    except Exception:
        app.logger.exception("api/subject-details failed")
        return jsonify([])


@app.route("/api/attendance-filters")
@login_required
def api_attendance_filters():
    if not _parent_portal_feature_allowed("mgmt_can_view_attendance"):
        abort(403)
    try:
        fb = _management_report_filters_payload(
            {"year": "", "term": "", "phase": "", "grade": "", "subject": "", "school": ""}
        )
        return jsonify({"years": fb.get("years") or [], "grades": fb.get("grades") or []})
    except Exception:
        return jsonify({"years": [], "grades": []})


def _attendance_rows_for_user(year: str, grade: str, admin_lid: str) -> list[dict]:
    cands: list[str] = []
    if is_analytics_user(current_user):
        cands = []
    else:
        admin_like = is_admin_user(current_user) or (
            is_manager_user(current_user) and session.get("portal_mode") == "management"
        )
        if admin_like:
            if str(admin_lid or "").strip():
                cands = get_learner_match_candidates(admin_lid)
        else:
            lid = get_active_learner_id_for_request(current_user)
            if lid:
                cands = get_learner_match_candidates(lid)
    q = """
    SELECT
        a.DateAbsent AS date_absent,
        CAST('20' || SUBSTR(a.DateAbsent, 7, 2) AS TEXT) AS year,
        CAST(a.Learnerid AS TEXT) AS learnerid,
        li.Grade AS grade,
        COALESCE(CAST(a.ReasonOther AS TEXT), '') AS reason
    FROM Absentees a
    LEFT JOIN Learner_Info li ON CAST(li."ID" AS TEXT) = CAST(a.Learnerid AS TEXT)
    WHERE a.DateAbsent IS NOT NULL
    """
    params: list = []
    if year:
        q += " AND CAST('20' || SUBSTR(a.DateAbsent, 7, 2) AS TEXT) = ?"
        params.append(year)
    if grade:
        q += " AND CSTR(li.Grade) = ?"
        params.append(grade)
    if cands:
        part = " OR ".join(["CSTR(a.Learnerid) = ?"] * len(cands))
        q += f" AND ({part}) "
        params.extend(cands)
    q += " ORDER BY a.DateAbsent DESC"
    rows = mdb_conn.execute_query(q, tuple(params)) or []
    out = []
    for r in rows:
        dt = r.get("date_absent") or r.get("DateAbsent")
        mo = None
        try:
            if hasattr(dt, "month"):
                mo = int(dt.month)
            elif dt:
                dtp = datetime.fromisoformat(str(dt)[:10])
                mo = int(dtp.month)
        except Exception:
            mo = None
        out.append(
            {
                "date_absent": dt,
                "year": r.get("year") or r.get("Year"),
                "grade": r.get("grade") or r.get("Grade"),
                "reason": r.get("reason") or r.get("Reason") or "",
                "month": mo,
                "learnerid": r.get("learnerid") or r.get("Learnerid") or "",
            }
        )
    return out


@app.route("/api/attendance")
@login_required
def api_attendance():
    if not _parent_portal_feature_allowed("mgmt_can_view_attendance"):
        abort(403)
    year = request.args.get("year", "").strip()
    grade = request.args.get("grade", "").strip()
    admin_lid = request.args.get("learner_id", "").strip()
    try:
        return jsonify(_attendance_rows_for_user(year, grade, admin_lid))
    except Exception:
        app.logger.exception("api/attendance failed")
        return jsonify({"error": "Could not load attendance."}), 500


@app.route("/api/finance")
@login_required
def api_finance():
    if not _parent_portal_feature_allowed("mgmt_can_view_finance"):
        abort(403)
    if is_analytics_user(current_user):
        return jsonify(
            {
                "annualFee": 0,
                "totalPaid": 0,
                "outstanding": 0,
                "balance": 0,
                "isPaid": True,
                "currentYear": datetime.utcnow().year,
                "transactions": [],
            }
        )
    req_id = request.args.get("learner_id", "").strip()
    admin_like = is_admin_user(current_user) or (
        is_manager_user(current_user) and session.get("portal_mode") == "management"
    )
    lid = req_id if (admin_like and req_id) else get_active_learner_id_for_request(current_user)
    if not lid:
        return jsonify({"error": "No learner selected."}), 400
    y = datetime.utcnow().year
    # First try the current year, then fall back to the most recent year with data
    pl = _finance_payload_for_learner(learner_id=str(lid), target_year=y)
    if not pl or not pl.get("transactions"):
        # Try most recent year from DebtorsTrans
        try:
            cand_keys: list[str] = [str(lid)]
            info_f = fetch_learner_info_by_id(str(lid)) or {}
            pk = str(info_f.get("id") or "").strip()
            if pk and pk != str(lid):
                cand_keys.append(pk)
            lc = str(info_f.get("learner_id") or "").strip()
            if lc:
                cand_keys.append(lc)
            parts = " OR ".join([f"CSTR([DebAcc]) = ?"] * len(cand_keys))
            yr_rows = mdb_conn.execute_query(
                f"""
                SELECT CSTR([Year]) AS Y
                FROM DebtorsTrans
                WHERE ({parts})
                ORDER BY CSTR([Year]) DESC
                LIMIT 1
                """,
                tuple(sorted(cand_keys)),
            ) or []
            if yr_rows:
                y_fallback = int(str(yr_rows[0].get("Y") or "0"))
                if y_fallback > 0:
                    y = y_fallback
                    pl = _finance_payload_for_learner(learner_id=str(lid), target_year=y)
        except Exception:
            pass
    if not pl:
        return jsonify(
            {
                "annualFee": 0,
                "totalPaid": 0,
                "outstanding": 0,
                "balance": 0,
                "isPaid": True,
                "currentYear": y,
                "transactions": [],
            }
        )
    outstanding = float(pl.get("outstanding") or 0)
    return jsonify(
        {
            "annualFee": float(pl.get("annualFee") or outstanding or 0),
            "totalPaid": float(pl.get("totalPaid") or 0),
            "outstanding": outstanding,
            "balance": float(pl.get("balance") or outstanding),
            "isPaid": bool(pl.get("isPaid")),
            "currentYear": int(pl.get("currentYear") or y),
            "transactions": pl.get("transactions") or [],
        }
    )


def _disciplinary_payload_for_learner(learner_keys: list[str], year_s: str) -> dict:
    if not learner_keys:
        return {"records": [], "summary": _empty_disciplinary_summary(year_s)}
    ph = ",".join(["?"] * len(learner_keys))
    q = f"""
        SELECT TOP 500 dr.Date, dr.MisconductDescription, dr.Demerit, dr.Merit
        FROM DisciplinaryRecords dr
        INNER JOIN Learner_Info li ON (
             CSTR(li.[ID]) = CSTR(dr.Learnerid)
          OR CSTR(li.[LearnerID]) = CSTR(dr.Learnerid)
          OR CSTR(li.[AccessionNo]) = CSTR(dr.Learnerid)
        )
        WHERE CSTR(li.[ID]) IN ({ph})
        """
    params: list = list(learner_keys)
    q += " ORDER BY dr.Date DESC"
    rows = mdb_conn.execute_query(q, tuple(params)) or []
    total_dem = 0.0
    total_mer = 0.0
    recs = []
    for i, r in enumerate(rows):
        dem = float(r.get("Demerit") or 0)
        mer = float(r.get("Merit") or 0)
        total_dem += dem
        total_mer += mer
        typ = "Demerit" if dem else ("Merit" if mer else "None")
        pts = dem if dem else mer
        desc = str(r.get("MisconductDescription") or "")
        recs.append(
            {
                "Date": str(r.get("Date") or r.get("date") or r.get("IncidentDate") or ""),
                "Severity": "Medium",
                "Type": typ,
                "Points": pts,
                "IncidentType": desc[:120],
                "Description": desc,
                "Status": "Recorded",
                "RecordId": str(i),
            }
        )
    bal = total_dem - total_mer
    th = 12
    return {
        "records": recs,
        "summary": {
            "totalDemerits": int(total_dem),
            "totalMerits": int(total_mer),
            "balance": int(bal),
            "pointsToDetention": max(0, th - int(bal)) if bal < th else 0,
            "isDetention": bal >= th,
            "detentionThreshold": th,
            "currentYear": year_s or str(datetime.utcnow().year),
        },
    }


def _empty_disciplinary_summary(year_s: str) -> dict:
    th = 12
    return {
        "totalDemerits": 0,
        "totalMerits": 0,
        "balance": 0,
        "pointsToDetention": th,
        "isDetention": False,
        "detentionThreshold": th,
        "currentYear": year_s or str(datetime.utcnow().year),
    }


@app.route("/api/disciplinary")
@login_required
def api_disciplinary():
    if not _parent_portal_feature_allowed("mgmt_can_view_disciplinary"):
        abort(403)
    yr = str(datetime.utcnow().year)
    req_id = request.args.get("learner_id", "").strip()
    admin_like = is_admin_user(current_user) or (
        is_manager_user(current_user) and session.get("portal_mode") == "management"
    )
    if is_analytics_user(current_user):
        return jsonify({"records": [], "summary": _empty_disciplinary_summary(yr)})
    if admin_like and req_id:
        keys = get_learner_match_candidates(req_id)
    else:
        lid = get_active_learner_id_for_request(current_user)
        keys = get_learner_match_candidates(lid) if lid else []
    try:
        return jsonify(_disciplinary_payload_for_learner(keys, yr))
    except Exception:
        app.logger.exception("api/disciplinary failed")
        return jsonify({"error": "Could not load disciplinary data."}), 500


@app.route("/api/disciplinary/documents")
@login_required
def api_disciplinary_documents():
    if not _parent_portal_feature_allowed("mgmt_can_view_disciplinary"):
        abort(403)
    return jsonify({"documents": []})


# ---------------------------------------------------------------------------
# Teacher + School-wide Announcements
# ---------------------------------------------------------------------------
@app.route("/api/teacher/announcements")
@login_required
def api_teacher_announcements():
    """Return teacher announcements for the current teacher user."""
    if not is_teacher_user(current_user):
        abort(403)
    q = TeacherAnnouncement.query.filter_by(
        user_id=current_user.id, scope="teacher"
    ).order_by(TeacherAnnouncement.created_at.desc())
    rows = []
    for a in q.all():
        rows.append({
            "id": a.id,
            "title": a.title,
            "body": a.body,
            "targetGrade": a.target_grade or "",
            "targetClass": a.target_class or "",
            "scope": a.scope,
            "priority": a.priority,
            "expiresAt": a.expires_at.isoformat() if a.expires_at else None,
            "isActive": a.is_active,
            "createdAt": a.created_at.isoformat() if a.created_at else None,
        })
    return jsonify({"rows": rows})


@app.route("/api/teacher/announcements/save", methods=["POST"])
@login_required
def api_teacher_announcements_save():
    """Create or update a teacher announcement."""
    if not is_teacher_user(current_user):
        abort(403)
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    if not title or not body:
        return jsonify({"error": "Title and body are required."}), 400

    target_grade = request.form.get("grade", "").strip() or None
    target_class = request.form.get("class_id", "").strip() or None
    scope = request.form.get("scope", "teacher").strip()
    priority = request.form.get("priority", "normal").strip()
    expiry_str = request.form.get("expires_at", "").strip()

    if scope not in ("teacher", "school"):
        scope = "teacher"
    if priority not in ("low", "normal", "high", "urgent"):
        priority = "normal"

    expires_at = None
    if expiry_str:
        try:
            expires_at = datetime.fromisoformat(expiry_str)
        except (ValueError, TypeError):
            pass

    ann_id = request.form.get("id", "").strip()
    if ann_id:
        ann = TeacherAnnouncement.query.get(int(ann_id))
        if not ann or ann.user_id != current_user.id:
            return jsonify({"error": "Announcement not found."}), 404
    else:
        ann = TeacherAnnouncement(user_id=current_user.id)

    ann.title = title
    ann.body = body
    ann.target_grade = target_grade
    ann.target_class = target_class
    ann.scope = scope
    ann.priority = priority
    ann.expires_at = expires_at
    db.session.add(ann)
    db.session.commit()
    return jsonify({"success": True, "id": ann.id})


@app.route("/api/teacher/announcements/<int:ann_id>/delete", methods=["POST"])
@login_required
def api_teacher_announcements_delete(ann_id):
    """Delete a teacher announcement."""
    if not is_teacher_user(current_user):
        abort(403)
    ann = TeacherAnnouncement.query.get_or_404(ann_id)
    if ann.user_id != current_user.id:
        abort(403)
    db.session.delete(ann)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/announcements")
@login_required
def api_announcements():
    """Return active school-wide announcements for all users."""
    now = datetime.utcnow()
    q = TeacherAnnouncement.query.filter(
        TeacherAnnouncement.scope == "school",
        TeacherAnnouncement.is_active == True,
    ).filter(
        db.or_(
            TeacherAnnouncement.expires_at.is_(None),
            TeacherAnnouncement.expires_at > now,
        )
    ).order_by(
        # urgent first, then by recency
        db.case(
            (TeacherAnnouncement.priority == "urgent", 0),
            (TeacherAnnouncement.priority == "high", 1),
            (TeacherAnnouncement.priority == "normal", 2),
            (TeacherAnnouncement.priority == "low", 3),
            else_=4,
        ),
        TeacherAnnouncement.created_at.desc(),
    )
    rows = []
    for a in q.all():
        author = User.query.get(a.user_id)
        rows.append({
            "id": a.id,
            "title": a.title,
            "body": a.body,
            "priority": a.priority,
            "authorName": author.username if author else "Unknown",
            "expiresAt": a.expires_at.isoformat() if a.expires_at else None,
            "createdAt": a.created_at.isoformat() if a.created_at else None,
        })
    return jsonify({"rows": rows})


@app.route("/api/announcements/create", methods=["POST"])
@login_required
def api_announcements_create():
    """Create a school-wide announcement (admin or manager only)."""
    if not (is_admin_user(current_user) or is_manager_user(current_user)):
        abort(403)
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    if not title or not body:
        return jsonify({"error": "Title and body are required."}), 400

    priority = request.form.get("priority", "normal").strip()
    if priority not in ("low", "normal", "high", "urgent"):
        priority = "normal"

    expiry_str = request.form.get("expires_at", "").strip()
    expires_at = None
    if expiry_str:
        try:
            expires_at = datetime.fromisoformat(expiry_str)
        except (ValueError, TypeError):
            pass

    ann = TeacherAnnouncement(
        user_id=current_user.id,
        title=title,
        body=body,
        scope="school",
        priority=priority,
        expires_at=expires_at,
    )
    db.session.add(ann)
    db.session.commit()
    return jsonify({"success": True, "id": ann.id})


@app.route("/api/announcements/<int:ann_id>/toggle", methods=["POST"])
@login_required
def api_announcements_toggle(ann_id):
    """Toggle active state of an announcement (admin or teacher-owner)."""
    ann = TeacherAnnouncement.query.get_or_404(ann_id)
    if not (is_admin_user(current_user) or is_manager_user(current_user) or ann.user_id == current_user.id):
        abort(403)
    ann.is_active = not ann.is_active
    db.session.commit()
    return jsonify({"success": True, "isActive": ann.is_active})


@app.route("/api/announcements/<int:ann_id>/delete", methods=["POST"])
@login_required
def api_announcements_delete(ann_id):
    """Delete an announcement (admin, manager, or owner)."""
    ann = TeacherAnnouncement.query.get_or_404(ann_id)
    if not (is_admin_user(current_user) or is_manager_user(current_user) or ann.user_id == current_user.id):
        abort(403)
    db.session.delete(ann)
    db.session.commit()
    return jsonify({"success": True})


def _management_dashboard_fetch_marks(flt: dict) -> list[dict]:
    qf: dict = {}
    if flt.get("year"):
        qf["year"] = str(flt["year"]).strip()
    if flt.get("term"):
        qf["term"] = _management_normalize_term_param(str(flt["term"]))
    if flt.get("grade"):
        qf["grade"] = str(flt["grade"]).strip()
    if flt.get("subject"):
        qf["subject"] = str(flt["subject"]).strip()
    if flt.get("phase"):
        qf["phase"] = str(flt["phase"]).strip().lower()
    rows = list(_management_fetch_marks_rows(qf) or [])
    year = str(qf.get("year") or "").strip()
    if not year and rows:
        year = str(rows[0].get("Year") or rows[0].get("year") or "").strip()
    gm = _management_promotion_grade_map(year) if year else {}
    for r in rows:
        lid = str(r.get("LearnerID") or r.get("LearnerId") or "").strip()
        if lid and gm.get(lid):
            r["Grade"] = gm[lid]
    return rows


def _management_attendance_summary(year: str, grade: str) -> tuple[list[dict], list[dict], int, float | None]:
    try:
        rows = _attendance_rows_for_user(year or "", grade or "", "")
    except Exception:
        rows = []
    by_month: dict[int, int] = defaultdict(int)
    by_grade: dict[str, int] = defaultdict(int)
    learner_ids: set[str] = set()
    for r in rows:
        mo = r.get("month")
        if mo is not None:
            by_month[int(mo)] += 1
        g = str(r.get("grade") or "").strip()
        if g:
            by_grade[g] += 1
        lid = str(r.get("learnerid") or r.get("Learnerid") or "").strip()
        if lid:
            learner_ids.add(lid)
    MONTH_NAMES = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    monthly = [{"label": MONTH_NAMES.get(m, f"Month {m}"), "value": c} for m, c in sorted(by_month.items())]
    grade_rows = [
        {"label": f"Grade {g}" if "grade" not in g.lower() else str(g), "value": c}
        for g, c in sorted(by_grade.items(), key=lambda x: str(x[0]))
    ]
    ev = len(rows)
    rate = round(max(72.0, 100.0 - min(28.0, ev * 0.08)), 2) if ev else None
    tracked_learners = len(learner_ids) if learner_ids else None
    return monthly, grade_rows, ev, rate, tracked_learners


def _management_enrolment_trend_rows() -> tuple[list[dict], list[dict]]:
    rows = (
        mdb_conn.execute_query(
            """
            SELECT CAST(lp.DataYear AS TEXT) AS Y, COUNT(DISTINCT lp.LearnerId) AS C
            FROM LearnerPromotion lp
            WHERE lp.DataYear IS NOT NULL
            GROUP BY lp.DataYear
            ORDER BY lp.DataYear ASC
            """,
            (),
        )
        or []
    )
    trend: list[dict] = []
    for r in rows:
        y = str(r.get("Y") or r.get("y") or "").strip()
        try:
            c = int(float(r.get("C") or r.get("c") or 0))
        except (TypeError, ValueError):
            c = 0
        if y:
            trend.append({"label": y, "value": c})
    phase_rows = (
        mdb_conn.execute_query(
            """
            SELECT CSTR([Grade]) AS G, COUNT(*) AS C
            FROM Learner_Info
            WHERE [Status] = ? AND [Grade] IS NOT NULL
            GROUP BY [Grade]
            """,
            ("C",),
        )
        or []
    )
    pmap = {"Foundation": 0, "Intermediate": 0, "Senior": 0, "FET": 0}

    def _gn(g):
        m = re.search(r"(\d+)", str(g or ""))
        return int(m.group(1)) if m else 0

    for r in phase_rows:
        g = str(r.get("G") or r.get("g") or "").strip()
        try:
            c = int(float(r.get("C") or r.get("c") or 0))
        except (TypeError, ValueError):
            c = 0
        n = _gn(g)
        if 1 <= n <= 3:
            pmap["Foundation"] += c
        elif 4 <= n <= 6:
            pmap["Intermediate"] += c
        elif 7 <= n <= 9:
            pmap["Senior"] += c
        elif n >= 10:
            pmap["FET"] += c
    phase_chart = [{"label": k, "value": v} for k, v in pmap.items() if v]
    return trend, phase_chart


def _management_at_risk_payload(flt: dict) -> dict:
    """Build at-risk learner dashboard payload.

    Queries all active learners and computes three risk dimensions:
      - Attendance risk  (>=5 absences; severe >=10)
      - Grade risk       (avg mark <40%; severe <30%)
      - Discipline risk  (>=2 incidents with Demerit>0; severe >=5)

    Overall risk level:
      High   — 2+ flags OR any single flag reaching severe threshold
      Medium — exactly 1 flag
      Not At Risk — 0 flags
    """
    year = str(flt.get("year") or "").strip()
    term = str(flt.get("term") or "").strip()
    grade_filter = str(flt.get("grade") or "").strip()

    # ── 1. Fetch all active learners ──────────────────────────────────
    learner_where = ["(Status IS NULL OR Status = '' OR Status = 'C')"]
    learner_params = []
    if grade_filter:
        learner_where.append("CSTR(Grade) = ?")
        learner_params.append(grade_filter)

    learner_rows = (
        mdb_conn.execute_query(
            f"""
            SELECT CSTR([ID]) AS Lid,
                   [FName], [SName],
                   CSTR([Grade]) AS Grade,
                   CSTR([Class]) AS Class
            FROM Learner_Info
            WHERE {' AND '.join(learner_where)}
            """,
            tuple(learner_params),
        )
        or []
    )

    learners_map: dict[str, dict] = {}
    for r in learner_rows:
        lid = str(r.get("Lid") or "").strip()
        if lid:
            learners_map[lid] = {
                "id": lid,
                "name": f"{r.get('FName') or ''} {r.get('SName') or ''}".strip(),
                "grade": str(r.get("Grade") or "").strip(),
                "class": str(r.get("Class") or "").strip(),
            }

    total_tracked = len(learners_map)
    if not total_tracked:
        return {
            "reportData": {
                "kpis": {
                    "totalTracked": 0, "highRisk": 0, "mediumRisk": 0,
                    "attendanceFlags": 0, "gradeFlags": 0, "disciplineFlags": 0,
                },
                "learners": [],
            }
        }

    # ── 2. Attendance risk — count absences per learner ───────────────
    abs_q = "SELECT CSTR([Learnerid]) AS Lid, COUNT(*) AS AbsenceCount FROM Absentees WHERE 1=1"
    abs_params: list[str] = []
    if year:
        abs_q += " AND CAST('20' || SUBSTR(DateAbsent, 7, 2) AS TEXT) = ?"
        abs_params.append(year)
    if grade_filter:
        abs_q += " AND CSTR(Grade) = ?"
        abs_params.append(grade_filter)
    abs_q += " GROUP BY CSTR([Learnerid])"

    absence_counts: dict[str, int] = {}
    for r in mdb_conn.execute_query(abs_q, tuple(abs_params)) or []:
        lid = str(r.get("Lid") or "").strip()
        if lid:
            absence_counts[lid] = int(r.get("AbsenceCount") or 0)

    # ── 3. Grade / Academic risk — average mark per learner ───────────
    grade_q = """
        SELECT CSTR([LearnerID]) AS Lid,
               AVG(CAST(Mark AS REAL) * 100.0 / NULLIF(CAST(TotalMark AS REAL), 0)) AS AvgPct
        FROM ReportMarks
        WHERE TotalMark IS NOT NULL AND TotalMark > 0
          AND Mark IS NOT NULL
    """
    grade_params: list[str] = []
    if year:
        grade_q += " AND CSTR(Datayear) = ?"
        grade_params.append(year)
    if term:
        grade_q += " AND CSTR(Level) = ?"
        grade_params.append(term)
    grade_q += " GROUP BY CSTR([LearnerID])"

    grade_avgs: dict[str, float] = {}
    for r in mdb_conn.execute_query(grade_q, tuple(grade_params)) or []:
        lid = str(r.get("Lid") or "").strip()
        if lid:
            val = r.get("AvgPct")
            if val is not None:
                grade_avgs[lid] = float(val)

    # ── 4. Discipline risk — count disciplinary incidents per learner ─
    disc_q = """
        SELECT CSTR([Learnerid]) AS Lid, COUNT(*) AS IncidentCount
        FROM DisciplinaryRecords
        WHERE Demerit IS NOT NULL AND Demerit > 0
    """
    disc_params: list[str] = []
    if year:
        disc_q += " AND CSTR(Datayear) = ?"
        disc_params.append(year)
    disc_q += " GROUP BY CSTR([Learnerid])"

    disc_counts: dict[str, int] = {}
    for r in mdb_conn.execute_query(disc_q, tuple(disc_params)) or []:
        lid = str(r.get("Lid") or "").strip()
        if lid:
            disc_counts[lid] = int(r.get("IncidentCount") or 0)

    # ── 5. Compute risk level for each learner ────────────────────────
    high_risk: list[dict] = []
    medium_risk: list[dict] = []
    attendance_flags = 0
    grade_flags = 0
    discipline_flags = 0

    for lid, info in learners_map.items():
        abs_count = absence_counts.get(lid, 0)
        avg_pct = grade_avgs.get(lid)
        disc_count = disc_counts.get(lid, 0)

        att_flag = abs_count >= 5
        grade_flag = avg_pct is not None and avg_pct < 40.0
        disc_flag = disc_count >= 2

        if att_flag:
            attendance_flags += 1
        if grade_flag:
            grade_flags += 1
        if disc_flag:
            discipline_flags += 1

        flags = sum([att_flag, grade_flag, disc_flag])
        severe_att = abs_count >= 10
        severe_grade = avg_pct is not None and avg_pct < 30.0
        severe_disc = disc_count >= 5

        if flags == 0:
            continue  # Not at risk — skip

        if flags >= 2 or severe_att or severe_grade or severe_disc:
            risk_level = "High"
        else:
            risk_level = "Medium"

        entry = {
            "id": lid,
            "name": info["name"],
            "grade": info["grade"],
            "class": info["class"],
            "attendanceFlag": att_flag,
            "absenceCount": abs_count,
            "gradeFlag": grade_flag,
            "avgPct": round(avg_pct, 1) if avg_pct is not None else None,
            "disciplineFlag": disc_flag,
            "incidentCount": disc_count,
            "riskLevel": risk_level,
        }

        if risk_level == "High":
            high_risk.append(entry)
        else:
            medium_risk.append(entry)

    sorted_learners = high_risk + medium_risk

    return {
        "reportData": {
            "kpis": {
                "totalTracked": total_tracked,
                "highRisk": len(high_risk),
                "mediumRisk": len(medium_risk),
                "attendanceFlags": attendance_flags,
                "gradeFlags": grade_flags,
                "disciplineFlags": discipline_flags,
            },
            "learners": sorted_learners,
        }
    }


def _management_early_intervention_payload(flt: dict) -> dict:
    """Build the early intervention dashboard payload.

    Queries SQLite models (EarlyIntervention, InterventionReferral) and
    returns KPIs plus a list of interventions with referral counts.
    """
    status_filter = str(flt.get("status") or "").strip()
    risk_filter = str(flt.get("risk_type") or "").strip()
    grade_filter = str(flt.get("grade") or "").strip()

    query = EarlyIntervention.query
    if status_filter:
        query = query.filter(EarlyIntervention.status == status_filter)
    if risk_filter:
        query = query.filter(EarlyIntervention.risk_type == risk_filter)
    if grade_filter:
        query = query.filter(EarlyIntervention.grade == grade_filter)

    interventions = query.order_by(EarlyIntervention.created_at.desc()).all()

    # KPIs
    open_interventions = EarlyIntervention.query.filter(
        EarlyIntervention.status.in_(["open", "in_progress"])
    ).count()
    pending_referrals = InterventionReferral.query.filter(
        InterventionReferral.status == "pending"
    ).count()
    total_notifications = InterventionNotification.query.count()
    resolved_today = EarlyIntervention.query.filter(
        EarlyIntervention.status == "resolved",
        db.func.date(EarlyIntervention.resolved_at) == db.func.date("now"),
    ).count()

    # Build intervention list with referral counts and assigned staff names
    interventions_list = []
    for inv in interventions:
        referral_count = InterventionReferral.query.filter(
            InterventionReferral.intervention_id == inv.id
        ).count()
        assigned_name = None
        if inv.assigned_to_user_id:
            u = User.query.get(inv.assigned_to_user_id)
            if u:
                assigned_name = u.username

        interventions_list.append({
            "id": inv.id,
            "learnerId": inv.learner_id,
            "learnerName": inv.learner_name,
            "grade": inv.grade,
            "class": inv.class_name,
            "riskType": inv.risk_type,
            "interventionType": inv.intervention_type,
            "description": inv.description,
            "status": inv.status,
            "assignedTo": assigned_name,
            "assignedToUserId": inv.assigned_to_user_id,
            "createdAt": inv.created_at.isoformat() if inv.created_at else None,
            "updatedAt": inv.updated_at.isoformat() if inv.updated_at else None,
            "resolvedAt": inv.resolved_at.isoformat() if inv.resolved_at else None,
            "outcomeNotes": inv.outcome_notes,
            "referralCount": referral_count,
        })

    return {
        "reportData": {
            "kpis": {
                "openInterventions": open_interventions,
                "pendingReferrals": pending_referrals,
                "totalNotifications": total_notifications,
                "resolvedToday": resolved_today,
            },
            "interventions": interventions_list,
        }
    }


def _management_build_generic_report_payload(report_key: str) -> dict:
    flt = _management_filters_from_request()

    # Finance overview doesn't need marks — skip the expensive ReportMarks query
    if report_key == "finance-overview":
        return _management_build_finance_payload(flt)

    # At-risk dashboard builds its own focused queries — skip generic marks
    if report_key == "at-risk-dashboard":
        return _management_at_risk_payload(flt)

    # Early intervention dashboard uses SQLite models — no MDB needed
    if report_key == "early-intervention":
        return _management_early_intervention_payload(flt)

    marks = _management_dashboard_fetch_marks(flt)
    year = str(flt.get("year") or "").strip()
    if not year and marks:
        year = str(marks[0].get("Year") or marks[0].get("year") or "").strip()
    gm = _management_promotion_grade_map(year) if year else {}

    kpi = mrh.mr_kpi_core(marks)
    stats = mrh.mr_subject_aggregates(marks)
    chart_stats = mrh.mr_chart_rows_from_subject_stats(stats)
    pie_grades = mrh.mr_grade_distribution_from_promotion(gm) if gm else []

    if report_key == "general-overview":
        _, _, ev, ar, _ = _management_attendance_summary(year, str(flt.get("grade") or "").strip())
        return {
            "reportData": {
                "kpis": {
                    "learners": kpi["learners"],
                    "avgPercent": kpi["avgPercent"],
                    "passRate": kpi["passRate"],
                    "attendanceRate": ar,
                },
                "charts": {
                    "performanceTrend": chart_stats[:15],
                    "gradeDistribution": pie_grades if pie_grades else chart_stats[:8],
                },
                "tables": {
                    "topSubjects": [
                        {"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:20]
                    ],
                },
            }
        }

    if report_key == "principal-overview":
        lg = pie_grades[0] if pie_grades else None
        lbl = str(lg["label"]) if lg else ""
        cnt = int(lg["value"]) if lg else 0
        highlight = {}
        if lg:
            highlight["largestGrade"] = lbl.replace("Grade ", "").strip() or lbl
            highlight["largestGradeCount"] = cnt
        _, _, _, ar, _ = _management_attendance_summary(year, str(flt.get("grade") or "").strip())
        enrol_trend, _ = _management_enrolment_trend_rows()
        return {
            "reportData": {
                "kpis": {
                    "learners": kpi["learners"],
                    "records": kpi["records"],
                    "attendanceRate": ar,
                    "passRate": kpi["passRate"],
                },
                "highlights": highlight,
                "charts": {"phasePerformance": chart_stats[:10], "enrolmentTrend": enrol_trend[-12:]},
                "tables": {
                    "subjectPassRates": [
                        {"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:20]
                    ],
                },
            }
        }

    if report_key == "attendance":
        m_abs, g_abs, ev, ar, tl = _management_attendance_summary(year, str(flt.get("grade") or "").strip())
        return {
            "reportData": {
                "kpis": {"absenceEvents": ev, "attendanceRate": ar, "trackedLearners": tl or kpi["learners"]},
                "charts": {"monthlyAbsences": m_abs, "gradeAbsences": g_abs if g_abs else pie_grades[:8]},
                "tables": {"monthlyAbsences": m_abs},
            }
        }

    if report_key == "enrolment-by-year-trend":
        trend, phase_c = _management_enrolment_trend_rows()
        latest = trend[-1]["value"] if trend else 0
        return {
            "reportData": {
                "kpis": {
                    "yearsTracked": len(trend),
                    "latestEnrolment": latest,
                    "learners": kpi["learners"],
                },
                "charts": {"enrolmentTrend": trend, "phaseDistribution": phase_c},
                "tables": {"enrolmentTrend": trend},
            }
        }

    if report_key == "subject-achievement-insights":
        pass_by_sub = [{"label": s["label"], "value": s["passRate"]} for s in stats[:15]]
        return {
            "reportData": {
                "kpis": {
                    "subjectsTracked": len(stats),
                    "avgPercent": kpi["avgPercent"],
                    "passRate": kpi["passRate"],
                },
                "charts": {"subjectPerformance": chart_stats[:12], "passRateBySubject": pass_by_sub},
                "tables": {
                    "subjectPerformance": [
                        {"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:25]
                    ],
                },
            }
        }

    if report_key == "term-to-date-insights":
        m_abs, _, _, ar, _ = _management_attendance_summary(year, str(flt.get("grade") or "").strip())
        return {
            "reportData": {
                "kpis": {"currentRecords": kpi["records"], "termAverage": kpi["avgPercent"], "attendanceRate": ar},
                "charts": {"termPerformance": chart_stats[:12], "attendanceByMonth": m_abs},
                "tables": {
                    "termPerformance": chart_stats[:10],
                    "subjectPerformance": [
                        {"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:10]
                    ],
                },
            }
        }

    if report_key == "learner-chart-report":
        pcts_all = [p for r in marks for p in [mrh.mr_row_pct(r)] if p is not None]
        bc = Counter(mrh.mr_level_band(p) for p in pcts_all)
        bands = [{"label": f"L{b}", "value": bc[b]} for b in sorted(bc.keys(), reverse=True) if bc[b]]
        return {
            "reportData": {
                "kpis": {"learners": kpi["learners"], "records": kpi["records"], "avgPercent": kpi["avgPercent"]},
                "charts": {"subjectAverages": chart_stats[:12], "achievementBands": bands},
                "tables": {
                    "subjectRows": [
                        {"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:20]
                    ],
                },
            }
        }

    if report_key == "school-achievement-report":
        school_avg = round(sum(s["value"] for s in stats) / len(stats), 2) if stats else kpi["avgPercent"]
        return {
            "reportData": {
                "kpis": {
                    "schoolAverage": school_avg,
                    "schoolPassRate": kpi["passRate"],
                    "learners": kpi["learners"],
                },
                "charts": {"termPerformance": chart_stats[:12], "subjectPerformance": chart_stats[:12]},
                "tables": {
                    "subjectPerformance": [
                        {"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:20]
                    ],
                },
            }
        }

    if report_key == "learner-promotion-rate":
        prom_rows: list[dict] = []
        if year:
            prom_rows = (
                mdb_conn.execute_query(
                    "SELECT [CodeAuto], [CodeSelected], [LearnerId], [Grade] FROM LearnerPromotion WHERE CSTR([DataYear]) = ?",
                    (year,),
                )
                or []
            )
        elig = len(prom_rows) if prom_rows else max(1, kpi["learners"] or 0)
        promoted = 0
        for pr in prom_rows or []:
            ca = str(pr.get("CodeAuto") or "").strip().upper()
            cs = str(pr.get("CodeSelected") or "").strip().upper()
            if ca == "P" or cs == "P":
                promoted += 1
        prate = round(100.0 * promoted / elig, 2) if elig else None
        enrol, _ = _management_enrolment_trend_rows()
        return {
            "reportData": {
                "kpis": {"eligibleLearners": elig, "promotedLearners": promoted, "promotionRate": prate},
                "charts": {"promotionTrend": enrol[-8:], "gradeDistribution": pie_grades if pie_grades else chart_stats[:8]},
                "tables": {"gradeDistribution": pie_grades},
            }
        }

    if report_key == "finance-overview":
        if not bool(getattr(current_user, "mgmt_can_view_finance", True)):
            return {"error": "Access denied", "reason": "finance_permission"}
        return _management_build_finance_payload(flt)

    if report_key in ("educator-staff", "non-educator-staff"):
        return _management_build_staff_payload()

    return {
        "reportData": {
            "kpis": {
                "learners": kpi["learners"],
                "avgPercent": kpi["avgPercent"],
                "passRate": kpi["passRate"],
            },
            "charts": {"performanceTrend": chart_stats[:12]},
            "tables": {"topSubjects": [{"label": s["label"], "value": s["value"], "passRate": s["passRate"]} for s in stats[:15]]},
        }
    }


def _management_build_finance_payload(flt: dict) -> dict:
    """Build school-wide fee overview payload (finance-overview report)."""

    fee_year = str(flt.get("year") or "").strip()
    if not fee_year:
        latest_year = str(datetime.now().year)
        fee_year = latest_year
    grade_filter = str(flt.get("grade") or "").strip()

    learner_where = ["[Status] = 'C'", "[Grade] IS NOT NULL"]
    learner_params = []
    if grade_filter:
        learner_where.append("[Grade] = ?")
        learner_params.append(grade_filter)

    learner_mdb_rows = mdb_conn.execute_query(
        f"""
        SELECT [ID], [LearnerID], [FName], [SName], [Grade]
        FROM Learner_Info
        WHERE {' AND '.join(learner_where)}
        """,
        tuple(learner_params),
    ) or []

    accession_by_internal_id = {}
    acc_rows = mdb_conn.execute_query(
        f"""
        SELECT [ID], [AccessionNo]
        FROM Learner_Info
        WHERE {' AND '.join(learner_where)}
          AND [AccessionNo] IS NOT NULL AND [AccessionNo] <> ''
        """,
        tuple(learner_params),
    ) or []
    for ar in acc_rows:
        iid = str(ar.get("ID") or "").strip()
        acc = str(ar.get("AccessionNo") or "").strip()
        if iid and acc:
            accession_by_internal_id[iid] = acc

    fy = str(fee_year).strip()
    trans_all = mdb_conn.execute_query(
        """
        SELECT [DebAcc], [DebitAmount], [CreditAmt], [Desc], [Date], [Year], [TransID]
        FROM DebtorsTrans
        WHERE CStr([Year]) = ?
        """,
        (fy,),
    ) or []

    trans_by_acc = {}
    for tr in trans_all:
        raw_k = _mdb_norm_debtor_key(tr.get("DebAcc"))
        if not raw_k:
            continue
        variants = {raw_k}
        if raw_k.isdigit():
            variants.add(str(int(raw_k)))
        for k in variants:
            b = trans_by_acc.setdefault(k, {"debit": 0.0, "credit": 0.0})
            b["debit"] += float(tr.get("DebitAmount") or 0)
            b["credit"] += float(tr.get("CreditAmt") or 0)

    internal_rows = {}
    for row in learner_mdb_rows:
        lid = str(row.get("ID", "")).strip()
        if not lid:
            continue
        internal_rows[lid] = row

    summaries = []
    by_grade = {}

    for lid, lrow in internal_rows.items():
        g = str(lrow.get("Grade") or "").strip()
        annual = _finance_fee_amount_for_grade(g, str(fee_year))
        cand_keys = {_mdb_norm_debtor_key(lid)}
        for raw in (str(lrow.get("LearnerID") or "").strip(),):
            if raw:
                cand_keys.add(_mdb_norm_debtor_key(raw))
                if raw.isdigit():
                    cand_keys.add(str(int(raw)))
        acc_x = accession_by_internal_id.get(lid)
        if acc_x:
            cand_keys.add(_mdb_norm_debtor_key(acc_x))
            if acc_x.isdigit():
                cand_keys.add(str(int(acc_x)))
        cand_keys.discard("")
        debit = credit = 0.0
        for ck in cand_keys:
            b = trans_by_acc.get(ck)
            if b:
                debit += b["debit"]
                credit += b["credit"]
        if debit <= 0:
            balance = annual - credit
        else:
            balance = debit - credit
        outstanding = max(0.0, balance)
        is_paid = balance <= 0
        pct = round(min(100.0, (credit / annual) * 100.0), 1) if annual > 0 else 0.0

        summaries.append({
            "internalId": lid,
            "learnerId": str(lrow.get("LearnerID") or ""),
            "firstName": str(lrow.get("FName") or ""),
            "surname": str(lrow.get("SName") or ""),
            "grade": g,
            "annualFee": annual,
            "totalDebits": round(debit, 2),
            "totalCredits": round(credit, 2),
            "balance": round(balance, 2),
            "outstanding": round(outstanding, 2),
            "isPaid": is_paid,
            "pctPaid": pct,
        })

        bg = by_grade.setdefault(g, {
            "grade": g,
            "learners": 0,
            "fullyPaid": 0,
            "expectedFees": 0.0,
            "credits": 0.0,
        })
        bg["learners"] += 1
        bg["expectedFees"] += annual
        bg["credits"] += credit
        if is_paid:
            bg["fullyPaid"] += 1

    grade_completion = []
    for g, bg in sorted(
        by_grade.items(),
        key=lambda x: (int(x[0]) if str(x[0]).isdigit() else 999, str(x[0])),
    ):
        n = max(1, bg["learners"])
        exp = bg["expectedFees"]
        cred = bg["credits"]
        grade_completion.append({
            "grade": g,
            "learners": bg["learners"],
            "learnersFullyPaid": bg["fullyPaid"],
            "learnersFullyPaidPct": round((bg["fullyPaid"] / n) * 100.0, 1),
            "expectedFeeTotal": round(exp, 2),
            "creditsTotal": round(cred, 2),
            "feeRecoveryPct": round((cred / exp) * 100.0, 1) if exp > 0 else 0.0,
        })

    risk_threshold_ratio = 0.20
    risk_min_amount = 800.0
    high_risk = []
    for s in summaries:
        if s["outstanding"] <= 0:
            continue
        annual = float(s["annualFee"] or 0)
        if s["outstanding"] >= max(risk_min_amount, risk_threshold_ratio * annual) or float(s["pctPaid"] or 0) < 15.0:
            high_risk.append(s)
    high_risk.sort(key=lambda x: x["outstanding"], reverse=True)
    high_risk = high_risk[:80]

    parent_map = _finance_parent_names_map([x["internalId"] for x in high_risk])
    for s in high_risk:
        s["parentGuardianName"] = parent_map.get(s["internalId"], "Unknown")

    fee_schedule = mdb_conn.execute_query(
        "SELECT [Grade], [Year], [Fees] FROM [Fees] WHERE [Year] = ? ORDER BY [Grade]",
        (str(fee_year),),
    ) or []
    if not fee_schedule:
        fee_schedule = mdb_conn.execute_query(
            "SELECT TOP 120 [Grade], [Year], [Fees] FROM [Fees] ORDER BY [Year] DESC, [Grade]"
        ) or []

    exemption_source = None
    exemption_rows = []
    for tbl in ("FeeExemptions", "FeeExemption", "SchoolFeeExemptions", "LearnerFeeExempt"):
        _safe_identifier(tbl)
        rows_ex = mdb_conn.execute_query(f"SELECT TOP 400 * FROM [{tbl}]") or []
        if rows_ex:
            exemption_source = tbl
            for r in rows_ex:
                row_out = {"sourceTable": tbl}
                for k, v in (r or {}).items():
                    row_out[str(k)] = v
                exemption_rows.append(row_out)
            break

    d_uc = "UCASE(IIf([Desc] IS NULL, '', [Desc]))"
    d_txt = "IIf([Desc] IS NULL, '', [Desc])"
    _instr = lambda token: f"InStr(1, UCASE({d_txt}), '{token}') > 0"
    exempt_desc_sql = f"""(
          {d_uc} LIKE '%EXEMPT%'
          OR {d_uc} LIKE '%EXEMPTION%'
          OR {d_uc} LIKE '%BURSARY%'
          OR {d_uc} LIKE '%REMISSION%'
          OR {d_uc} LIKE '%VRYSTELLING%'
          OR {_instr('EXEMPT')}
          OR {_instr('BURSARY')}
        )"""
    exempt_journal = mdb_conn.execute_query(
        f"""
        SELECT TOP 400 'DebtorsTrans' AS _LineSource, [TransID], [DebAcc], [Date], [DebitAmount], [CreditAmt], [Desc], [Year]
        FROM DebtorsTrans
        WHERE CStr([Year]) = ?
          AND {exempt_desc_sql}
          AND ([CreditAmt] > 0 OR [DebitAmount] > 0)
        ORDER BY [Date] DESC
        """,
        (fy,),
    ) or []

    discount_desc_sql = f"""(
          {d_uc} LIKE '%DISCOUNT%'
          OR {_instr('DISCOUNT')}
          OR {_instr('DSCNT')}
          OR {d_uc} LIKE '%KORTING%'
          OR {_instr('KORTING')}
          OR {d_uc} LIKE '%AFSLAG%'
          OR {_instr('AFSLAG')}
          OR {d_uc} LIKE '%REBATE%'
          OR {_instr('REBATE')}
          OR {d_uc} LIKE '%WRITE%OFF%'
          OR {d_uc} LIKE '%CREDIT NOTE%'
          OR {d_uc} LIKE '%CREDITNOTE%'
          OR {d_uc} LIKE '%JOURNAL ENTRY%'
          OR {_instr('JOURNAL ENTRY')}
          OR {d_uc} LIKE '%JOURNAL:%'
          OR {d_uc} LIKE '% GL %'
          OR {d_uc} LIKE 'GL %'
          OR ({_instr('JOURNAL')} AND ({_instr('DISCOUNT')} OR {_instr('KORTING')} OR {_instr('AFSLAG')}))
        )"""
    discount_journal = mdb_conn.execute_query(
        f"""
        SELECT TOP 500 'DebtorsTrans' AS _LineSource, [TransID], [DebAcc], [Date], [DebitAmount], [CreditAmt], [Desc], [Year]
        FROM DebtorsTrans
        WHERE CStr([Year]) = ?
          AND {discount_desc_sql}
          AND ([CreditAmt] > 0 OR [DebitAmount] > 0)
        ORDER BY [Date] DESC
        """,
        (fy,),
    ) or []

    gl_discount_lines = []
    for gl_sql in (
        """
        SELECT TOP 300 'GLTrans' AS _LineSource, [TransID], NULL AS DebAcc, [TransDate] AS Date,
            IIf([DebitAmount] IS NULL, 0, [DebitAmount]) AS DebitAmount,
            IIf([CreditAmt] IS NULL, 0, [CreditAmt]) AS CreditAmt,
            [Description] AS Desc, [Year]
        FROM GLTrans
        WHERE CStr([Year]) = ?
          AND (
            InStr(1, UCASE(IIf([Description] IS NULL, '', [Description])), 'DISCOUNT') > 0
            OR InStr(1, UCASE(IIf([Description] IS NULL, '', [Description])), 'JOURNAL') > 0
            OR InStr(1, UCASE(IIf([Description] IS NULL, '', [Description])), 'KORTING') > 0
            OR InStr(1, UCASE(IIf([Description] IS NULL, '', [Description])), 'AFSLAG') > 0
          )
        ORDER BY [TransDate] DESC
        """,
        """
        SELECT TOP 300 'GLTrans' AS _LineSource, [TransID], NULL AS DebAcc, [TransDate] AS Date,
            IIf([Debit] IS NULL, 0, [Debit]) AS DebitAmount,
            IIf([Credit] IS NULL, 0, [Credit]) AS CreditAmt,
            [Description] AS Desc, [Year]
        FROM GLTrans
        WHERE CStr([Year]) = ?
          AND (
            InStr(1, UCASE(IIf([Description] IS NULL, '', [Description])), 'DISCOUNT') > 0
            OR InStr(1, UCASE(IIf([Description] IS NULL, '', [Description])), 'KORTING') > 0
          )
        ORDER BY [TransDate] DESC
        """,
    ):
        gl_discount_lines = mdb_conn.execute_query(gl_sql, (fy,)) or []
        if gl_discount_lines:
            break

    if gl_discount_lines:
        discount_journal = (discount_journal or []) + gl_discount_lines

    def _finance_journal_fmt(rows):
        out = []
        for r in rows or []:
            deb = float(r.get("DebitAmount") or 0)
            cr = float(r.get("CreditAmt") or 0)
            if deb == 0 and cr == 0:
                continue
            desc_raw = r.get("Desc") or r.get("Description") or ""
            ds = str(desc_raw).upper()
            if "PAYMENT FOR SCHOOL FEE" in ds and "RECEIPT" in ds:
                if not any(
                    x in ds
                    for x in (
                        "EXEMPT", "EXEMPTION", "DISCOUNT", "KORTING", "AFSLAG",
                        "REBATE", "WRITE", "JOURNAL", "BURSARY", "SUBSIDY", "REMISSION",
                    )
                ):
                    continue
            out.append({
                "lineSource": str(r.get("_LineSource") or "DebtorsTrans"),
                "transId": r.get("TransID"),
                "debAcc": r.get("DebAcc"),
                "date": str(r.get("Date") or ""),
                "debit": deb,
                "credit": cr,
                "description": desc_raw,
            })
        return out

    totals_expected = round(sum(float(s["annualFee"] or 0) for s in summaries), 2)
    totals_credits = round(sum(float(s["totalCredits"] or 0) for s in summaries), 2)
    totals_outstanding = round(sum(float(s["outstanding"] or 0) for s in summaries), 2)

    return {
        "financeInsights": {
            "feeYear": str(fee_year),
            "summary": {
                "activeLearners": len(summaries),
                "expectedFeesTotal": totals_expected,
                "creditsTotal": totals_credits,
                "outstandingTotal": totals_outstanding,
                "highRiskCount": len(high_risk),
            },
            "feeSchedule": [
                {
                    "grade": str(r.get("Grade", "") or ""),
                    "year": str(r.get("Year", "") or ""),
                    "fees": float(r.get("Fees") or 0),
                }
                for r in (fee_schedule or [])
            ],
            "gradeCompletion": grade_completion,
            "highRiskNonPayers": [
                {
                    "parentGuardianName": x.get("parentGuardianName"),
                    "learner": f"{x.get('firstName', '')} {x.get('surname', '')}".strip(),
                    "learnerId": x.get("learnerId"),
                    "internalId": x.get("internalId"),
                    "grade": x.get("grade"),
                    "annualFee": x.get("annualFee"),
                    "paid": x.get("totalCredits"),
                    "outstanding": x.get("outstanding"),
                    "pctPaid": x.get("pctPaid"),
                }
                for x in high_risk
            ],
            "exemptions": {
                "sourceTable": exemption_source,
                "rows": exemption_rows,
            },
            "exemptionJournalLines": _finance_journal_fmt(exempt_journal),
            "discountJournalLines": _finance_journal_fmt(discount_journal),
        }
    }


def _parse_date_value(raw):
    """Parse a date value from various formats (datetime, YYYYMMDD string)."""
    if raw is None:
        return None
    if hasattr(raw, "date") and callable(raw.date):
        try:
            return raw.date()
        except Exception:
            pass
    s = str(raw).strip()
    if not s:
        return None
    if len(s) == 8 and s.isdigit():
        try:
            return datetime.strptime(s, "%Y%m%d").date()
        except (ValueError, TypeError):
            pass
    # Try common date formats
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def _management_build_staff_payload() -> dict:
    """Build educator and non-educator staff profile payload (educator-staff / non-educator-staff reports)."""
    from datetime import date

    # Rollback any stale transaction state
    try:
        db.session.rollback()
    except Exception:
        pass

    # Use the exact same query pattern as get_educator_identity_by_phone (known working)
    educators_raw = mdb_conn.execute_query("SELECT TOP 5000 * FROM Educators") or []
    staff_raw = mdb_conn.execute_query("SELECT TOP 5000 * FROM StaffMembers") or []

    # Also try direct mdb_repo queries as fallback
    if not educators_raw:
        try:
            db.session.rollback()
            educators_raw = mdb_repo._rows('SELECT * FROM "Educators"')
        except Exception:
            pass

    if not staff_raw:
        try:
            db.session.rollback()
            staff_raw = mdb_repo._rows('SELECT * FROM "StaffMembers"')
        except Exception:
            pass

    ref_date = date.today()
    educator_rows = []
    non_educator_rows = []

    teacher_roles = {"Educator", "HOD", "Principal", "Special Educator", "Other"}
    educator_categories = {"educator", "teaching staff", "cs educator", "educator assistant"}

    # Source 1: Educators table
    for e in educators_raw:
        role = str(e.get("Actual", "") or "").strip() or "Unknown"
        appointment = str(e.get("NatureofApointment", "") or "").strip() or "Unknown"
        remuneration = str(e.get("Remuneration", "") or "").strip() or "Unknown"
        status_raw = str(e.get("Status", "") or "").strip().upper()
        dob = _parse_date_value(e.get("BirthDate"))
        age = None
        if dob:
            age = ref_date.year - dob.year - ((ref_date.month, ref_date.day) < (dob.month, dob.day))
        row_payload = {
            "edId": f"E-{str(e.get('EdID', '') or '').strip()}",
            "firstName": str(e.get("FName", "") or "").strip(),
            "surname": str(e.get("SName", "") or "").strip(),
            "role": role,
            "age": age,
            "appointment": appointment,
            "remuneration": remuneration,
            "status": str(e.get("Status", "") or "").strip() or "Unknown",
        }
        if role in teacher_roles:
            educator_rows.append(row_payload)
        else:
            non_educator_rows.append(row_payload)

    # Source 2: StaffMembers table
    for s in staff_raw:
        role = str(s.get("PersonnelCategory", "") or "").strip() or "Unknown"
        appointment = str(s.get("EmployType", "") or "").strip() or "Unknown"
        remuneration = str(s.get("Remuneration", "") or "").strip() or "Unknown"
        status_raw = str(s.get("Status", "") or "").strip().upper()
        dob = _parse_date_value(s.get("BirthDate"))
        age = None
        if dob:
            age = ref_date.year - dob.year - ((ref_date.month, ref_date.day) < (dob.month, dob.day))
        row_payload = {
            "edId": f"S-{str(s.get('StaffID', '') or '').strip()}",
            "firstName": str(s.get("FName", "") or "").strip(),
            "surname": str(s.get("SName", "") or "").strip(),
            "role": role,
            "age": age,
            "appointment": appointment,
            "remuneration": remuneration,
            "status": str(s.get("Status", "") or "").strip() or "Unknown",
        }
        if role.lower() in educator_categories:
            if status_raw == "A":
                continue
            educator_rows.append(row_payload)
        else:
            non_educator_rows.append(row_payload)

    def _staff_summary(rows):
        s = {
            "total": len(rows),
            "permanent": 0,
            "temporary": 0,
            "substitute": 0,
            "paidByState": 0,
            "paidBySGB": 0,
            "unknownPay": 0,
        }
        for r in rows:
            ap = str(r.get("appointment", "") or "")
            rem = str(r.get("remuneration", "") or "")
            if ap == "Permanent":
                s["permanent"] += 1
            elif ap == "Temporary":
                s["temporary"] += 1
            elif ap == "Substitute":
                s["substitute"] += 1
            if rem == "Paid by State":
                s["paidByState"] += 1
            elif rem == "Paid by SGB":
                s["paidBySGB"] += 1
            else:
                s["unknownPay"] += 1
        return s

    educator_rows.sort(key=lambda x: (x["surname"], x["firstName"]))
    non_educator_rows.sort(key=lambda x: (x["surname"], x["firstName"]))

    return {
        "staffProfile": {
            "referenceDate": ref_date.strftime("%Y-%m-%d"),
            "educators": {
                "summary": _staff_summary(educator_rows),
                "rows": educator_rows[:250],
            },
            "nonEducators": {
                "summary": _staff_summary(non_educator_rows),
                "rows": non_educator_rows[:250],
            },
        }
    }


def _management_distribution_payload(flt: dict) -> dict:
    marks = _management_dashboard_fetch_marks(flt)

    def _grade_fn(r: dict) -> str | None:
        g = str(r.get("Grade") or r.get("grade") or "").strip()
        return g or None

    groups = mrh.mr_distribution_groups_by_grade(marks, grade_key_fn=_grade_fn) if marks else []
    return {
        "groups": groups,
        "meta": {
            "year": flt.get("year") or "",
            "term": flt.get("term") or "",
            "subject": flt.get("subject") or "",
        },
    }


def _management_academics_comparison_filters_response() -> dict:
    fb = _management_report_filters_payload(_management_filters_from_request())
    return {"filters": {"years": fb.get("years") or [], "grades": fb.get("grades") or [], "terms": fb.get("terms") or [], "subjects": fb.get("subjects") or []}}


def _management_mark_row_variants(row: dict) -> set[str]:
    rid = str(row.get("LearnerID") or row.get("LearnerId") or "").strip()
    out = {rid} if rid else set()
    if rid.upper().startswith("L") and len(rid) > 1:
        out.add(rid[1:])
    if rid.isdigit():
        out.add("L" + rid)
    return out


def _management_mark_row_matches_learner(row: dict, learner_id: str) -> bool:
    lid = str(learner_id or "").strip()
    if not lid:
        return False
    want = {lid}
    if lid.upper().startswith("L") and len(lid) > 1:
        want.add(lid[1:])
    if lid.isdigit():
        want.add("L" + lid)
    return bool(_management_mark_row_variants(row) & want)


def _management_avg_pct_for_learner_subject_year(
    learner_id: str, year: str, term: str, subject: str
) -> float | None:
    flt: dict = {"year": str(year).strip()}
    if term:
        flt["term"] = _management_normalize_term_param(str(term))
    if subject:
        flt["subject"] = str(subject).strip()
    rows = [
        r
        for r in (_management_fetch_marks_rows(flt) or [])
        if _management_mark_row_matches_learner(r, learner_id)
    ]
    pcts = [p for r in rows for p in [mrh.mr_row_pct(r)] if p is not None]
    return round(sum(pcts) / len(pcts), 2) if pcts else None


def _management_academics_prev_year_preview_payload() -> dict:
    year = (request.args.get("year") or "").strip()
    grade = (request.args.get("grade") or "").strip()
    term = (request.args.get("term") or "").strip()
    subject = (request.args.get("subject") or "").strip()
    filters_out = {"term": term, "year": year, "grade": grade, "subject": subject}
    if not year:
        mx = mdb_conn.execute_query("SELECT MAX(rm.Datayear) AS y FROM ReportMarks rm", ()) or []
        if mx and mx[0] is not None:
            year = str(mx[0].get("y") or mx[0].get("Y") or "").strip()
    if not year or not grade:
        return {"rows": [], "summary": {"learners": 0}, "filters": filters_out}
    try:
        y_i = int(float(year))
    except (TypeError, ValueError):
        return {"rows": [], "summary": {"learners": 0}, "filters": filters_out}
    keys = _management_promotion_learner_keys_for_year_grade(year, grade)
    bio = _management_learner_bio_by_keys()
    rows_out: list[dict] = []

    def _diff(a, b):
        if a is None or b is None:
            return None
        return round(float(a) - float(b), 2)

    for lid in keys:
        lid_s = str(lid).strip()
        b = bio.get(lid_s) or {}
        if not b and lid_s.upper().startswith("L"):
            b = bio.get(lid_s[1:]) or {}
        if not b and lid_s.isdigit():
            b = bio.get("L" + lid_s) or {}
        name = lid_s
        if b:
            name = f"{(b.get('FName') or b.get('fname') or '').strip()} {(b.get('SName') or b.get('sname') or '').strip()}".strip() or lid_s
        t1 = _management_avg_pct_for_learner_subject_year(lid_s, str(y_i), term, subject)
        py = _management_avg_pct_for_learner_subject_year(lid_s, str(y_i - 1), term, subject)
        py2 = _management_avg_pct_for_learner_subject_year(lid_s, str(y_i - 2), term, subject)
        py3 = _management_avg_pct_for_learner_subject_year(lid_s, str(y_i - 3), term, subject)
        rows_out.append(
            {
                "learnerName": name,
                "term1": t1,
                "py": py,
                "diffPy": _diff(t1, py),
                "py2": py2,
                "diffPy2": _diff(t1, py2),
                "py3": py3,
                "diffPy3": _diff(t1, py3),
            }
        )
    return {"rows": rows_out, "summary": {"learners": len(rows_out)}, "filters": filters_out}


def _management_average_academics_prev_year_preview_payload() -> dict:
    year = (request.args.get("year") or "").strip()
    grade_filter = (request.args.get("grade") or "").strip()
    term = (request.args.get("term") or "").strip()
    subject = (request.args.get("subject") or "").strip()
    filters_out = {"term": term, "year": year, "grade": grade_filter, "subject": subject}
    if not year:
        return {"rows": [], "summary": {"grades": 0}, "filters": filters_out}
    try:
        y_i = int(float(year))
    except (TypeError, ValueError):
        return {"rows": [], "summary": {"grades": 0}, "filters": filters_out}
    years = [str(y_i - k) for k in range(4)]
    marks_by_year_grade: dict[tuple[str, str], list[float]] = defaultdict(list)
    for ys in years:
        flt: dict = {"year": ys}
        if term:
            flt["term"] = _management_normalize_term_param(term)
        if subject:
            flt["subject"] = subject
        for r in _management_fetch_marks_with_grades(ys, _management_normalize_term_param(term) if term else "", subject):
            g = str(r.get("Grade") or "").strip()
            if grade_filter and g != grade_filter:
                continue
            p = mrh.mr_row_pct(r)
            if p is not None and g:
                marks_by_year_grade[(ys, g)].append(p)
    grades = sorted({k[1] for k in marks_by_year_grade if k[0] == str(y_i)})
    if grade_filter:
        if grade_filter not in grades:
            grades = [grade_filter]
    elif not grades:
        grades = sorted({k[1] for k in marks_by_year_grade})
    rows_out = []
    for g in grades:
        row = mrh.mr_year_over_year_grade_averages(
            marks_by_year_grade,
            current_year=str(y_i),
            grade_label=str(g),
            term_label=term or "All",
        )
        rows_out.append(
            {
                "grade": g,
                "term1": row.get("term1"),
                "py": row.get("py"),
                "diffPy": row.get("diffPy"),
                "py2": row.get("py2"),
                "diffPy2": row.get("diffPy2"),
                "py3": row.get("py3"),
                "diffPy3": row.get("diffPy3"),
            }
        )
    return {"rows": rows_out, "summary": {"grades": len(rows_out)}, "filters": filters_out}


def _management_learner_numeric_grade(g: str) -> int | None:
    m = re.search(r"(\d+)", str(g or ""))
    return int(m.group(1)) if m else None


def _management_learner_movement_learner_ids(mode: str, year: str, grade: str) -> list[str]:
    if not year:
        return []
    try:
        y_i = int(float(year))
    except (TypeError, ValueError):
        return []
    prev_y = str(y_i - 1)
    y = str(year).strip()
    g = str(grade).strip()
    lids: list[str] = []

    if mode == "repeating":
        q = (
            "SELECT DISTINCT c.LearnerId AS LearnerId FROM LearnerPromotion c "
            "INNER JOIN LearnerPromotion p ON p.LearnerId = c.LearnerId "
            "AND CSTR(p.DataYear) = ? AND CSTR(c.DataYear) = ? "
            "WHERE CSTR(p.Grade) = CSTR(c.Grade)"
        )
        params: list = [prev_y, y]
        if g:
            q += " AND CSTR(c.Grade) = ?"
            params.append(g)
        for alt in [q] + (
            [q.replace("CSTR(p.DataYear)", "CSTR(p.Datayear)").replace("CSTR(c.DataYear)", "CSTR(c.Datayear)")]
            if len(_management_learner_promotion_year_columns()) > 1
            else []
        ):
            rows = mdb_conn.execute_query(alt, tuple(params)) or []
            lids = [str(r.get("LearnerId") or r.get("learnerid") or "").strip() for r in rows if r.get("LearnerId") or r.get("learnerid")]
            if lids:
                break

    elif mode == "progressed":
        q = (
            "SELECT c.LearnerId AS LearnerId, CSTR(c.Grade) AS Gc, CSTR(p.Grade) AS Gp FROM LearnerPromotion c "
            "INNER JOIN LearnerPromotion p ON p.LearnerId = c.LearnerId "
            "AND CSTR(p.DataYear) = ? AND CSTR(c.DataYear) = ?"
        )
        params = [prev_y, y]
        if g:
            q += " AND CSTR(c.Grade) = ?"
            params.append(g)
        for alt in [q] + (
            [q.replace("CSTR(p.DataYear)", "CSTR(p.Datayear)").replace("CSTR(c.DataYear)", "CSTR(c.Datayear)")]
            if len(_management_learner_promotion_year_columns()) > 1
            else []
        ):
            rows = mdb_conn.execute_query(alt, tuple(params)) or []
            lids = []
            for r in rows or []:
                gc = _management_learner_numeric_grade(str(r.get("Gc") or ""))
                gp = _management_learner_numeric_grade(str(r.get("Gp") or ""))
                if gc is not None and gp is not None and gc > gp:
                    lids.append(str(r.get("LearnerId") or "").strip())
            if lids:
                break

    elif mode == "dropped_out":
        attempts: list[tuple[str, tuple]] = []
        _valid_ycols = set(_management_learner_promotion_year_columns())
        for ycol in _management_learner_promotion_year_columns():
            if ycol not in _valid_ycols:
                continue
            _safe_identifier(ycol)
            if g:
                attempts.append(
                    (
                        f"SELECT p.LearnerId AS LearnerId FROM LearnerPromotion p "
                        f"WHERE CSTR(p.{ycol}) = ? AND CSTR(p.Grade) = ? AND p.LearnerId NOT IN ("
                        f"SELECT c.LearnerId FROM LearnerPromotion c WHERE CSTR(c.{ycol}) = ?)",
                        (prev_y, g, y),
                    )
                )
            else:
                attempts.append(
                    (
                        f"SELECT p.LearnerId AS LearnerId FROM LearnerPromotion p "
                        f"WHERE CSTR(p.{ycol}) = ? AND p.LearnerId NOT IN ("
                        f"SELECT c.LearnerId FROM LearnerPromotion c WHERE CSTR(c.{ycol}) = ?)",
                        (prev_y, y),
                    )
                )
        lids = []
        for q_sql, par in attempts:
            rows = mdb_conn.execute_query(q_sql, par) or []
            lids = [str(r.get("LearnerId") or "").strip() for r in rows if r.get("LearnerId")]
            if lids:
                break
    else:
        q = (
            "SELECT DISTINCT c.LearnerId AS LearnerId FROM LearnerPromotion c "
            "INNER JOIN LearnerPromotion p ON p.LearnerId = c.LearnerId "
            "AND CSTR(p.DataYear) = ? AND CSTR(c.DataYear) = ? "
            "WHERE CSTR(p.Grade) = CSTR(c.Grade)"
        )
        params = [prev_y, y]
        if g:
            q += " AND CSTR(c.Grade) = ?"
            params.append(g)
        lids = []
        for alt in [q] + (
            [q.replace("CSTR(p.DataYear)", "CSTR(p.Datayear)").replace("CSTR(c.DataYear)", "CSTR(c.Datayear)")]
            if len(_management_learner_promotion_year_columns()) > 1
            else []
        ):
            rows = mdb_conn.execute_query(alt, tuple(params)) or []
            lids = [str(r.get("LearnerId") or "").strip() for r in rows or [] if r.get("LearnerId")]
            if lids:
                break

    seen: set[str] = set()
    out: list[str] = []
    for lid in lids:
        if lid and lid not in seen:
            seen.add(lid)
            out.append(lid)
    return out


def _management_learner_movement_payload() -> dict:
    mode = (request.args.get("mode") or "repeating").strip()
    grade_sel = (request.args.get("grade") or "").strip()
    year_sel = (request.args.get("year") or "").strip()
    fb = _management_report_filters_payload(_management_filters_from_request())
    years_opt = [str(y) for y in (fb.get("years") or [])]
    grades_opt = [str(g) for g in (fb.get("grades") or [])]
    year = year_sel or (years_opt[0] if years_opt else "")
    grade = grade_sel or (grades_opt[0] if grades_opt else "")

    titles = {
        "repeating": "Learners repeating a grade",
        "progressed": "Learners who progressed",
        "dropped_out": "Learners who dropped out",
    }
    lids = _management_learner_movement_learner_ids(mode, year, grade)
    bio = _management_learner_bio_by_keys()
    rows_out: list[dict] = []
    for i, lid in enumerate(lids, start=1):
        b = bio.get(lid) or bio.get(str(int(float(lid))) if lid.isdigit() else "") or {}
        if not b:
            b = next((bio[k] for k in bio if str(k).endswith(lid)), {}) or {}
        rows_out.append(
            {
                "no": i,
                "accessionNo": str(b.get("AccessionNo") or b.get("accessionno") or ""),
                "surname": str(b.get("SName") or b.get("sname") or ""),
                "name": str(b.get("FName") or b.get("fname") or ""),
                "gender": str(b.get("Gender") or b.get("gender") or ""),
                "grade": str(b.get("Grade") or b.get("grade") or ""),
                "className": str(b.get("Class") or b.get("class") or ""),
            }
        )
    return {
        "rows": rows_out,
        "filters": {"grades": grades_opt, "years": years_opt},
        "selected": {"mode": mode, "grade": grade, "year": year},
        "meta": {"title": titles.get(mode, "Learner movement")},
    }


@app.route("/api/management-report")
@login_required
def api_management_report():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    rk = (request.args.get("report_key") or "").strip()
    if not rk:
        return jsonify({"error": "report_key required"}), 400
    try:
        return jsonify(_management_build_generic_report_payload(rk))
    except Exception:
        app.logger.exception("management-report failed key=%s", rk)
        return jsonify({"error": "Could not build report."}), 500


@app.route("/api/management-distribution-results")
@login_required
def api_management_distribution_results():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    try:
        payload = _management_distribution_payload(flt)
        groups = payload.get("groups", [])
        page_info = mrh._apply_pagination(groups, flt.get("page", 1), flt.get("per_page", 100))
        return jsonify(
            {
                "groups": page_info["items"],
                "meta": payload.get("meta", {}),
                "pagination": {"page": page_info["page"], "perPage": page_info["perPage"], "total": page_info["total"], "totalPages": page_info["totalPages"]},
            }
        )
    except Exception:
        app.logger.exception("management-distribution-results failed")
        return jsonify({"error": "Could not build report."}), 500


@app.route("/api/management-averages-per-subject-per-grade")
@login_required
def api_management_averages_per_subject_per_grade():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    try:
        marks = _management_dashboard_fetch_marks(flt)

        def _gf(r: dict) -> str | None:
            g = str(r.get("Grade") or r.get("grade") or "").strip()
            return g or None

        groups = mrh.mr_averages_grid_by_phase(marks, _gf)
        page_info = mrh._apply_pagination(groups, flt.get("page", 1), flt.get("per_page", 100))
        return jsonify(
            {
                "groups": page_info["items"],
                "meta": {"year": flt.get("year") or "", "term": flt.get("term") or ""},
                "pagination": {"page": page_info["page"], "perPage": page_info["perPage"], "total": page_info["total"], "totalPages": page_info["totalPages"]},
            }
        )
    except Exception:
        app.logger.exception("management-averages-per-subject-per-grade failed")
        return jsonify({"error": "Could not build report."}), 500


@app.route("/api/management-results-per-grade-subject")
@login_required
def api_management_results_per_grade_subject():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    try:
        marks = _management_dashboard_fetch_marks(flt)
        rows = mrh.mr_results_rows_for_grade(marks)
        page_info = mrh._apply_pagination(rows, flt.get("page", 1), flt.get("per_page", 100))
        return jsonify(
            {
                "rows": page_info["items"],
                "meta": {"year": flt.get("year") or "", "term": flt.get("term") or "", "grade": flt.get("grade") or ""},
                "pagination": {"page": page_info["page"], "perPage": page_info["perPage"], "total": page_info["total"], "totalPages": page_info["totalPages"]},
            }
        )
    except Exception:
        app.logger.exception("management-results-per-grade-subject failed")
        return jsonify({"error": "Could not build report."}), 500


@app.route("/api/management-analysis")
@login_required
def api_management_analysis():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    try:
        marks = _management_dashboard_fetch_marks(flt)

        def _gf(r: dict) -> str | None:
            g = str(r.get("Grade") or r.get("grade") or "").strip()
            return g or None

        blocks = mrh.mr_analysis_blocks(marks, _gf)
        page_info = mrh._apply_pagination(blocks, flt.get("page", 1), flt.get("per_page", 100))
        return jsonify(
            {
                "blocks": page_info["items"],
                "meta": {"year": flt.get("year") or "", "term": flt.get("term") or ""},
                "pagination": {"page": page_info["page"], "perPage": page_info["perPage"], "total": page_info["total"], "totalPages": page_info["totalPages"]},
            }
        )
    except Exception:
        app.logger.exception("management-analysis failed")
        return jsonify({"error": "Could not build report."}), 500


@app.route("/api/management-learner-movement")
@login_required
def api_management_learner_movement():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    try:
        return jsonify(_management_learner_movement_payload())
    except Exception:
        app.logger.exception("management-learner-movement failed")
        return jsonify({"error": "Could not load learner movement."}), 500


@app.route("/api/management-top3")
@login_required
def api_management_top3():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    try:
        flt = _management_filters_from_request()
        year = str(flt.get("year") or "").strip()
        term = str(flt.get("term") or "").strip()
        top_n = request.args.get("top", "3")
        try:
            top_n = max(1, min(20, int(top_n)))
        except (ValueError, TypeError):
            top_n = 3

        # Fetch marks
        marks = _management_dashboard_fetch_marks(flt)

        if not year and marks:
            year = str(marks[0].get("Year") or marks[0].get("year") or "").strip()

        # Build learner info lookup (name, class)
        learner_info_rows = mdb_conn.execute_query(
            """
            SELECT CSTR([ID]) AS ID, CSTR([LearnerID]) AS LearnerID,
                   [FName], [SName], [Class]
            FROM Learner_Info
            """,
            (),
        ) or []
        learner_lookup: dict[str, dict] = {}
        for r in learner_info_rows:
            lid = str(r.get("LearnerID") or "").strip()
            iid = str(r.get("ID") or "").strip()
            rec = {
                "name": " ".join(x for x in [str(r.get("FName") or "").strip(), str(r.get("SName") or "").strip()] if x),
                "class": str(r.get("Class") or "").strip(),
            }
            if lid:
                learner_lookup[lid] = rec
            if iid:
                learner_lookup[iid] = rec

        # Aggregate per learner per grade
        grade_learners: dict[str, dict[str, dict]] = {}
        for r in marks:
            lid = str(r.get("LearnerID") or "").strip()
            grade = str(r.get("Grade") or r.get("grade") or "").strip()
            if not lid or not grade:
                continue
            pct = mrh.mr_row_pct(r)
            if pct is None:
                continue
            sub = str(r.get("Subject") or "").strip()
            if not sub:
                continue
            if grade not in grade_learners:
                grade_learners[grade] = {}
            if lid not in grade_learners[grade]:
                info = learner_lookup.get(lid, {})
                grade_learners[grade][lid] = {
                    "learnerId": lid,
                    "learnerName": info.get("name", lid),
                    "class": info.get("class", ""),
                    "marks": [],
                    "pcts": [],
                }
            grade_learners[grade][lid]["marks"].append({"subject": sub, "pct": pct})
            grade_learners[grade][lid]["pcts"].append(pct)

        # Build output: for each grade, sort learners by average, take top N
        groups: list[dict] = []
        for grade in sorted(grade_learners.keys(), key=lambda x: (int(re.search(r"(\d+)", x).group(1)) if re.search(r"(\d+)", str(x)) else 999, x)):
            learners = grade_learners[grade].values()
            scored = []
            for l in learners:
                pcts = l["pcts"]
                avg = round(sum(pcts) / len(pcts), 2) if pcts else 0.0
                scored.append({**l, "averagePct": avg})
            scored.sort(key=lambda x: x["averagePct"], reverse=True)
            top = scored[:top_n]
            for t in top:
                t["marks"].sort(key=lambda m: m["subject"].lower())
            groups.append(
                {
                    "grade": f"Grade {grade}",
                    "rank": [{"learnerId": t["learnerId"], "learnerName": t["learnerName"], "class": t["class"], "averagePct": t["averagePct"], "marks": t["marks"]} for t in top],
                }
            )

        return jsonify(
            {
                "groups": groups,
                "topN": top_n,
                "meta": {"year": year, "term": term},
            }
        )
    except Exception:
        app.logger.exception("management-top3 failed")
        return jsonify({"error": "Could not build top learners report."}), 500


@app.route("/api/management-academics-previous-year-comparison/filters")
@login_required
def api_management_academics_previous_year_comparison_filters():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    return jsonify(_management_academics_comparison_filters_response())


@app.route("/api/management-academics-previous-year-comparison/preview")
@login_required
def api_management_academics_previous_year_comparison_preview():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    try:
        return jsonify(_management_academics_prev_year_preview_payload())
    except Exception:
        app.logger.exception("academics-prev-year preview failed")
        return jsonify({"rows": [], "summary": {"learners": 0}, "filters": {}})


@app.route("/api/management-average-academics-previous-year-comaparison/filters")
@login_required
def api_management_average_academics_previous_year_comparision_filters():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    return jsonify(_management_academics_comparison_filters_response())


@app.route("/api/management-average-academics-previous-year-comaparison/preview")
@login_required
def api_management_average_academics_previous_year_comparision_preview():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    try:
        return jsonify(_management_average_academics_prev_year_preview_payload())
    except Exception:
        app.logger.exception("average-academics-prev-year preview failed")
        return jsonify({"rows": [], "summary": {"grades": 0}, "filters": {}})


@app.route("/api/management-report-filters")
@login_required
def api_management_report_filters():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"filters": _management_report_filters_payload(_management_filters_from_request())})


# ── Early Intervention API ────────────────────────────────────────────────


@app.route("/api/early-intervention/list")
@login_required
def api_early_intervention_list():
    """Return interventions with optional filters (status, risk_type, grade)."""
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    st = str(request.args.get("status", "")).strip()
    rt = str(request.args.get("risk_type", "")).strip()
    gr = str(request.args.get("grade", "")).strip()
    query = EarlyIntervention.query
    if st:
        query = query.filter(EarlyIntervention.status == st)
    if rt:
        query = query.filter(EarlyIntervention.risk_type == rt)
    if gr:
        query = query.filter(EarlyIntervention.grade == gr)
    interventions = query.order_by(EarlyIntervention.created_at.desc()).all()
    return jsonify({
        "status": "success",
        "interventions": [
            {
                "id": i.id,
                "learner_id": i.learner_id,
                "learner_name": i.learner_name,
                "grade": i.grade,
                "class_name": i.class_name,
                "risk_type": i.risk_type,
                "intervention_type": i.intervention_type,
                "description": i.description,
                "status": i.status,
                "assigned_to_user_id": i.assigned_to_user_id,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in interventions
        ],
    })


@app.route("/api/early-intervention/create", methods=["POST"])
@login_required
def api_early_intervention_create():
    """Create a new intervention record."""
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json(silent=True) or {}
    learner_id = str(data.get("learner_id") or "").strip()
    risk_type = str(data.get("risk_type") or "").strip()
    intervention_type = str(data.get("intervention_type") or "").strip()
    if not learner_id or not risk_type or not intervention_type:
        return jsonify({"error": "learner_id, risk_type, and intervention_type are required"}), 400
    inv = EarlyIntervention(
        learner_id=learner_id,
        learner_name=str(data.get("learner_name") or "").strip() or None,
        grade=str(data.get("grade") or "").strip() or None,
        class_name=str(data.get("class_name") or "").strip() or None,
        risk_type=risk_type,
        intervention_type=intervention_type,
        description=str(data.get("description") or "").strip() or None,
        assigned_to_user_id=data.get("assigned_to_user_id") or None,
        created_by_user_id=getattr(current_user, "id", 0) or 0,
    )
    db.session.add(inv)
    db.session.commit()
    return jsonify({
        "status": "success",
        "intervention": {
            "id": inv.id,
            "learner_id": inv.learner_id,
            "learner_name": inv.learner_name,
            "grade": inv.grade,
            "class_name": inv.class_name,
            "risk_type": inv.risk_type,
            "intervention_type": inv.intervention_type,
            "description": inv.description,
            "status": inv.status,
            "assigned_to_user_id": inv.assigned_to_user_id,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
        },
    }), 201


@app.route("/api/early-intervention/update", methods=["POST"])
@login_required
def api_early_intervention_update():
    """Update intervention status, outcome_notes, or assigned_to."""
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json(silent=True) or {}
    inv_id = data.get("id")
    if not inv_id:
        return jsonify({"error": "id required"}), 400
    inv = db.session.get(EarlyIntervention, inv_id)
    if not inv:
        return jsonify({"error": "Intervention not found"}), 404
    if "status" in data:
        new_status = str(data["status"]).strip()
        inv.status = new_status
        if new_status in ("resolved", "closed") and not inv.resolved_at:
            inv.resolved_at = datetime.utcnow()
    if "outcome_notes" in data:
        inv.outcome_notes = str(data["outcome_notes"]).strip() or None
    if "assigned_to_user_id" in data:
        inv.assigned_to_user_id = data["assigned_to_user_id"] or None
    if "description" in data:
        inv.description = str(data["description"]).strip() or None
    db.session.commit()
    return jsonify({
        "status": "success",
        "intervention": {
            "id": inv.id,
            "learner_id": inv.learner_id,
            "learner_name": inv.learner_name,
            "grade": inv.grade,
            "class_name": inv.class_name,
            "risk_type": inv.risk_type,
            "intervention_type": inv.intervention_type,
            "description": inv.description,
            "status": inv.status,
            "assigned_to_user_id": inv.assigned_to_user_id,
            "outcome_notes": inv.outcome_notes,
            "resolved_at": inv.resolved_at.isoformat() if inv.resolved_at else None,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        },
    })


@app.route("/api/early-intervention/detail")
@login_required
def api_early_intervention_detail():
    """Return single intervention with its referrals."""
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    inv_id = request.args.get("id")
    if not inv_id:
        return jsonify({"error": "id required"}), 400
    inv = db.session.get(EarlyIntervention, int(inv_id))
    if not inv:
        return jsonify({"error": "Intervention not found"}), 404
    referrals = InterventionReferral.query.filter_by(intervention_id=inv.id).all()
    return jsonify({
        "intervention": {
            "id": inv.id,
            "learner_id": inv.learner_id,
            "learner_name": inv.learner_name,
            "grade": inv.grade,
            "class_name": inv.class_name,
            "risk_type": inv.risk_type,
            "intervention_type": inv.intervention_type,
            "description": inv.description,
            "status": inv.status,
            "assigned_to_user_id": inv.assigned_to_user_id,
            "outcome_notes": inv.outcome_notes,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
            "resolved_at": inv.resolved_at.isoformat() if inv.resolved_at else None,
        },
        "referrals": [
            {
                "id": r.id,
                "referred_to": r.referred_to,
                "referred_to_name": r.referred_to_name,
                "reason": r.reason,
                "notes": r.notes,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
                "outcome": r.outcome,
            }
            for r in referrals
        ],
    })


@app.route("/api/early-intervention/referral/create", methods=["POST"])
@login_required
def api_early_intervention_referral_create():
    """Create a referral linked to an intervention."""
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json(silent=True) or {}
    intervention_id = data.get("intervention_id")
    referred_to = str(data.get("referred_to") or "").strip()
    reason = str(data.get("reason") or "").strip()
    if not intervention_id or not referred_to or not reason:
        return jsonify({"error": "intervention_id, referred_to, and reason are required"}), 400
    inv = db.session.get(EarlyIntervention, intervention_id)
    if not inv:
        return jsonify({"error": "Intervention not found"}), 404
    ref = InterventionReferral(
        intervention_id=intervention_id,
        referred_to=referred_to,
        referred_to_name=str(data.get("referred_to_name") or "").strip() or None,
        reason=reason,
        notes=str(data.get("notes") or "").strip() or None,
        created_by_user_id=getattr(current_user, "id", 0) or 0,
    )
    db.session.add(ref)
    db.session.commit()
    return jsonify({
        "status": "success",
        "referral": {
            "id": ref.id,
            "intervention_id": ref.intervention_id,
            "referred_to": ref.referred_to,
            "referred_to_name": ref.referred_to_name,
            "reason": ref.reason,
            "notes": ref.notes,
            "status": ref.status,
            "created_at": ref.created_at.isoformat() if ref.created_at else None,
        },
    }), 201


@app.route("/api/early-intervention/referral/update", methods=["POST"])
@login_required
def api_early_intervention_referral_update():
    """Update referral status and outcome."""
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json(silent=True) or {}
    ref_id = data.get("id")
    if not ref_id:
        return jsonify({"error": "id required"}), 400
    ref = db.session.get(InterventionReferral, ref_id)
    if not ref:
        return jsonify({"error": "Referral not found"}), 404
    if "status" in data:
        ref.status = str(data["status"]).strip()
        if data["status"] in ("completed", "declined") and not ref.resolved_at:
            ref.resolved_at = datetime.utcnow()
    if "outcome" in data:
        ref.outcome = str(data["outcome"]).strip() or None
    if "notes" in data:
        ref.notes = str(data["notes"]).strip() or None
    db.session.commit()
    return jsonify({
        "status": "success",
        "referral": {
            "id": ref.id,
            "intervention_id": ref.intervention_id,
            "referred_to": ref.referred_to,
            "referred_to_name": ref.referred_to_name,
            "reason": ref.reason,
            "notes": ref.notes,
            "status": ref.status,
            "outcome": ref.outcome,
            "resolved_at": ref.resolved_at.isoformat() if ref.resolved_at else None,
        },
    })


@app.route("/api/early-intervention/from-at-risk")
@login_required
def api_early_intervention_from_at_risk():
    """Check which at-risk learners already have open interventions.

    Returns a set of learner_ids that have open (open|in_progress) interventions.
    """
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    learner_ids_str = str(request.args.get("learner_ids", "")).strip()
    learner_ids = [lid.strip() for lid in learner_ids_str.split(",") if lid.strip()]
    if not learner_ids:
        return jsonify({"open_intervention_learner_ids": []})
    open_ids = set()
    for lid in learner_ids:
        count = EarlyIntervention.query.filter(
            EarlyIntervention.learner_id == lid,
            EarlyIntervention.status.in_(["open", "in_progress"]),
        ).count()
        if count > 0:
            open_ids.add(lid)
    return jsonify({"open_intervention_learner_ids": sorted(open_ids)})


# ── Result Analysis ────────────────────────────────────────────────────────


@app.route("/api/management-result-analysis")
@login_required
def api_management_result_analysis():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    year = str(flt.get("year") or "").strip()
    term = str(flt.get("term") or "").strip()
    if not year or not term:
        fb = _management_report_filters_payload({"year": "", "term": "", "phase": "", "grade": "", "subject": "", "school": ""})
        ys, ts = fb.get("years") or [], fb.get("terms") or []
        year = year or (str(ys[0]) if ys else "")
        term = term or (str(ts[0]) if ts else "")
    if not year or not term:
        return jsonify({"error": "Select year and term."}), 400
    try:
        payload = _management_build_result_analysis_payload(year, term)
        return jsonify(payload)
    except Exception:
        app.logger.exception("management-result-analysis failed for year=%s term=%s", year, term)
        return jsonify({"error": "Could not build report."}), 500


@app.route("/api/management-achievement-promotion-analysis")
@login_required
def api_management_achievement_promotion_analysis():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    year = str(flt.get("year") or "").strip()
    term = str(flt.get("term") or "").strip()
    phase = str(flt.get("phase") or "").strip()
    if not year or not term:
        fb = _management_report_filters_payload({"year": "", "term": "", "phase": "", "grade": "", "subject": "", "school": ""})
        ys, ts = fb.get("years") or [], fb.get("terms") or []
        year = year or (str(ys[0]) if ys else "")
        term = term or (str(ts[0]) if ts else "")
    if not year or not term:
        return jsonify({"error": "Select year and term."}), 400
    try:
        payload = _management_build_achievement_promotion_analysis_payload(year, term, phase)
        return jsonify(payload)
    except Exception:
        app.logger.exception("management-achievement-promotion-analysis failed for year=%s term=%s", year, term)
        return jsonify({"error": "Could not build report."}), 500


def _management_build_result_analysis_pdf_buffer(year: str, term: str) -> BytesIO:
    """PDF with the same figures as the on-screen / XLSX Result Analysis (not a browser-print stub)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    year_s, term_s = str(year).strip(), str(term).strip()
    try:
        payload = _management_build_result_analysis_payload(year_s, term_s)
    except Exception:
        payload = None

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=28,
        rightMargin=28,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story: list = []

    def esc(s: str) -> str:
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if not payload:
        story.append(Paragraph("<b>Result Analysis</b>", styles["Title"]))
        story.append(Paragraph(esc("Could not build this report. Try again or use Export Excel."), styles["Normal"]))
        doc.build(story)
        buf.seek(0)
        return buf

    meta = payload.get("meta") or {}
    school = str(meta.get("schoolName") or "School")
    note = str(meta.get("passThresholdNote") or "")

    story.append(Paragraph(f"<b>{esc(school)}</b>", styles["Title"]))
    story.append(Paragraph(esc(f"Year {year_s} — TERM {term_s}"), styles["Heading2"]))
    story.append(Paragraph("<b>RESULT ANALYSIS</b>", styles["Heading2"]))
    if note:
        story.append(Paragraph(esc(note[:900]), styles["Normal"]))
    story.append(Spacer(1, 0.12 * inch))

    def fmt_trip(m) -> tuple[str, str, str]:
        if not m or not m.get("count"):
            return "—", "—", "—"

        def fv(k: str) -> str:
            v = m.get(k)
            return "—" if v is None else str(v)

        return fv("passPct"), fv("passAt50Pct"), fv("average")

    def promoted_display(s: dict) -> str:
        raw = s.get("numberPromoted")
        if raw is not None and raw != "":
            return str(raw)
        raw = s.get("promoted")
        if raw is not None and raw != "":
            return str(raw)
        a, f = s.get("assessed"), s.get("failed")
        if a is not None and f is not None and a != "" and f != "":
            try:
                return str(int(a) - int(f))
            except (TypeError, ValueError):
                pass
        return "—"

    for ph in payload.get("phases") or []:
        title = str(ph.get("title") or "")
        grades = [int(x) for x in (ph.get("grades") or [])]
        cap = str(ph.get("passPctColumnNote") or "")
        if cap:
            story.append(Paragraph(f"<i>{esc(cap[:1200])}</i>", styles["Normal"]))
            story.append(Spacer(1, 0.06 * inch))
        story.append(Paragraph(f"<b>{esc(title)}</b>", styles["Heading2"]))

        subjects = ph.get("subjects") or []
        summ = ph.get("summary") or {}
        show_prog = bool(ph.get("showProgressedRow"))
        if not grades:
            story.append(Spacer(1, 0.08 * inch))
            continue

        hdr = ["SUBJECT"]
        for g in grades:
            hdr.extend([f"G{g} Pass%", f"G{g} @50%", f"G{g} Avg"])
        data: list[list] = [hdr]

        for sub in subjects:
            subj = str(sub.get("subject") or "")
            row = [subj]
            gmap = sub.get("grades") or {}
            for g in grades:
                trip = gmap.get(str(g))
                if trip is None:
                    trip = gmap.get(g)
                row.extend(list(fmt_trip(trip)))
            data.append(row)

        def sg(gn: int) -> dict:
            return summ.get(str(gn)) or summ.get(gn) or {}

        span_cmds: list = []

        def add_sum_row(label: str, val_for_grade) -> None:
            row = [label]
            ridx = len(data)
            ci = 1
            for gn in grades:
                v = val_for_grade(gn)
                disp = "—" if v is None or v == "" else str(v)
                row.extend([disp, "", ""])
                span_cmds.append(("SPAN", (ci, ridx), (ci + 2, ridx)))
                ci += 3
            data.append(row)

        add_sum_row("Total number assessed", lambda gn: sg(gn).get("assessed"))
        add_sum_row("Number promoted", lambda gn: promoted_display(sg(gn)))
        add_sum_row("Number failed", lambda gn: sg(gn).get("failed"))
        add_sum_row(
            "Total pass %",
            lambda gn: (
                "—"
                if sg(gn).get("totalPassPct") is None or sg(gn).get("totalPassPct") == ""
                else f"{sg(gn).get('totalPassPct')}%"
            ),
        )
        if show_prog:
            add_sum_row("Number progressed", lambda gn: sg(gn).get("progressed"))

        n_sub = len(subjects)
        sum_start = 1 + n_sub
        sum_end = len(data) - 1
        style_cmds = [
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
            ("FONTNAME", (0, sum_start), (-1, sum_end), "Helvetica-Bold"),
        ]
        style_cmds.extend(span_cmds)

        subj_w = min(1.55 * inch, doc.width * 0.18)
        per = (doc.width - subj_w) / (3 * len(grades))
        col_widths = [subj_w] + [per] * (3 * len(grades))

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(style_cmds))
        story.append(tbl)
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buf.seek(0)
    return buf


@app.route("/api/management-result-analysis/pdf")
@login_required
def api_management_result_analysis_pdf():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    flt = _management_filters_from_request()
    year = str(flt.get("year") or "").strip()
    term = str(flt.get("term") or "").strip()
    if not year or not term:
        fb = _management_report_filters_payload(
            {"year": "", "term": "", "phase": "", "grade": "", "subject": "", "school": ""}
        )
        ys, ts = fb.get("years") or [], fb.get("terms") or []
        year = year or (str(ys[0]) if ys else "")
        term = term or (str(ts[0]) if ts else "")
    if not year or not term:
        return jsonify({"error": "Select year and term."}), 400
    try:
        buf = _management_build_result_analysis_pdf_buffer(year, term)
    except Exception:
        app.logger.exception("management-result-analysis pdf failed year=%s term=%s", year, term)
        return jsonify({"error": "Could not build PDF."}), 500
    y_fn = secure_filename(str(year)) or "year"
    t_fn = secure_filename(str(term)) or "term"
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"result_analysis_{y_fn}_t{t_fn}.pdf",
        mimetype="application/pdf",
    )


@app.route("/api/management-result-analysis/xlsx")
@login_required
def api_management_result_analysis_xlsx():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    from openpyxl import Workbook

    flt = _management_filters_from_request()
    year = str(flt.get("year") or "").strip() or "—"
    term = str(flt.get("term") or "").strip() or "—"
    wb = Workbook()
    ws = wb.active
    ws.title = "Result Analysis"
    ws.append(["Result Analysis", f"Year {year}", f"Term {term}"])
    ws.append([])
    try:
        payload = _management_build_result_analysis_payload(year, term)
        for ph in payload.get("phases") or []:
            ws.append([ph.get("title")])
            for sub in ph.get("subjects") or []:
                row = [sub.get("subject")]
                for g in ph.get("grades") or []:
                    trip = (sub.get("grades") or {}).get(str(g)) or (sub.get("grades") or {}).get(g)
                    if not trip or not trip.get("count"):
                        row.extend(["—", "—", "—"])
                    else:
                        row.extend([trip.get("passPct"), trip.get("passAt50Pct"), trip.get("average")])
                ws.append(row)
            ws.append([])
    except Exception:
        app.logger.exception("management-result-analysis xlsx export")
        ws.append(["Export failed — open the on-screen report and try again."])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"result_analysis_{year}_t{term}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/api/management-mark-schedules/filters")
@login_required
def api_management_mark_schedules_filters():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    return jsonify({"filters": _management_mark_schedules_filters_payload(_management_mark_schedules_args_from_request())})


@app.route("/api/management-mark-schedules/preview")
@login_required
def api_management_mark_schedules_preview():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403
    try:
        return jsonify(_management_mark_schedules_preview_payload(_management_mark_schedules_args_from_request()))
    except Exception:
        app.logger.exception("management-mark-schedules preview failed")
        return jsonify({"error": "Could not build preview.", "rows": [], "subjects": [], "summary": {}}), 500


@app.route("/api/management-mark-schedules/pdf")
@login_required
def api_management_mark_schedules_pdf():
    if not _management_user_can_access_reports(current_user):
        return jsonify({"error": "Access denied"}), 403

    args = _management_mark_schedules_args_from_request()
    try:
        payload = _management_mark_schedules_preview_payload(args)
    except Exception:
        app.logger.exception("management-mark-schedules pdf payload failed")
        payload = {"rows": [], "subjects": [], "summary": {}}

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=24,
        rightMargin=24,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    def esc(s: str) -> str:
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story: list = []
    year_label = str(args.get("year") or "—")
    cycle_label = str(args.get("cycle") or "all")
    grade_label = str(args.get("grade") or "all")
    story.append(Paragraph("<b>Mark Schedules</b>", styles["Title"]))
    story.append(
        Paragraph(
            esc(f"Year: {year_label} | Cycle: {cycle_label} | Grade: {grade_label}"),
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.1 * inch))

    rows_data = payload.get("rows") or []
    subjects = payload.get("subjects") or []
    summary = payload.get("summary") or {}

    if not rows_data:
        story.append(Paragraph("No records found for the selected filters.", styles["Normal"]))
        doc.build(story)
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name="mark_schedules.pdf", mimetype="application/pdf")

    # Static columns + one subject column per subject + average + code
    static_cols = ["No", "Adm #", "Learner", "DOB", "Gender", "Yrs Grd", "Yrs Ph", "Abs"]
    hdr = static_cols + subjects + ["Avg %", "Code"]

    table_data: list[list] = [[Paragraph(f"<b>{esc(h)}</b>", styles["Normal"]) for h in hdr]]

    for r in rows_data:
        subject_map = {}
        for sc in r.get("subjectScores") or []:
            subject_map[sc["subject"]] = str(sc.get("percent") or "")
        row: list = [
            str(r.get("no") or ""),
            str(r.get("admissionNumber") or ""),
            str(r.get("learnerName") or ""),
            str(r.get("dateOfBirth") or ""),
            str(r.get("gender") or ""),
            str(r.get("yearsInGrade") or ""),
            str(r.get("yearsInPhase") or ""),
            str(r.get("daysAbsent") or ""),
        ]
        for sub in subjects:
            row.append(subject_map.get(sub, ""))
        row.append(str(r.get("averagePercent") or ""))
        row.append(str(r.get("code") or ""))
        table_data.append(row)

    # Build the table with as many repeats as needed for subject columns
    col_widths = [30, 50, 110, 60, 36, 32, 32, 32]
    sub_width = min(55, max(35, int((landscape(A4)[0] - 24 - 24 - sum(col_widths) - 50) / max(len(subjects), 1))))
    for _ in subjects:
        col_widths.append(sub_width)
    col_widths.append(38)
    col_widths.append(34)

    # If cols are too wide, shrink uniformly
    total_w = sum(col_widths)
    page_w = landscape(A4)[0] - 24 - 24
    if total_w > page_w:
        factor = page_w / total_w
        col_widths = [int(w * factor) for w in col_widths]

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 6.5),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (3, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ]
        )
    )
    story.append(tbl)

    story.append(Spacer(1, 0.15 * inch))
    learners = summary.get("learners", 0)
    pass_c = summary.get("passCount", 0)
    np_c = summary.get("notPassCount", 0)
    avg_p = summary.get("averagePercent")
    summary_line = f"Total: {learners}  |  Pass: {pass_c}  |  Not Pass: {np_c}"
    if avg_p is not None:
        summary_line += f"  |  Avg %: {avg_p}"
    story.append(Paragraph(esc(summary_line), styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    fn_year = secure_filename(str(year_label)) or "year"
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"mark_schedules_{fn_year}.pdf",
        mimetype="application/pdf",
    )


MANAGEMENT_REPORT_REGISTRY = [
    {"key": "finance-overview", "title": "Finance Overview", "template": "management/finance_overview.html"},
    {"key": "educator-staff", "title": "Educator Staff Profile", "template": "management/educator_staff.html"},
    {"key": "non-educator-staff", "title": "Non-Educator Staff Profile", "template": "management/non_educator_staff.html"},
    {"key": "general-overview", "title": "General Overview", "template": "management/general_overview.html"},
    {"key": "principal-overview", "title": "Principal Overview", "template": "management/principal_overview.html"},
    {"key": "attendance", "title": "Attendance", "template": "management/attendance.html"},
    {"key": "at-risk-dashboard", "title": "At-Risk Learner Dashboard", "template": "management/at_risk_dashboard.html"},
    {"key": "early-intervention", "title": "Early Intervention", "template": "management/early_intervention.html"},
    {"key": "learner-chart-report", "title": "Learner Chart Report", "template": "management/learner_chart_report.html"},
    {"key": "school-achievement-report", "title": "School Achievement Report", "template": "management/school_achievement_report.html"},
    {"key": "learner-promotion-rate", "title": "Learner Promotion Rate", "template": "management/learner_promotion_rate.html"},
    {"key": "enrolment-by-year-trend", "title": "Enrolment by Year Trend", "template": "management/enrolment_by_year_trend.html"},
    {"key": "subject-achievement-insights", "title": "Subject Achievement Insights", "template": "management/subject_achievement_insights.html"},
    {"key": "term-to-date-insights", "title": "Term-to-Date Insights", "template": "management/term_to_date_insights.html"},
    {"key": "mark-schedules", "title": "Mark Schedules", "template": "management/mark_schedules.html"},
    {"key": "academics-previous-year-comparison", "title": "Academics Previous Year Comparison", "template": "management/academics_previous_year_comparison.html"},
    {"key": "average-academics-previous-year-comaparison", "title": "Average Academics Previous Year Comaparison", "template": "management/average_academics_previous_year_comaparison.html"},
    {"key": "analysis", "title": "Analysis", "template": "management/analysis.html"},
    {"key": "distribution-results-per-grade-per-subject", "title": "Distribution Results per Grade per Subject", "template": "management/distribution_results_per_grade_subject.html"},
    {"key": "averages-per-subject-per-grade", "title": "Averages per Subject per Grade", "template": "management/averages_per_subject_grade.html"},
    {"key": "results-per-grade-subject", "title": "Results per Grade/Subject", "template": "management/results_per_grade_subject.html"},
    {"key": "achievement-promotion-analysis", "title": "Achievement/Promotion Analysis", "template": "management/achievement_promotion_analysis.html"},
    {"key": "learner-movement", "title": "Learners who dropped Out or are Repeating a Grade", "template": "management/learner_movement.html"},
    {"key": "result-analysis", "title": "Result Analysis", "template": "management/result_analysis.html"},
    {"key": "top3", "title": "Top 3", "template": "management/top3.html"},
]
MANAGEMENT_REPORTS_BY_KEY = {r["key"]: r for r in MANAGEMENT_REPORT_REGISTRY}

# CAP-style phases for the printed-style Result Analysis report (Grades 1–12).
# Pass boundaries are inclusive (≥): exactly meeting the printed minimum counts as a pass
# (e.g. 50% meets a 50% HL rule; 40% meets a 40% rule). Comparisons use >= / fail only when pct < thr.
# Percentages are rounded half-up (fractional part ≥ 0.5 rounds up), matching typical EMS behaviour.
RESULT_ANALYSIS_PHASES = (
    {"key": "foundation", "title": "FOUNDATION PHASE", "grades": (1, 2, 3), "show_progressed_row": False},
    {"key": "intermediate", "title": "INTERMEDIATE PHASE", "grades": (4, 5, 6), "show_progressed_row": True},
    {"key": "senior", "title": "SENIOR PHASE", "grades": (7, 8, 9), "show_progressed_row": False},
    {"key": "fet", "title": "FET PHASE", "grades": (10, 11, 12), "show_progressed_row": False},
)
RESULT_ANALYSIS_PASS_PCT_THRESHOLD = 40.0
RESULT_ANALYSIS_PASS_PCT_THRESHOLD_HOME_LANGUAGE = 50.0  # Grades 1–9 Home Language column Pass%
RESULT_ANALYSIS_PASS_PCT_THRESHOLD_FET_HOME_LANGUAGE = 40.0  # Grades 10–12 HL (NSC basic column guide)
RESULT_ANALYSIS_PASS_PCT_THRESHOLD_FET_OTHER = 30.0  # Non-HL FET subjects column Pass% guide
RESULT_ANALYSIS_PASS_PCT_TABLE_NOTE_SENIOR = (
    "Pass% column (Grades 7–9): English (HL slot) ≥50%; Afrikaans (FAL), Mathematics, Natural Sciences, Social Sciences, "
    "Technology, EMS, Life Orientation, Creative Arts (and other assessed subjects) ≥40%. "
    "Marks-based promotion uses the same per-subject minima."
)
RESULT_ANALYSIS_PASS_PCT_TABLE_NOTE_FET = (
    "Pass% column (Grades 10–12): English (HL slot) ≥40%; First Additional Language, Mathematics / Mathematical Literacy, "
    "Life Orientation, and elective subjects ≥30%. Marks-based promotion uses the same per-subject minima."
)
RESULT_ANALYSIS_OVERALL_PROMOTION_NON_ENGLISH_MIN_PCT = 40.0
RESULT_ANALYSIS_OVERALL_PROMOTION_ENGLISH_MIN_PCT = 50.0


def _management_normalize_subject_label(raw: str) -> str:
    """Strip EMS suffixes such as '(Gr 5)' so matchers align across grades."""
    return re.sub(r"\s*\(Gr\s+\d+\)\s*$", "", str(raw or "").strip(), flags=re.IGNORECASE)


def _management_is_english_subject(subject: str) -> bool:
    """True when the subject name refers to English (HL, FAL, SAL, etc.)."""
    k = re.sub(r"[^a-z0-9]+", " ", str(subject or "").lower()).strip()
    return bool(re.search(r"\benglish\b", k))


def _management_is_home_language_subject(subject: str) -> bool:
    """English Home Language slot for CAP / NSC rules (school policy: HL is English).

    Includes typical EMS lines (“English Home Language”) and bare “English” rows without Additional/FAL.
    English First Additional is excluded — use “other subject” thresholds instead.
    """
    s = _management_normalize_subject_label(subject).lower()
    if not re.search(r"\benglish\b", s):
        return False
    if "first additional" in s or "second additional" in s:
        return False
    if re.search(r"\bfal\b", s):
        return False
    if "additional" in s and "home language" not in s:
        return False
    return True


def _management_is_fal_subject(subject: str) -> bool:
    """Afrikaans First Additional Language slot (school policy FAL = Afrikaans; excludes Afrikaans HL).

    Afrikaans Home Language is tracked separately and does not satisfy the FAL requirement for promotion.
    """
    s = _management_normalize_subject_label(subject).lower()
    if not re.search(r"\bafrikaans\b", s):
        return False
    return "home language" not in s


def _management_is_afrikaans_home_language_subject(subject: str) -> bool:
    s = _management_subject_label_lower(subject)
    return bool(re.search(r"\bafrikaans\b", s) and "home language" in s)


def _management_is_maths_subject(subject: str) -> bool:
    s = _management_normalize_subject_label(subject).lower()
    if re.search(r"\bmath", s) or re.search(r"\bmaths\b", s):
        return True
    return bool(re.search(r"\bnumeracy\b", s))


def _management_subject_label_lower(subject: str) -> str:
    return _management_normalize_subject_label(subject).lower()


def _management_is_natural_sciences_technology_subject(subject: str) -> bool:
    """Natural Sciences, Natural Sciences & Technology, NST, etc. (GET phases)."""
    s = _management_subject_label_lower(subject)
    return bool(
        "natural science" in s
        or ("ns" in s and "tec" in s.replace("&", " "))
        or "nstec" in s.replace("&", "").replace(" ", "")
    )


def _management_is_social_sciences_subject(subject: str) -> bool:
    s = _management_subject_label_lower(subject)
    return bool("social science" in s or re.search(r"(^|\s)ss(\s|$)", s) or "soc sci" in s)


def _management_is_life_skills_subject(subject: str) -> bool:
    s = _management_subject_label_lower(subject)
    if "orientation" in s:
        return False
    return bool(re.search(r"life\s*skill", s) or "lifeskills" in s.replace(" ", ""))


def _management_is_life_orientation_subject(subject: str) -> bool:
    s = _management_subject_label_lower(subject)
    return bool("life orientation" in s or re.search(r"(^|\s)lo(\s|$)", s))


def _management_is_technology_subject(subject: str) -> bool:
    """Senior Phase Technology — excludes combined Natural Sciences & Technology (counted under NST)."""
    s = _management_subject_label_lower(subject)
    if "natural science" in s:
        return False
    return bool(re.search(r"\btechnology\b", s) or "design and technology" in s)


def _management_is_ems_subject(subject: str) -> bool:
    s = _management_subject_label_lower(subject)
    return "economic management" in s or bool(re.search(r"(^|\s)ems(\s|$)", s))


def _management_is_creative_arts_subject(subject: str) -> bool:
    s = _management_subject_label_lower(subject)
    return any(
        k in s
        for k in (
            "creative art",
            "visual art",
            "dramatic art",
            "dance studies",
            "music",
        )
    )


def _management_marks_pass_threshold_pct_for_subject(grade: int, subject: str) -> float | None:
    """School EMS minimum % for this subject in marks-based promotion; None if row must not count as meeting policy."""
    if _management_is_afrikaans_home_language_subject(subject):
        return None
    if grade <= 3:
        if _management_is_home_language_subject(subject):
            return 50.0
        if _management_is_fal_subject(subject):
            return 40.0
        if _management_is_maths_subject(subject):
            return 40.0
        if _management_is_life_skills_subject(subject) or _management_is_life_orientation_subject(subject):
            return 40.0
        return None
    if 4 <= grade <= 6:
        if _management_is_home_language_subject(subject):
            return 50.0
        if _management_is_fal_subject(subject):
            return 40.0
        if _management_is_maths_subject(subject):
            return 40.0
        if _management_is_natural_sciences_technology_subject(subject):
            return 40.0
        if _management_is_social_sciences_subject(subject):
            return 40.0
        if _management_is_life_skills_subject(subject) or _management_is_life_orientation_subject(subject):
            return 40.0
        return None
    if 7 <= grade <= 9:
        if _management_is_home_language_subject(subject):
            return 50.0
        if _management_is_fal_subject(subject):
            return 40.0
        if _management_is_maths_subject(subject):
            return 40.0
        if _management_is_natural_sciences_technology_subject(subject):
            return 40.0
        if _management_is_social_sciences_subject(subject):
            return 40.0
        if _management_is_technology_subject(subject):
            return 40.0
        if _management_is_ems_subject(subject):
            return 40.0
        if _management_is_life_orientation_subject(subject) or _management_is_life_skills_subject(subject):
            return 40.0
        if _management_is_creative_arts_subject(subject):
            return 40.0
        return 40.0
    if 10 <= grade <= 12:
        if _management_is_home_language_subject(subject):
            return 40.0
        if _management_is_fal_subject(subject):
            return 30.0
        if _management_is_maths_subject(subject):
            return 30.0
        if _management_is_life_orientation_subject(subject):
            return 30.0
        return 30.0
    return None


def _management_pass_pct_threshold_for_subject_grade(grade: int, subject: str) -> float:
    """Pass% column: English (HL) vs Afrikaans (FAL) vs Maths vs other; FET uses NSC-style HL/other split."""
    subj = subject
    if grade <= 9:
        if _management_is_home_language_subject(subj):
            return float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD_HOME_LANGUAGE)
        if _management_is_fal_subject(subj) or _management_is_maths_subject(subj):
            return float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)
        return float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)
    if _management_is_home_language_subject(subj):
        return float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD_FET_HOME_LANGUAGE)
    return float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD_FET_OTHER)


def _management_subject_excluded_from_overall_pass(subject: str) -> bool:
    """Marks-only subjects that must not affect promoted/failed / Total pass% (not on printed analysis)."""
    s = _management_normalize_subject_label(subject).lower()
    return any(
        k in s
        for k in (
            "sport",
            "cultural programme",
            "cultural program",
            "club",
            "computer literacy",
            "coding",
            "robotics",
        )
    )


def _management_subject_in_overall_pass_computation(grade: int, subject: str) -> bool:
    """Subjects whose marks determine Total pass% / promoted / failed (matches EMS curriculum tables)."""
    if _management_subject_excluded_from_overall_pass(subject):
        return False
    if grade <= 3:
        return (
            _management_is_english_subject(subject)
            or _management_is_fal_subject(subject)
            or _management_is_maths_subject(subject)
            or _management_is_life_skills_subject(subject)
            or _management_is_life_orientation_subject(subject)
            or _management_is_afrikaans_home_language_subject(subject)
        )

    if 4 <= grade <= 6:
        return (
            _management_is_english_subject(subject)
            or _management_is_fal_subject(subject)
            or _management_is_maths_subject(subject)
            or _management_is_natural_sciences_technology_subject(subject)
            or _management_is_social_sciences_subject(subject)
            or _management_is_life_skills_subject(subject)
            or _management_is_life_orientation_subject(subject)
            or _management_is_afrikaans_home_language_subject(subject)
        )

    # Grades 7–12: include all assessed subjects except explicit exclusions (programme varies by school).
    return True


def _grade_to_phase(grade_value: str) -> str:
    m = re.search(r"(\d+)", str(grade_value or "").strip())
    if not m:
        return "Other"
    num = int(m.group(1))
    if num <= 3:
        return "Foundation"
    if num <= 6:
        return "Intermediate"
    if num <= 9:
        return "Senior"
    return "FET"


def _management_filters_from_request() -> dict:
    return {
        "year": str(request.args.get("year", "")).strip(),
        "term": str(request.args.get("term", "")).strip(),
        "grade": str(request.args.get("grade", "")).strip(),
        "subject": str(request.args.get("subject", "")).strip(),
        "phase": str(request.args.get("phase", "")).strip(),
        "school": str(request.args.get("school", "")).strip(),
        "page": int(request.args.get("page", "1")),
        "per_page": int(request.args.get("per_page", "100")),
    }


def _management_promotion_grade_map(year: str) -> dict[str, str]:
    """
    Map learner keys (Learner_Info.ID, Learner_Info.LearnerID, LearnerPromotion.LearnerId value)
    to promotion Grade for the given DataYear. ReportMarks.LearnerID may not match
    LearnerPromotion.[LearnerId] as the same string; aligning keys fixes empty Result Analysis
    and Mark Schedules.
    """
    year_s = str(year or "").strip()
    if not year_s:
        return {}
    learners = (
        mdb_conn.execute_query(
            """
            SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class], [Gender], [Status]
            FROM Learner_Info
            WHERE [Status] = ?
            """,
            ("C",),
        )
        or []
    )
    lookup = build_learner_lookup_by_any_id(learners)
    grade_map: dict[str, str] = {}

    def _add(promo_key: str, g: str) -> None:
        k = str(promo_key or "").strip()
        gg = str(g or "").strip()
        if not k or not gg:
            return
        grade_map[k] = gg
        info = lookup.get(k)
        if info:
            if info.get("id"):
                grade_map[str(info["id"])] = gg
            if info.get("learner_id"):
                grade_map[str(info["learner_id"])] = gg

    lp_rows: list[dict] = []
    for lid_col in ("LearnerId", "LearnerID"):
        for ycol in _management_learner_promotion_year_columns():
            lp_rows = (
                mdb_conn.execute_query(
                    f"""
                    SELECT CSTR([{lid_col}]) AS Lid, CSTR([Grade]) AS G
                    FROM LearnerPromotion
                    WHERE CSTR([{ycol}]) = ?
                    """,
                    (year_s,),
                )
                or []
            )
            if lp_rows:
                break
        if lp_rows:
            break
    for r in lp_rows:
        _add(str(r.get("Lid") or r.get("lid") or ""), str(r.get("G") or r.get("g") or ""))
    return grade_map


def _management_normalize_term_param(term: str) -> str:
    """Align UI / Cycle terms (e.g. 1 vs 1.0) with ReportCycles.Term in PostgreSQL."""
    t = str(term or "").strip()
    if not t:
        return t
    try:
        if float(t) == int(float(t)):
            return str(int(float(t)))
    except ValueError:
        pass
    return t


def _management_term_sort_key(term_val) -> tuple:
    """Sort terms 1, 2, 10 instead of lexicographic 1, 10, 2 from plain ORDER BY Term."""
    t = str(term_val or "").strip()
    try:
        return (0, int(float(t)))
    except ValueError:
        return (1, t.lower())


def _management_grade_matches_filter(want: str, *candidates: str) -> bool:
    """True if filter grade matches promotion or bio strings (e.g. 10 vs '10' vs 'Gr 10')."""
    w = str(want).strip()
    if not w:
        return True

    def tokens(s: str) -> set[str]:
        s = str(s or "").strip()
        if not s:
            return set()
        out = {s.lower()}
        for m in re.finditer(r"\d+", s):
            out.add(m.group(0))
        return out

    w_tok = tokens(w)
    for c in candidates:
        if w_tok & tokens(c):
            return True
    return False


def _management_promotion_learner_keys_for_year_grade(year: str, grade: str) -> list[str]:
    """Learner keys on ReportMarks rows (ID and learner code) for a promotion year+grade."""
    year_s, g_s = str(year).strip(), str(grade).strip()
    if not year_s or not g_s:
        return []
    learners = (
        mdb_conn.execute_query(
            "SELECT [ID], [LearnerID] FROM Learner_Info WHERE [Status] = ?",
            ("C",),
        )
        or []
    )
    lookup = build_learner_lookup_by_any_id(learners)
    raw: set[str] = set()
    for lid_col in ("LearnerId", "LearnerID"):
        for ycol in _management_learner_promotion_year_columns():
            rows = (
                mdb_conn.execute_query(
                    f"""
                    SELECT CSTR([{lid_col}]) AS Lid
                    FROM LearnerPromotion
                    WHERE CSTR([{ycol}]) = ? AND CSTR([Grade]) = ?
                    """,
                    (year_s, g_s),
                )
                or []
            )
            for r in rows:
                lid = str(r.get("Lid") or r.get("lid") or "").strip()
                if lid:
                    raw.add(lid)
            if raw:
                break
        if raw:
            break
    expanded: set[str] = set()
    for lid in raw:
        expanded.add(lid)
        info = lookup.get(lid)
        if info:
            if info.get("id"):
                expanded.add(str(info["id"]))
            if info.get("learner_id"):
                expanded.add(str(info["learner_id"]))
    return list(expanded)


def _management_fetch_marks_rows(filters: dict) -> list[dict]:
    query = """
        SELECT rm.Datayear AS Year, rc.Term AS Term, s.Name AS Subject,
               rm.Mark AS Mark, rm.TotalMark AS TotalMark, CSTR(rm.LearnerID) AS LearnerID
        FROM ReportMarks rm, ReportCycles rc, Subjects s
        WHERE rm.ReportId = rc.CycleId
          AND rm.SubjectId = s.Id
    """
    params = []
    if filters.get("year"):
        query += " AND CSTR(rm.Datayear) = ?"
        params.append(filters["year"])
    else:
        # Default to latest available year to avoid full historical scans.
        query += " AND rm.Datayear = (SELECT MAX(rm2.Datayear) FROM ReportMarks rm2)"
    # When a specific report cycle is selected, filtering by Term as well often drops all rows
    # (type/format mismatch across CycleId vs Term in PostgreSQL).
    if filters.get("term") and not filters.get("report_id"):
        query += " AND CSTR(rc.Term) = ?"
        params.append(_management_normalize_term_param(str(filters["term"])))
    if filters.get("report_id"):
        query += " AND CSTR(rm.ReportId) = ?"
        params.append(str(filters["report_id"]).strip())
    if filters.get("grade"):
        keys = _management_promotion_learner_keys_for_year_grade(str(filters.get("year") or ""), str(filters["grade"]).strip())
        if not keys:
            return []
        chunk_sz = 200
        chunks = [keys[i : i + chunk_sz] for i in range(0, len(keys), chunk_sz)]
        in_parts = []
        for ch in chunks:
            if not ch:
                continue
            in_parts.append("CSTR(rm.LearnerID) IN (" + ",".join(["?"] * len(ch)) + ")")
            params.extend(ch)
        if not in_parts:
            return []
        query += " AND (" + " OR ".join(in_parts) + ")"
    if filters.get("subject"):
        query += " AND (s.Name = ? OR s.Name LIKE ?)"
        params.append(filters["subject"])
        # Match the normalized base subject followed by grade suffix e.g. "Mathematics (Gr 8)"
        # This is more precise than a bare prefix which could match "Mathematics Literacy"
        params.append(f"{filters['subject']} (Gr %")
    query += " ORDER BY rm.Datayear DESC, rc.Term ASC"
    rows = mdb_conn.execute_query(query, tuple(params)) or []
    if filters.get("phase"):
        phase = filters["phase"].lower()

        def _row_phase(item: dict) -> str:
            learner_grade = item.get("LearnerGrade")
            if learner_grade:
                return _grade_to_phase(str(learner_grade))
            subject_name = str(item.get("Subject") or "")
            m = re.search(r"\(Gr\s+(\d+)\)\s*$", subject_name, flags=re.IGNORECASE)
            if m:
                return _grade_to_phase(m.group(1))
            return "Other"

        rows = [item for item in rows if _row_phase(item).lower() == phase]
    for item in rows:
        raw = str(item.get("Subject") or "")
        item["Subject"] = _management_normalize_subject_label(raw)
    return rows


def _management_round_percentage_half_up(value: float | Decimal | int | None, decimals: int = 0) -> float:
    if value is None:
        return 0.0
    step = Decimal("1") if decimals <= 0 else Decimal("0." + ("0" * (decimals - 1)) + "1")
    return float(Decimal(str(float(value))).quantize(step, rounding=ROUND_HALF_UP))


def _management_fetch_marks_with_grades(year: str, term: str, subject: str = "") -> list[dict]:
    flt = {"year": str(year).strip(), "term": str(term).strip()}
    if subject:
        flt["subject"] = subject
    rows = _management_fetch_marks_rows(flt)
    if not rows:
        return []
    grade_map = _management_promotion_grade_map(str(year).strip())
    out: list[dict] = []
    for r in rows:
        lid = str(r.get("LearnerID") or "").strip()
        if not lid:
            continue
        g = grade_map.get(lid)
        if not g:
            continue
        out.append(
            {
                "Grade": g,
                "LearnerID": lid,
                "Subject": str(r.get("Subject") or ""),
                "Mark": r.get("Mark"),
                "TotalMark": r.get("TotalMark"),
            }
        )
    return out


def _management_mark_schedules_args_from_request() -> dict:
    return {
        "grade": str(request.args.get("grade", "")).strip(),
        "class": str(request.args.get("class", "")).strip(),
        "year": str(request.args.get("year", "")).strip(),
        "cycle": str(request.args.get("cycle", "")).strip(),
        "learner_filter": str(request.args.get("learner_filter", "")).strip(),
        "code": str(request.args.get("code", "")).strip(),
    }


def _management_term_for_cycle_or_year(cycle_id: str, year: str) -> str:
    cid = str(cycle_id or "").strip()
    if cid:
        rows = (
            mdb_conn.execute_query(
                "SELECT TOP 1 CSTR(rc.Term) AS T FROM ReportCycles rc WHERE CSTR(rc.CycleId) = ?",
                (cid,),
            )
            or []
        )
        if rows:
            t_raw = str(rows[0].get("T") or rows[0].get("t") or "").strip()
            return _management_normalize_term_param(t_raw) if t_raw else "1"
    ys = str(year or "").strip()
    if ys:
        tr = (
            mdb_conn.execute_query(
                """
                SELECT DISTINCT CSTR(rc.Term) AS T
                FROM ReportMarks rm, ReportCycles rc
                WHERE rm.ReportId = rc.CycleId AND CSTR(rm.Datayear) = ?
                """,
                (ys,),
            )
            or []
        )
        if tr:
            tr_sorted = sorted(tr, key=lambda row: _management_term_sort_key(row.get("T") or row.get("t")))
            t0 = str(tr_sorted[0].get("T") or tr_sorted[0].get("t") or "1").strip()
            return _management_normalize_term_param(t0)
    return "1"


def _management_learner_bio_by_keys(year: str = "") -> dict[str, dict]:
    rows = (
        mdb_conn.execute_query(
            """
            SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class], [Gender], [BirthDate] AS DOB, [AccessionNo]
            FROM Learner_Info
            WHERE [Status] = ?
            """,
            ("C",),
        )
        or []
    )
    by_key: dict[str, dict] = {}
    for r in rows:
        for key in (str(r.get("ID") or ""), str(r.get("LearnerID") or "")):
            k = key.strip()
            if k and k != "None" and k not in by_key:
                by_key[k] = r
    # When a year is specified, also fetch bio for non-current learners who
    # have marks in that year (they left, graduated, etc.).  Without this,
    # switching to an older year shows only names of learners still current.
    yr = str(year or "").strip()
    if yr:
        lids_rows = (
            mdb_conn.execute_query(
                """
                SELECT DISTINCT CSTR(rm.LearnerID) AS Lid
                FROM ReportMarks rm
                WHERE CSTR(rm.Datayear) = ?
                """,
                (yr,),
            )
            or []
        )
        lids = [str(r.get("Lid") or "").strip() for r in lids_rows if str(r.get("Lid") or "").strip()]
        if lids:
            chunk_sz = 200
            for i in range(0, len(lids), chunk_sz):
                chunk = lids[i : i + chunk_sz]
                placeholders = ",".join(["?"] * len(chunk))
                extra = (
                    mdb_conn.execute_query(
                        f"""
                        SELECT [ID], [LearnerID], [FName], [SName], [Grade], [Class], [Gender], [BirthDate] AS DOB, [AccessionNo]
                        FROM Learner_Info
                        WHERE 1=1
                          AND (CSTR([ID]) IN ({placeholders}) OR CSTR([LearnerID]) IN ({placeholders}))
                        """,
                        tuple(chunk + chunk),
                    )
                    or []
                )
                for r in extra:
                    for key in (str(r.get("ID") or ""), str(r.get("LearnerID") or "")):
                        k = key.strip()
                        if k and k != "None" and k not in by_key:
                            by_key[k] = r
    return by_key


def _management_mark_schedules_filters_payload(args: dict) -> dict:
    fb = _management_report_filters_payload(
        {
            "year": str(args.get("year") or ""),
            "term": "",
            "phase": "",
            "grade": str(args.get("grade") or ""),
            "subject": "",
            "school": "",
        }
    )
    grades = fb.get("grades") or []
    years = fb.get("years") or []
    year_ctx = str(args.get("year") or "").strip() or (str(years[0]) if years else "")
    cycles: list[str] = []
    if year_ctx:
        cr = (
            mdb_conn.execute_query(
                """
                SELECT DISTINCT rc.CycleId, rc.Term
                FROM ReportCycles rc
                INNER JOIN ReportMarks rm ON rm.ReportId = rc.CycleId
                WHERE CSTR(rm.Datayear) = ?
                """,
                (year_ctx,),
            )
            or []
        )
        cr_sorted = sorted(cr, key=lambda row: _management_term_sort_key(row.get("Term")))
        for r in cr_sorted:
            cid = str(r.get("CycleId") or "").strip()
            if cid:
                cycles.append(cid)
    cl_rows = (
        mdb_conn.execute_query(
            """
            SELECT DISTINCT CSTR([Class]) AS C
            FROM Learner_Info
            WHERE [Class] IS NOT NULL AND [Status] = ?
            ORDER BY C
            """,
            ("C",),
        )
        or []
    )
    classes = [str(x.get("C") or x.get("c") or "").strip() for x in cl_rows if str(x.get("C") or x.get("c") or "").strip()]
    return {
        "grades": grades,
        "classes": classes,
        "years": years,
        "cycles": cycles,
        "learnerFilters": [
            {"value": "", "label": "All learners"},
            {"value": "pass", "label": "Passed (avg ≥ 40%)"},
            {"value": "notpass", "label": "Not passed (avg < 40%)"},
        ],
        "codes": ["P", "NP"],
    }


def _management_mark_row_pct(row: dict) -> float | None:
    try:
        m = float(row.get("Mark") or 0)
        t = float(row.get("TotalMark") or 0)
        if t <= 0:
            return None
        return float(_management_round_percentage_half_up(m / t * 100.0, 1))
    except (TypeError, ValueError):
        return None


def _management_mark_schedules_preview_payload(args: dict) -> dict:
    year = str(args.get("year") or "").strip()
    grade_f = str(args.get("grade") or "").strip()
    class_f = str(args.get("class") or "").strip()
    cycle = str(args.get("cycle") or "").strip()
    lf = str(args.get("learner_filter") or "").strip()
    code_f = str(args.get("code") or "").strip()
    empty_sum = {"learners": 0, "passCount": 0, "notPassCount": 0, "averagePercent": None}

    if not year:
        mx = mdb_conn.execute_query("SELECT MAX(rm.Datayear) AS y FROM ReportMarks rm", ()) or []
        if mx and mx[0] is not None:
            year = str(mx[0].get("y") or mx[0].get("Y") or "").strip()
    if not year:
        return {"rows": [], "subjects": [], "summary": empty_sum}

    term = _management_term_for_cycle_or_year(cycle, year) or "1"
    flt: dict = {"year": year}
    if not cycle:
        flt["term"] = _management_normalize_term_param(term)
    if cycle:
        flt["report_id"] = cycle
    marks = _management_fetch_marks_rows(flt)
    by_key = _management_learner_bio_by_keys(year)
    grade_map = _management_promotion_grade_map(year)
    if grade_f:
        marks = [
            r
            for r in marks
            if _management_grade_matches_filter(
                grade_f,
                str(grade_map.get(str(r.get("LearnerID") or "").strip(), "") or ""),
                str(
                    by_key.get(str(r.get("LearnerID") or "").strip(), {}).get("Grade")
                    or ""
                ),
            )
        ]
    if not marks:
        return {"rows": [], "subjects": [], "summary": empty_sum}

    subjects = sorted({str(r.get("Subject") or "") for r in marks if r.get("Subject")}, key=lambda s: s.lower())
    by_lid: dict[str, list[dict]] = defaultdict(list)
    for r in marks:
        lid = str(r.get("LearnerID") or "").strip()
        if lid:
            by_lid[lid].append(r)

    rows_out: list[dict] = []
    pass_thr = 40.0
    seq = 0
    for lid, mlist in sorted(by_lid.items(), key=lambda x: x[0]):
        bio = by_key.get(lid)
        if not bio:
            continue
        if class_f and str(bio.get("Class") or "").strip() != class_f:
            continue
        subj_scores: list[dict] = []
        pcts: list[float] = []
        for sub in subjects:
            prs = [
                p
                for p in (
                    _management_mark_row_pct(r) for r in mlist if str(r.get("Subject") or "") == sub
                )
                if p is not None
            ]
            av = sum(prs) / len(prs) if prs else None
            subj_scores.append({"subject": sub, "percent": av if av is not None else ""})
            if av is not None:
                pcts.append(float(av))
        avg = _management_round_percentage_half_up(sum(pcts) / len(pcts), 1) if pcts else None
        code = "P" if (avg is not None and avg >= pass_thr) else "NP"
        if lf == "pass" and not (avg is not None and avg >= pass_thr):
            continue
        if lf == "notpass" and (avg is None or avg >= pass_thr):
            continue
        if code_f and code != code_f:
            continue
        seq += 1
        name = f"{bio.get('FName', '') or ''} {bio.get('SName', '') or ''}".strip()
        rows_out.append(
            {
                "no": seq,
                "admissionNumber": str(bio.get("LearnerID") or bio.get("AccessionNo") or ""),
                "learnerName": name,
                "dateOfBirth": str(bio.get("DOB") or ""),
                "gender": str(bio.get("Gender") or ""),
                "yearsInGrade": "—",
                "yearsInPhase": "—",
                "daysAbsent": "",
                "subjectScores": subj_scores,
                "averagePercent": avg if avg is not None else "",
                "code": code,
            }
        )

    pass_c = sum(1 for r in rows_out if r.get("code") == "P")
    np_c = len(rows_out) - pass_c
    all_avg = None
    avs = [float(r["averagePercent"]) for r in rows_out if r.get("averagePercent") not in ("", None)]
    if avs:
        all_avg = _management_round_percentage_half_up(sum(avs) / len(avs), 1)
    return {
        "rows": rows_out,
        "subjects": subjects,
        "summary": {
            "learners": len(rows_out),
            "passCount": pass_c,
            "notPassCount": np_c,
            "averagePercent": all_avg,
        },
    }


def _management_result_analysis_aggregate(year: str, term: str):
    raw = _management_fetch_marks_with_grades(year, term)
    # ReportMarks may reference a learner as numeric ID in some rows and as LearnerID (code)
    # in others. Unioning raw keys over-counts "assessed" learners and inflates failures.
    li_for_keys = (
        mdb_conn.execute_query(
            "SELECT [ID], [LearnerID] FROM Learner_Info WHERE [Status] = ?",
            ("C",),
        )
        or []
    )
    _lk = build_learner_lookup_by_any_id(li_for_keys)

    def _canonical_lid(mark_lid: str) -> str:
        s = str(mark_lid or "").strip()
        if not s:
            return s
        info = _lk.get(s)
        if info:
            cid = str(info.get("id") or "").strip()
            if cid:
                return cid
        return s

    groups: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for r in raw:
        m_g = re.search(r"(\d+)", str(r.get("Grade") or ""))
        if not m_g:
            continue
        g = int(m_g.group(1))
        sub = _management_normalize_subject_label(str(r.get("Subject") or ""))
        lid = _canonical_lid(str(r.get("LearnerID") or "").strip())
        if not sub or not lid:
            continue
        groups[(sub, g, lid)].append(r)

    cell: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    gl_nested: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for (sub, g, lid), lst in groups.items():
        pcts: list[float] = []
        for row in lst:
            mk = row.get("Mark")
            tk = row.get("TotalMark")
            try:
                tkf = float(tk)
                mkf = float(mk or 0)
            except (TypeError, ValueError):
                continue
            if tkf <= 0:
                continue
            raw_pct = mkf / tkf * 100.0
            pcts.append(_management_round_percentage_half_up(raw_pct, 0))
        if not pcts:
            continue
        agg = _management_round_percentage_half_up(sum(pcts) / len(pcts), 0)
        cell[(sub, g)][lid] = float(agg)
        gl_nested[g][lid].append(float(agg))

    gl_out = {g: dict(inner) for g, inner in gl_nested.items()}
    return dict(cell), gl_out, _lk


def _management_cell_pct(by_cell: dict, grade: int, learner_id: str, pred) -> float | None:
    lid = str(learner_id)
    g = int(grade)
    best: float | None = None
    for (sub, gg), mp in by_cell.items():
        if gg != g or lid not in mp:
            continue
        if not pred(sub):
            continue
        v = float(mp[lid])
        best = v if best is None else max(best, v)
    return best


def _management_learner_passes_result_analysis(
    by_cell: dict,
    promotion_register: dict,
    grade: int,
    learner_id: str,
) -> bool:
    """Marks-based promotion check aligned with school EMS table tests."""
    _ = promotion_register
    g = int(grade)
    if g <= 9 and _management_cell_pct(by_cell, g, learner_id, _management_is_afrikaans_home_language_subject) is not None:
        return False

    if g <= 3:
        ehl = _management_cell_pct(
            by_cell, g, learner_id, lambda s: _management_is_home_language_subject(s) and _management_is_english_subject(s)
        )
        if ehl is None or ehl < float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD_HOME_LANGUAGE):
            return False
        fal = _management_cell_pct(by_cell, g, learner_id, _management_is_fal_subject)
        if fal is None or fal < float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD):
            return False
        maths = _management_cell_pct(by_cell, g, learner_id, _management_is_maths_subject)
        if maths is None or maths < float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD):
            return False
        life = _management_cell_pct(
            by_cell,
            g,
            learner_id,
            lambda s: _management_is_life_skills_subject(s) or _management_is_life_orientation_subject(s),
        )
        return life is not None and life >= float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)

    if 4 <= g <= 6:
        slots = (
            (lambda s: _management_is_home_language_subject(s) and _management_is_english_subject(s), float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD_HOME_LANGUAGE)),
            (_management_is_fal_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_maths_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_natural_sciences_technology_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_social_sciences_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (
                lambda s: _management_is_life_skills_subject(s) or _management_is_life_orientation_subject(s),
                float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD),
            ),
        )
        for pred, thr in slots:
            v = _management_cell_pct(by_cell, g, learner_id, pred)
            if v is None or v < thr:
                return False
        return True

    if 7 <= g <= 9:
        slots = (
            (lambda s: _management_is_home_language_subject(s) and _management_is_english_subject(s), float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD_HOME_LANGUAGE)),
            (_management_is_fal_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_maths_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_natural_sciences_technology_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_social_sciences_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_life_orientation_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_technology_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_ems_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
            (_management_is_creative_arts_subject, float(RESULT_ANALYSIS_PASS_PCT_THRESHOLD)),
        )
        for pred, thr in slots:
            v = _management_cell_pct(by_cell, g, learner_id, pred)
            if v is None or v < thr:
                return False
        return True

    if g >= 10:
        for (sub, gg), mp in by_cell.items():
            if gg != g or learner_id not in mp:
                continue
            if not _management_subject_in_overall_pass_computation(g, sub):
                continue
            thr = _management_marks_pass_threshold_pct_for_subject(g, sub)
            if thr is None:
                continue
            if float(mp[learner_id]) + 1e-9 < float(thr):
                return False
        return True

    return False


def _management_promotion_diagnostics_for_grades(year: str, term: str, grades: list[int]) -> dict:
    _ = year, term
    return {
        "grades": {str(g): {"howTotalsWereChosen": "Summary-only export; full diagnostics not wired."} for g in grades},
    }


def _management_phase_note_for_key(phase_key: str) -> str:
    if phase_key == "senior":
        return str(RESULT_ANALYSIS_PASS_PCT_TABLE_NOTE_SENIOR)
    if phase_key == "fet":
        return str(RESULT_ANALYSIS_PASS_PCT_TABLE_NOTE_FET)
    return (
        "Pass% column (Grades 1–6): English Home Language ≥50%; Afrikaans First Additional Language, Mathematics, "
        "and other phase subjects ≥40% where applicable. Marks-based promotion uses EMS minima."
    )


def _management_subject_row_metrics(by_cell: dict, grade: int, subject: str) -> dict:
    g = int(grade)
    col = by_cell.get((_management_normalize_subject_label(subject), g)) or {}
    if not col:
        return {"count": 0}
    pcts = [float(v) for v in col.values()]
    thr = float(_management_pass_pct_threshold_for_subject_grade(g, subject))
    passed = sum(1 for p in pcts if p >= thr)
    passed50 = sum(1 for p in pcts if p >= 50.0)
    n = len(pcts)
    avg = _management_round_percentage_half_up(sum(pcts) / n, 2)
    return {
        "count": n,
        "passPct": _management_round_percentage_half_up(100.0 * passed / n, 2),
        "passAt50Pct": _management_round_percentage_half_up(100.0 * passed50 / n, 2),
        "average": avg,
    }


def _management_build_result_analysis_payload(year: str, term: str) -> dict:
    year_s, term_s = str(year).strip(), str(term).strip()
    by_cell, _gl, by_any = _management_result_analysis_aggregate(year_s, term_s)
    _, promo_rows = _management_load_promotion_register(year_s, term_s)
    promo_lookup = _management_build_promo_fast_lookup(promo_rows, by_any)

    school_name = (os.environ.get("SCHOOL_DISPLAY_NAME") or "").strip() or "School"
    meta = {
        "schoolName": school_name,
        "year": year_s,
        "term": term_s,
        "passThresholdNote": (
            "Inclusive pass boundaries (≥). Percentages rounded half-up. "
            "Summary promoted / failed / progressed follow LearnerPromotion codes (P, NP, PG) when present; "
            "if no register row, marks-based EMS minima apply."
        ),
    }

    phases_out: list[dict] = []

    for phase in RESULT_ANALYSIS_PHASES:
        phase_key = str(phase.get("key") or "")
        phase_grades = tuple(int(x) for x in phase.get("grades") or ())
        subjects_set: set[str] = set()
        for (sub, gg) in by_cell.keys():
            if gg in phase_grades:
                subjects_set.add(sub)
        subjects_sorted = sorted(subjects_set, key=lambda s: s.lower())

        subjects_rows: list[dict] = []
        for sub in subjects_sorted:
            gmap: dict[str, dict] = {}
            for g in phase_grades:
                metrics = _management_subject_row_metrics(by_cell, g, sub)
                if metrics.get("count"):
                    gmap[str(g)] = metrics
            if gmap:
                subjects_rows.append({"subject": sub, "grades": gmap})

        summary: dict[str, dict] = {}
        show_prog = bool(phase.get("show_progressed_row"))
        for g in phase_grades:
            learners_g: set[str] = set()
            for (sub, gg), mp in by_cell.items():
                if gg != g or not _management_subject_in_overall_pass_computation(g, sub):
                    continue
                learners_g.update(mp.keys())
            assessed = len(learners_g)
            promoted, failed, progressed_n = _management_register_promotion_summary_for_learners(
                by_cell, promo_lookup, by_any, g, learners_g
            )
            successes = promoted + progressed_n
            total_pct = (
                _management_round_percentage_half_up(100.0 * successes / assessed, 2) if assessed else None
            )
            entry = {
                "assessed": assessed,
                "promoted": promoted,
                "failed": failed,
                "totalPassPct": total_pct,
            }
            if show_prog:
                entry["progressed"] = progressed_n
            summary[str(g)] = entry

        phases_out.append(
            {
                "key": phase_key,
                "title": phase.get("title") or "",
                "grades": list(phase_grades),
                "showProgressedRow": show_prog,
                "passPctColumnNote": _management_phase_note_for_key(phase_key),
                "subjects": subjects_rows,
                "summary": summary,
            }
        )

    return {"meta": meta, "phases": phases_out}


def _management_norm_promo_code_val(v) -> str:
    return str(v if v is not None else "").strip().upper()


def _management_promotion_code_cell(row: dict, *keys: str) -> str:
    for k in keys:
        if k in row and row.get(k) is not None and str(row.get(k)).strip() != "":
            return _management_norm_promo_code_val(row.get(k))
        lk = k.lower()
        for rk in row:
            if str(rk).lower() == lk:
                if row.get(rk) is not None and str(row.get(rk)).strip() != "":
                    return _management_norm_promo_code_val(row.get(rk))
    return ""


def _management_register_bucket_from_row(row: dict) -> str:
    """Return promoted | progressed | failed | unknown (aligned with scripts/audit_promotion_codes.py)."""
    sel = _management_promotion_code_cell(row, "CodeSelected", "codeselected")
    auto = _management_promotion_code_cell(row, "CodeAuto", "codeauto")
    sched = _management_promotion_code_cell(row, "CodeSched", "codesched")
    pd_raw = row.get("PromotionDecision")
    if pd_raw is None:
        for rk in row:
            if str(rk).lower() == "promotiondecision":
                pd_raw = row.get(rk)
                break
    pd_s = _management_norm_promo_code_val(pd_raw)
    codes_present = bool(sel or auto or sched or pd_s)
    if sched == "PG" or "PROGRESSED" in sched:
        return "progressed"
    if sel == "NP" or auto == "NP" or sched == "NP":
        return "failed"
    if pd_s == "14":
        return "failed"
    has_p = sel == "P" or auto == "P" or sched == "P"
    has_np = sel == "NP" or auto == "NP" or sched == "NP"
    if has_p and not has_np:
        return "promoted"
    if pd_s == "6":
        return "promoted"
    if not codes_present:
        return "unknown"
    return "unknown"


def _management_fetch_promotion_register_rows(year: str, term: str) -> list[dict]:
    y, t = str(year).strip(), str(term).strip()
    sel = (
        "SELECT CSTR(lp.LearnerId) AS LearnerID, CSTR(lp.Grade) AS Grade, "
        "lp.CodeSelected, lp.CodeAuto, lp.CodeSched, lp.PromotionDecision "
        "FROM LearnerPromotion lp"
    )
    attempts: list[tuple[str, tuple]] = []
    for ycol in _management_learner_promotion_year_columns():
        attempts.append(
            (
                sel + f", ReportCycles rc WHERE lp.ReportId = rc.CycleId AND CSTR(lp.{ycol})=? AND CSTR(rc.Term)=?",
                (y, t),
            )
        )
    for ycol in _management_learner_promotion_year_columns():
        attempts.append((sel + f" WHERE CSTR(lp.{ycol})=?", (y,)))
    for q, params in attempts:
        rows = mdb_conn.execute_query(q, params) or []
        if rows:
            return rows
    return []


def _management_dedupe_promotion_by_grade_learner(rows: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for r in rows or []:
        lid = str(r.get("LearnerID") or "").strip()
        g = str(r.get("Grade") or "").strip()
        if not lid or not g.isdigit():
            continue
        key = (g, lid)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def _management_marks_id_for_promotion(g: int, lid_lp: str, glists: dict) -> str:
    lids = glists.get(int(g)) or set()
    if not lids:
        return str(lid_lp).strip()
    c_lp = set(get_learner_match_candidates(lid_lp))
    for mlid in lids:
        mlid_s = str(mlid).strip()
        if mlid_s == str(lid_lp).strip() or mlid_s in c_lp:
            return mlid_s
        if c_lp & set(get_learner_match_candidates(mlid_s)):
            return mlid_s
    return str(lid_lp).strip()


def _management_build_promo_fast_lookup(promo_rows: list[dict], by_any_id: dict) -> dict[tuple[int, str], dict]:
    """Map (grade, learner id variant) -> promotion row; first row wins (dedup order)."""
    promo_lookup: dict[tuple[int, str], dict] = {}
    for r in promo_rows or []:
        m_g = re.search(r"(\d+)", str(r.get("Grade") or ""))
        if not m_g:
            continue
        gg = int(m_g.group(1))
        lid = str(r.get("LearnerID") or "").strip()
        if not lid:
            continue
        for c in _learner_match_candidates_with_lookup(lid, by_any_id):
            cs = str(c).strip()
            if not cs:
                continue
            key = (gg, cs)
            if key not in promo_lookup:
                promo_lookup[key] = r
    return promo_lookup


def _management_find_promo_row_fast(promo_lookup: dict, by_any_id: dict, g: int, mlid: str) -> dict | None:
    for c in _learner_match_candidates_with_lookup(mlid, by_any_id):
        r = promo_lookup.get((int(g), str(c).strip()))
        if r is not None:
            return r
    return None


def _management_load_promotion_register(year: str, term: str) -> tuple[dict[tuple[int, str], dict], list[dict]]:
    """Single fetch: deduped LearnerPromotion rows plus (grade, LearnerId) index."""
    promo_rows = _management_dedupe_promotion_by_grade_learner(_management_fetch_promotion_register_rows(year, term))
    promo_by_key: dict[tuple[int, str], dict] = {}
    for r in promo_rows:
        m_g = re.search(r"(\d+)", str(r.get("Grade") or ""))
        if not m_g:
            continue
        gg = int(m_g.group(1))
        lid = str(r.get("LearnerID") or "").strip()
        if lid:
            promo_by_key[(gg, lid)] = r
    return promo_by_key, promo_rows


def _management_register_promotion_summary_for_learners(
    by_cell: dict,
    promo_lookup: dict[tuple[int, str], dict],
    by_any_id: dict,
    grade: int,
    learner_ids: set[str],
) -> tuple[int, int, int]:
    """Result Analysis totals: (promoted P, failed NP, progressed PG) using register when present."""
    g = int(grade)
    promoted = failed = progressed_n = 0
    for lid in learner_ids:
        row = _management_find_promo_row_fast(promo_lookup, by_any_id, g, lid)
        if row:
            b = _management_register_bucket_from_row(row)
            if b == "failed":
                failed += 1
            elif b == "promoted":
                promoted += 1
            elif b == "progressed":
                progressed_n += 1
            else:
                if _management_learner_passes_result_analysis(by_cell, {}, g, lid):
                    promoted += 1
                else:
                    failed += 1
        else:
            if _management_learner_passes_result_analysis(by_cell, {}, g, lid):
                promoted += 1
            else:
                failed += 1
    return promoted, failed, progressed_n


def _management_achievement_tri_state(promo_row: dict | None, by_cell: dict, g: int, mlid: str) -> str:
    """meet | progress | notMeet"""
    if promo_row:
        reg = _management_register_bucket_from_row(promo_row)
        if reg == "promoted":
            return "meet"
        if reg == "progressed":
            return "progress"
        if reg == "failed":
            return "notMeet"
    if _management_learner_passes_result_analysis(by_cell, {}, int(g), str(mlid).strip()):
        return "meet"
    return "notMeet"


def _management_is_male_gender_label(gen: str) -> bool:
    s = str(gen or "").strip().lower()
    return s in {"m", "male", "boy", "boys"} or s.startswith("m ")


def _management_is_female_gender_label(gen: str) -> bool:
    s = str(gen or "").strip().lower()
    return s in {"f", "female", "girl", "girls"} or s.startswith("f ")


def _management_build_achievement_promotion_analysis_payload(year: str, term: str, phase: str) -> dict:
    year_s, term_s = str(year).strip(), str(term).strip()
    by_cell, glists, by_any = _management_result_analysis_aggregate(year_s, term_s)
    _, promo_rows = _management_load_promotion_register(year_s, term_s)
    promo_lookup = _management_build_promo_fast_lookup(promo_rows, by_any)

    keys: set[tuple[int, str]] = set()
    for g, lids in glists.items():
        for mlid in lids:
            keys.add((int(g), str(mlid).strip()))
    for r in promo_rows:
        m_g = re.search(r"(\d+)", str(r.get("Grade") or ""))
        if not m_g:
            continue
        g = int(m_g.group(1))
        lid_lp = str(r.get("LearnerID") or "").strip()
        mlid = _management_marks_id_for_promotion(g, lid_lp, glists)
        keys.add((g, mlid))

    phase_sel = str(phase or "").strip().lower()
    pmap = {"foundation": {1, 2, 3}, "intermediate": {4, 5, 6}, "senior": {7, 8, 9}, "fet": {10, 11, 12}}
    allowed = pmap.get(phase_sel)
    if allowed:
        keys = {(g, m) for (g, m) in keys if int(g) in allowed}

    grade_keys: dict[int, list[str]] = defaultdict(list)
    for g, mlid in keys:
        grade_keys[int(g)].append(mlid)

    gender_cache: dict[str, str] = {}

    def _gender_for(mlid: str) -> str:
        if mlid in gender_cache:
            return gender_cache[mlid]
        info = fetch_learner_info_by_id(mlid)
        g = str((info or {}).get("gender", "") or "").strip()
        gender_cache[mlid] = g
        return g

    pop_m: dict[int, int] = defaultdict(int)
    pop_f: dict[int, int] = defaultdict(int)
    pop_u: dict[int, int] = defaultdict(int)
    for g, mlids in grade_keys.items():
        seen: set[str] = set()
        for mlid in mlids:
            if mlid in seen:
                continue
            seen.add(mlid)
            gen = _gender_for(mlid)
            if _management_is_male_gender_label(gen):
                pop_m[g] += 1
            elif _management_is_female_gender_label(gen):
                pop_f[g] += 1
            else:
                pop_u[g] += 1

    acc: dict[int, dict[str, int]] = defaultdict(
        lambda: {"nm_m": 0, "nm_f": 0, "nm_u": 0, "pr_m": 0, "pr_f": 0, "pr_u": 0, "mt_m": 0, "mt_f": 0, "mt_u": 0}
    )
    for g, mlid in sorted(keys, key=lambda t: (t[0], t[1])):
        promo = _management_find_promo_row_fast(promo_lookup, by_any, g, mlid)
        tri = _management_achievement_tri_state(promo, by_cell, g, mlid)
        gen = _gender_for(mlid)
        cell = acc[int(g)]
        if tri == "notMeet":
            if _management_is_male_gender_label(gen):
                cell["nm_m"] += 1
            elif _management_is_female_gender_label(gen):
                cell["nm_f"] += 1
            else:
                cell["nm_u"] += 1
        elif tri == "progress":
            if _management_is_male_gender_label(gen):
                cell["pr_m"] += 1
            elif _management_is_female_gender_label(gen):
                cell["pr_f"] += 1
            else:
                cell["pr_u"] += 1
        else:
            if _management_is_male_gender_label(gen):
                cell["mt_m"] += 1
            elif _management_is_female_gender_label(gen):
                cell["mt_f"] += 1
            else:
                cell["mt_u"] += 1

    def _pct(num: int, den: int) -> float:
        return _management_round_percentage_half_up(100.0 * float(num) / float(den), 2) if den else 0.0

    def _row_for_grade(g: int) -> dict:
        c = acc[g]
        pm, pf, pu = pop_m[g], pop_f[g], pop_u[g]
        pall = pm + pf + pu
        nm_t = c["nm_m"] + c["nm_f"] + c["nm_u"]
        pr_t = c["pr_m"] + c["pr_f"] + c["pr_u"]
        mt_t = c["mt_m"] + c["mt_f"] + c["mt_u"]
        return {
            "grade": g,
            "notMeetMaleCount": c["nm_m"],
            "notMeetMalePct": _pct(c["nm_m"], pm),
            "notMeetFemaleCount": c["nm_f"],
            "notMeetFemalePct": _pct(c["nm_f"], pf),
            "notMeetTotalCount": nm_t,
            "notMeetTotalPct": _pct(nm_t, pall),
            "progressMaleCount": c["pr_m"],
            "progressMalePct": _pct(c["pr_m"], pm),
            "progressFemaleCount": c["pr_f"],
            "progressFemalePct": _pct(c["pr_f"], pf),
            "progressTotalCount": pr_t,
            "progressTotalPct": _pct(pr_t, pall),
            "meetMaleCount": c["mt_m"],
            "meetMalePct": _pct(c["mt_m"], pm),
            "meetFemaleCount": c["mt_f"],
            "meetFemalePct": _pct(c["mt_f"], pf),
            "meetTotalCount": mt_t,
            "meetTotalPct": _pct(mt_t, pall),
            "grandMaleCount": pm,
            "grandMalePct": 100.0 if pm else 0.0,
            "grandFemaleCount": pf,
            "grandFemalePct": 100.0 if pf else 0.0,
            "grandTotalCount": pall,
        }

    grades_sorted = sorted(grade_keys.keys(), key=int)
    rows_out = [_row_for_grade(g) for g in grades_sorted]

    t_acc = {"nm_m": 0, "nm_f": 0, "nm_u": 0, "pr_m": 0, "pr_f": 0, "pr_u": 0, "mt_m": 0, "mt_f": 0, "mt_u": 0}
    t_pm = t_pf = t_pu = 0
    for g in grades_sorted:
        t_pm += pop_m[g]
        t_pf += pop_f[g]
        t_pu += pop_u[g]
        for k in t_acc:
            t_acc[k] += acc[g][k]
    totals = {
        "grade": "All",
        "notMeetMaleCount": t_acc["nm_m"],
        "notMeetMalePct": _pct(t_acc["nm_m"], t_pm),
        "notMeetFemaleCount": t_acc["nm_f"],
        "notMeetFemalePct": _pct(t_acc["nm_f"], t_pf),
        "notMeetTotalCount": t_acc["nm_m"] + t_acc["nm_f"] + t_acc["nm_u"],
        "notMeetTotalPct": _pct(t_acc["nm_m"] + t_acc["nm_f"] + t_acc["nm_u"], t_pm + t_pf + t_pu),
        "progressMaleCount": t_acc["pr_m"],
        "progressMalePct": _pct(t_acc["pr_m"], t_pm),
        "progressFemaleCount": t_acc["pr_f"],
        "progressFemalePct": _pct(t_acc["pr_f"], t_pf),
        "progressTotalCount": t_acc["pr_m"] + t_acc["pr_f"] + t_acc["pr_u"],
        "progressTotalPct": _pct(t_acc["pr_m"] + t_acc["pr_f"] + t_acc["pr_u"], t_pm + t_pf + t_pu),
        "meetMaleCount": t_acc["mt_m"],
        "meetMalePct": _pct(t_acc["mt_m"], t_pm),
        "meetFemaleCount": t_acc["mt_f"],
        "meetFemalePct": _pct(t_acc["mt_f"], t_pf),
        "meetTotalCount": t_acc["mt_m"] + t_acc["mt_f"] + t_acc["mt_u"],
        "meetTotalPct": _pct(t_acc["mt_m"] + t_acc["mt_f"] + t_acc["mt_u"], t_pm + t_pf + t_pu),
        "grandMaleCount": t_pm,
        "grandMalePct": 100.0 if t_pm else 0.0,
        "grandFemaleCount": t_pf,
        "grandFemalePct": 100.0 if t_pf else 0.0,
        "grandTotalCount": t_pm + t_pf + t_pu,
    }

    return {"meta": {"year": year_s, "term": term_s}, "rows": rows_out, "totals": totals}


try:
    from inventory_routes import register_inventory

    register_inventory(app)
except Exception as _inv_exc:
    app.logger.warning("Inventory routes could not be registered: %s", _inv_exc)

try:
    from admin_routes import register_admin_routes

    register_admin_routes(app)
except Exception as _adm_exc:
    app.logger.warning("Admin routes could not be registered: %s", _adm_exc)


if __name__ == "__main__":
    # Used by start_app.bat / start_app.ps1 (`python app.py`). Flask CLI (`flask run`) remains supported.
    _port_raw = str(os.environ.get("PORT") or os.environ.get("FLASK_RUN_PORT") or "5000").strip()
    try:
        _port = int(_port_raw)
    except ValueError:
        _port = 5000
    _host = str(os.environ.get("FLASK_RUN_HOST") or "127.0.0.1").strip() or "127.0.0.1"
    _debug = str(os.environ.get("FLASK_DEBUG") or "").strip().lower() in {"1", "true", "yes", "on"}
    socketio.run(app, host=_host, port=_port, debug=_debug, allow_unsafe_werkzeug=True)
