"""Reads the chapter -> PPT link mapping out of sat-math.xlsx and writes it into
the chapters table, matching rows to chapters by their leading chapter number
(e.g. "01 - Math Strategies" in the sheet matches chapter code "c01").
"""
import re

import openpyxl

SLIDES_ID_RE = re.compile(r"/presentation/d/([a-zA-Z0-9_-]+)")
LEADING_NUM_RE = re.compile(r"^\s*(\d+)")


def to_embed_url(share_link):
    """Turns a Google Slides share/edit link into an embeddable URL."""
    if not share_link:
        return None
    m = SLIDES_ID_RE.search(str(share_link))
    if not m:
        return None
    return f"https://docs.google.com/presentation/d/{m.group(1)}/embed?start=false&loop=false&delayms=3000"


def read_ppt_links(xlsx_path):
    """Returns {chapter_number_zero_padded: (raw_link, embed_url)} from the sheet."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.worksheets[0]
    links = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        chapter_label = row[0]
        link = row[1] if len(row) > 1 else None
        m = LEADING_NUM_RE.match(str(chapter_label))
        if not m:
            continue
        num = m.group(1).zfill(2)
        links[num] = (link, to_embed_url(link))
    return links


def sync_ppt_links(conn, xlsx_path):
    """Updates chapters.ppt_link / ppt_embed_url from the workbook. Returns the count updated."""
    links = read_ppt_links(xlsx_path)
    cur = conn.cursor()
    updated = 0
    for num, (raw_link, embed_url) in links.items():
        code = f"c{num}"
        cur.execute(
            "UPDATE chapters SET ppt_link = ?, ppt_embed_url = ? WHERE code = ?",
            (raw_link, embed_url, code),
        )
        updated += cur.rowcount
    conn.commit()
    return updated
