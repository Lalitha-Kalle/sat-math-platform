from pathlib import Path

from flask import Blueprint, jsonify

from db.connection import get_connection
from services.auth import login_required
from services.chapters import get_chapters_full, get_chapters_summary
from services.excel_sync import sync_ppt_links

api_bp = Blueprint("api", __name__, url_prefix="/api")

XLSX_PATH = Path(__file__).resolve().parent.parent / "sat-math.xlsx"


@api_bp.route("/chapters")
@login_required
def chapters_summary():
    conn = get_connection()
    try:
        return jsonify(get_chapters_summary(conn))
    finally:
        conn.close()


@api_bp.route("/chapters/full")
@login_required
def chapters_full():
    conn = get_connection()
    try:
        return jsonify(get_chapters_full(conn))
    finally:
        conn.close()


@api_bp.route("/admin/sync-excel", methods=["POST"])
@login_required
def sync_excel():
    """Re-reads sat-math.xlsx and refreshes each chapter's PPT link without reseeding."""
    if not XLSX_PATH.exists():
        return jsonify({"error": f"{XLSX_PATH.name} not found"}), 404
    conn = get_connection()
    try:
        updated = sync_ppt_links(conn, XLSX_PATH)
    except PermissionError:
        return jsonify({"error": f"{XLSX_PATH.name} is open elsewhere — close it and retry"}), 423
    finally:
        conn.close()
    return jsonify({"updated": updated})
