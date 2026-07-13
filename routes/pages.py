import json

from flask import Blueprint, render_template

from db.connection import get_connection
from services.auth import login_required
from services.chapters import get_chapters_full

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
@login_required
def index():
    conn = get_connection()
    try:
        chapters = get_chapters_full(conn)
    finally:
        conn.close()
    # Escape "</" so a stray "</script>" inside seeded content can't break out of the tag.
    chapters_json = json.dumps(chapters, ensure_ascii=False).replace("</", "<\\/")
    return render_template("index.html", chapters_json=chapters_json)
