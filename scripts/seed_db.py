"""Creates the SQLite schema and seeds it with the built-in chapters, slides
and question bank (chapters_seed.json), then syncs each chapter's PPT link
from sat-math.xlsx.

Run this once to set up the database, and again any time chapters_seed.json
or sat-math.xlsx changes:

    python scripts/seed_db.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db.connection import get_connection, init_db  # noqa: E402
from services.auth import seed_default_user  # noqa: E402
from services.excel_sync import sync_ppt_links  # noqa: E402

SEED_PATH = Path(__file__).resolve().parent / "chapters_seed.json"
XLSX_PATH = ROOT / "sat-math.xlsx"


def main():
    init_db()
    conn = get_connection()

    seed_default_user(conn)

    conn.execute("DELETE FROM questions")
    conn.execute("DELETE FROM slides")
    conn.execute("DELETE FROM chapters")

    chapters = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    for seq, chap in enumerate(chapters, start=1):
        cur = conn.execute(
            "INSERT INTO chapters (code, seq, name, ppt_link, ppt_embed_url) "
            "VALUES (?, ?, ?, NULL, NULL)",
            (chap["id"], seq, chap["name"]),
        )
        chapter_id = cur.lastrowid

        for pos, slide in enumerate(chap["slides"], start=1):
            conn.execute(
                "INSERT INTO slides (chapter_id, position, kicker, heading, sub, bullets, note) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (chapter_id, pos, slide["k"], slide["h"], slide["s"], json.dumps(slide["b"]), slide["n"]),
            )

        for level in ("E", "M", "H"):
            for pos, q in enumerate(chap["q"][level], start=1):
                conn.execute(
                    "INSERT INTO questions "
                    "(chapter_id, level, position, stem, options, correct_index, explanation) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (chapter_id, level, pos, q["s"], json.dumps(q["o"]), q["c"], q["e"]),
                )

    conn.commit()
    print(f"Seeded {len(chapters)} chapters into {ROOT / 'data' / 'sat_math.sqlite3'}")
    print("Default login ready: master_tutor / tp@1234")

    if XLSX_PATH.exists():
        try:
            updated = sync_ppt_links(conn, XLSX_PATH)
            print(f"Synced PPT links for {updated} chapter(s) from {XLSX_PATH.name}")
        except PermissionError:
            print(f"Could not read {XLSX_PATH.name} — close it in Excel and re-run to sync PPT links.")
    else:
        print(f"No {XLSX_PATH.name} found next to app.py — skipping PPT link sync.")

    conn.close()


if __name__ == "__main__":
    main()
