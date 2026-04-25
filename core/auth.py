"""
Auth Manager — SQLite-based user authentication.
Handles signup, login, logout, session, and per-user data isolation.
Passwords are hashed with bcrypt.
"""
import os
import sqlite3
import hashlib
import hmac
import secrets
import time
from pathlib import Path

DB_PATH = os.getenv("AUTH_DB_PATH", "./data/users.db")


def _get_conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create users and sessions tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password_hash TEXT  NOT NULL,
            full_name   TEXT    DEFAULT '',
            role        TEXT    DEFAULT 'user',
            created_at  TEXT    DEFAULT (datetime('now')),
            last_login  TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT    PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            created_at  REAL    NOT NULL,
            expires_at  REAL    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS user_datasets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            filename    TEXT    NOT NULL,
            uploaded_at TEXT    DEFAULT (datetime('now')),
            row_count   INTEGER DEFAULT 0,
            col_count   INTEGER DEFAULT 0,
            chroma_key  TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  PASSWORD HASHING (SHA-256 + salt, no bcrypt dependency)
# ─────────────────────────────────────────────

def _hash_password(password: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000)
    return f"{salt}${key.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, _ = stored_hash.split("$", 1)
        return hmac.compare_digest(_hash_password(password, salt), stored_hash)
    except Exception:
        return False


# ─────────────────────────────────────────────
#  USER MANAGEMENT
# ─────────────────────────────────────────────

def create_user(username: str, email: str, password: str, full_name: str = "") -> dict:
    """Register a new user. Returns {ok, message}."""
    if len(password) < 6:
        return {"ok": False, "message": "Password must be at least 6 characters."}
    if len(username) < 3:
        return {"ok": False, "message": "Username must be at least 3 characters."}

    conn = _get_conn()
    try:
        pw_hash = _hash_password(password)
        conn.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username.lower().strip(), email.lower().strip(), pw_hash, full_name.strip()),
        )
        conn.commit()
        return {"ok": True, "message": "Account created successfully!"}
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return {"ok": False, "message": "Username already taken."}
        if "email" in str(e):
            return {"ok": False, "message": "Email already registered."}
        return {"ok": False, "message": "Registration failed."}
    finally:
        conn.close()


def authenticate_user(username_or_email: str, password: str) -> dict:
    """Verify credentials. Returns {ok, user_id, username, full_name, role} or {ok, message}."""
    conn = _get_conn()
    try:
        val = username_or_email.lower().strip()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", (val, val)
        ).fetchone()

        if not row:
            return {"ok": False, "message": "User not found."}
        if not _verify_password(password, row["password_hash"]):
            return {"ok": False, "message": "Incorrect password."}

        # Update last login
        conn.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (row["id"],))
        conn.commit()

        return {
            "ok": True,
            "user_id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "email": row["email"],
            "role": row["role"],
        }
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    conn = _get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def change_password(user_id: int, old_password: str, new_password: str) -> dict:
    conn = _get_conn()
    try:
        row = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return {"ok": False, "message": "User not found."}
        if not _verify_password(old_password, row["password_hash"]):
            return {"ok": False, "message": "Current password is incorrect."}
        if len(new_password) < 6:
            return {"ok": False, "message": "New password must be at least 6 characters."}
        new_hash = _hash_password(new_password)
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        conn.commit()
        return {"ok": True, "message": "Password changed successfully."}
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  SESSION TOKENS
# ─────────────────────────────────────────────

SESSION_DURATION = 60 * 60 * 24 * 7  # 7 days


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now = time.time()
    conn = _get_conn()
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token, user_id, now, now + SESSION_DURATION),
    )
    conn.commit()
    conn.close()
    return token


def validate_session(token: str) -> dict | None:
    """Returns user dict if session is valid, else None."""
    if not token:
        return None
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM sessions WHERE token = ? AND expires_at > ?",
            (token, time.time()),
        ).fetchone()
        if not row:
            return None
        return get_user_by_id(row["user_id"])
    finally:
        conn.close()


def delete_session(token: str):
    conn = _get_conn()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def cleanup_expired_sessions():
    conn = _get_conn()
    conn.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  PER-USER DATASET REGISTRY
# ─────────────────────────────────────────────

def save_dataset_record(user_id: int, name: str, filename: str,
                         row_count: int, col_count: int, chroma_key: str) -> int:
    conn = _get_conn()
    cur = conn.execute(
        """INSERT INTO user_datasets (user_id, name, filename, row_count, col_count, chroma_key)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, name, filename, row_count, col_count, chroma_key),
    )
    conn.commit()
    record_id = cur.lastrowid
    conn.close()
    return record_id


def get_user_datasets(user_id: int) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM user_datasets WHERE user_id = ? ORDER BY uploaded_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_dataset_record(dataset_id: int, user_id: int) -> bool:
    conn = _get_conn()
    cur = conn.execute(
        "DELETE FROM user_datasets WHERE id = ? AND user_id = ?",
        (dataset_id, user_id),
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def list_all_users() -> list[dict]:
    """Admin only — list all users."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, username, email, full_name, role, created_at, last_login FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Initialize DB on import
init_db()