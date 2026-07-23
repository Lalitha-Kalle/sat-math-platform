"""Read access to chapters/slides/questions, shaped to match the frontend's
original CHAPTERS[] structure so templates/index.html needs no rework beyond
receiving that structure from the server instead of a hardcoded literal.
"""
import json


def get_chapters_summary(conn):
    rows = conn.execute(
        "SELECT code, name, seq, ppt_link, ppt_embed_url FROM chapters ORDER BY seq"
    ).fetchall()
    return [
        {
            "id": r["code"],
            "name": r["name"],
            "seq": r["seq"],
            "ppt_link": r["ppt_link"],
            "ppt_embed_url": r["ppt_embed_url"],
        }
        for r in rows
    ]


def get_chapters_full(conn):
    chapters = conn.execute("SELECT * FROM chapters ORDER BY seq").fetchall()
    result = []
    for ch in chapters:
        slide_rows = conn.execute(
            "SELECT kicker, heading, sub, bullets, note FROM slides "
            "WHERE chapter_id = ? ORDER BY position",
            (ch["id"],),
        ).fetchall()
        slides = [
            {
                "k": s["kicker"],
                "h": s["heading"],
                "s": s["sub"],
                "b": json.loads(s["bullets"]),
                "n": s["note"],
            }
            for s in slide_rows
        ]

        result.append(
            {
                "id": ch["code"],
                "name": ch["name"],
                "deck": ch["ppt_embed_url"] or "",
                "slides": slides,
                # Quiz questions come from data/sat_qa_bank.sqlite3 only (see
                # services.qa_bank.merge_qa_chapters), not from this database.
                "q": {"E": [], "M": [], "H": []},
            }
        )
    return result
