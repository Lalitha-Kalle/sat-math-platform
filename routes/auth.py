from flask import Blueprint, redirect, render_template, request, session, url_for

from db.connection import get_connection
from services.auth import verify_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_connection()
        try:
            ok = verify_user(conn, username, password)
        finally:
            conn.close()

        if ok:
            session.clear()
            session["user"] = username
            next_url = request.args.get("next")
            if not next_url or not next_url.startswith("/") or next_url.startswith("//"):
                next_url = url_for("pages.index")
            return redirect(next_url)
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
