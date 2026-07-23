"""Loads sat-ques-and-ans.xlsx into its own SQLite database (data/sat_qa_bank.sqlite3),
kept separate from data/sat_math.sqlite3 used by the main app.

Expected sheet columns (Sheet1, row 1 = header):
    Chapter | Option A | Option B | Option C | Option D | Correct Option | Question | Explanation | Difficuilty

Re-running this script wipes and reloads the qa_bank tables, so it's safe to
run again any time sat-ques-and-ans.xlsx changes:

    python scripts/load_qa_bank.py
"""
import sqlite3
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "sat-ques-and-ans.xlsx"
DB_PATH = ROOT / "data" / "sat_qa_bank.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS chapters (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id     INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    difficulty     TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    question       TEXT NOT NULL,
    option_a       TEXT,
    option_b       TEXT,
    option_c       TEXT,
    option_d       TEXT,
    correct_option TEXT NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    explanation    TEXT
);

CREATE INDEX IF NOT EXISTS idx_questions_chapter_difficulty
    ON questions(chapter_id, difficulty);
"""

# Fixed column order matching the current sat-ques-and-ans.xlsx layout.
COL_CHAPTER, COL_A, COL_B, COL_C, COL_D, COL_CORRECT, COL_QUESTION, COL_EXPLANATION, COL_DIFFICULTY = range(9)


def clean(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def read_rows(xlsx_path):
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.worksheets[0]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[COL_CHAPTER]:
            continue
        rows.append(row)
    return rows


def get_or_create_chapter(conn, cache, name):
    if name in cache:
        return cache[name]
    cur = conn.execute("INSERT INTO chapters (name) VALUES (?)", (name,))
    cache[name] = cur.lastrowid
    return cache[name]


def main():
    if not XLSX_PATH.exists():
        print(f"{XLSX_PATH.name} not found next to app.py — nothing to load.")
        sys.exit(1)

    try:
        rows = read_rows(XLSX_PATH)
    except PermissionError:
        print(f"Could not read {XLSX_PATH.name} — close it in Excel and re-run.")
        sys.exit(1)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript(SCHEMA)
        conn.execute("DELETE FROM questions")
        conn.execute("DELETE FROM chapters")

        chapter_cache = {}
        loaded = 0
        for row in rows:
            chapter_name = clean(row[COL_CHAPTER])
            difficulty = clean(row[COL_DIFFICULTY])
            correct_option = clean(row[COL_CORRECT])
            question = clean(row[COL_QUESTION])
            if not (chapter_name and difficulty and correct_option and question):
                continue

            chapter_id = get_or_create_chapter(conn, chapter_cache, chapter_name)
            conn.execute(
                "INSERT INTO questions "
                "(chapter_id, difficulty, question, option_a, option_b, option_c, option_d, "
                " correct_option, explanation) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    chapter_id,
                    difficulty,
                    question,
                    clean(row[COL_A]),
                    clean(row[COL_B]),
                    clean(row[COL_C]),
                    clean(row[COL_D]),
                    correct_option.upper(),
                    clean(row[COL_EXPLANATION]),
                ),
            )
            loaded += 1

        conn.commit()
        print(f"Loaded {loaded} question(s) across {len(chapter_cache)} chapter(s) into {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
