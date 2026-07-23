"""Reads the separate qa_bank database (data/sat_qa_bank.sqlite3, loaded by
scripts/load_qa_bank.py) and shapes it to match the same chapter structure
services.chapters.get_chapters_full() produces, so the frontend's existing
chapter picker / difficulty picker / quiz runner can render it unchanged.
"""
import re

DIFFICULTY_TO_LEVEL = {"easy": "E", "medium": "M", "hard": "H"}
OPTION_LETTER_TO_INDEX = {"A": 0, "B": 1, "C": 2, "D": 3}


def _slugify(name):
    return "qa-" + re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def get_qa_chapters(conn):
    chapters = conn.execute("SELECT id, name FROM chapters ORDER BY name").fetchall()
    result = []
    for ch in chapters:
        q = {"E": [], "M": [], "H": []}
        rows = conn.execute(
            "SELECT difficulty, question, option_a, option_b, option_c, option_d, "
            "       correct_option, explanation "
            "FROM questions WHERE chapter_id = ? ORDER BY id",
            (ch["id"],),
        ).fetchall()
        for r in rows:
            level = DIFFICULTY_TO_LEVEL.get((r["difficulty"] or "").strip().lower())
            if not level:
                continue
            q[level].append(
                {
                    "s": r["question"],
                    "o": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
                    "c": OPTION_LETTER_TO_INDEX.get((r["correct_option"] or "").strip().upper(), 0),
                    "e": r["explanation"],
                }
            )

        result.append(
            {
                "id": _slugify(ch["name"]),
                "name": ch["name"],
                "deck": "",
                "slides": [
                    {
                        "k": "Question bank",
                        "h": ch["name"],
                        "s": "Loaded from sat-ques-and-ans.xlsx",
                        "b": [],
                        "n": "No slide deck for this chapter yet — use Quiz mode to practice.",
                    }
                ],
                "q": q,
            }
        )
    return result


def _normalize_name(name):
    return re.sub(r"[^a-z0-9]+", " ", name.strip().lower()).strip()


def merge_qa_chapters(chapters, qa_chapters):
    """Merges qa_chapters into chapters: questions for a qa_bank chapter whose
    name matches an existing chapter (ignoring case/punctuation) are appended
    to that chapter's question bank instead of appearing as a duplicate entry
    in the chapter picker. Only genuinely new chapter names are added.
    """
    by_name = {_normalize_name(c["name"]): c for c in chapters}
    for qc in qa_chapters:
        target = by_name.get(_normalize_name(qc["name"]))
        if target:
            for level in ("E", "M", "H"):
                target["q"][level].extend(qc["q"][level])
        else:
            chapters.append(qc)
    return chapters
