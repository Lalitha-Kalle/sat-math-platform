from functools import wraps

from flask import redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

DEFAULT_USERNAME = "master_tutor"
DEFAULT_PASSWORD = "tp@1234"


def seed_default_user(conn):
    """Creates the default tutor login if no such user exists yet (idempotent)."""
    conn.execute(
        "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
        (DEFAULT_USERNAME, generate_password_hash(DEFAULT_PASSWORD)),
    )
    conn.commit()


def verify_user(conn, username, password):
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped
