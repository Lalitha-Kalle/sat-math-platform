-- SATly SAT Math Studio -- SQLite schema

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT UNIQUE NOT NULL,      -- e.g. 'c01'
    seq           INTEGER NOT NULL,          -- display order
    name          TEXT NOT NULL,             -- '01 · Math Strategies'
    ppt_link      TEXT,                      -- raw share link, from Excel
    ppt_embed_url TEXT                       -- derived Google Slides embed URL
);

CREATE TABLE IF NOT EXISTS slides (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id  INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL,
    kicker      TEXT,
    heading     TEXT,
    sub         TEXT,
    bullets     TEXT,                        -- JSON array of strings
    note        TEXT
);

CREATE TABLE IF NOT EXISTS questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id     INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    level          TEXT NOT NULL CHECK (level IN ('E', 'M', 'H')),
    position       INTEGER NOT NULL,
    stem           TEXT NOT NULL,
    options        TEXT NOT NULL,            -- JSON array of 4 strings
    correct_index  INTEGER NOT NULL,
    explanation    TEXT
);

CREATE INDEX IF NOT EXISTS idx_slides_chapter ON slides(chapter_id);
CREATE INDEX IF NOT EXISTS idx_questions_chapter_level ON questions(chapter_id, level);
