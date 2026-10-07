import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path.home() / "quran-app"
DB = BASE / "app/src/main/assets/data/quran.db"
SRC = BASE / "madinah-mushaf-json/pages"

print("=== MUSHAF MIGRATION + IMPORT + VALIDATION ===")

if not DB.exists():
    raise SystemExit("ERROR: database not found")

if not SRC.exists():
    raise SystemExit("ERROR: mushaf source not found")

BACKUP = DB.with_name(
    "quran-backup-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".db"
)

shutil.copy2(DB, BACKUP)
print("Backup:", BACKUP)

pages = sorted(SRC.glob("page-*.json"))

if len(pages) != 604:
    raise SystemExit(
        "ERROR: expected 604 pages, found " + str(len(pages))
    )

print("Source pages:", len(pages))

source_refs = []
seen = set()

for path in pages:
    data = json.loads(path.read_text(encoding="utf-8"))
    page_no = data["page"]

    for verse in data["verses"]:
        key = (
            verse["surah_number"],
            verse["ayah_number"]
        )

        if key in seen:
            raise SystemExit(
                "ERROR: duplicate ayah " + str(key)
            )

        seen.add(key)
        source_refs.append(
            (page_no, key[0], key[1])
        )

if len(source_refs) != 6236:
    raise SystemExit(
        "ERROR: expected 6236 source ayahs, found "
        + str(len(source_refs))
    )

print("Source ayahs:", len(source_refs))

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

db_count = cur.execute(
    "SELECT COUNT(*) FROM ayahs"
).fetchone()[0]

print("Database ayahs:", db_count)

if db_count != 6236:
    conn.close()
    raise SystemExit(
        "ERROR: expected 6236 database ayahs, found "
        + str(db_count)
    )

db_refs = set(
    cur.execute(
        "SELECT s.number, a.ayah_number "
        "FROM ayahs a JOIN surahs s "
        "ON s.id = a.surah_id"
    ).fetchall()
)

src_refs = set(
    (surah, ayah)
    for page, surah, ayah in source_refs
)

if db_refs != src_refs:
    conn.close()
    raise SystemExit("ERROR: database/source ayah mismatch")

cur.execute("""
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY,
    page_number INTEGER UNIQUE NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ayah_pages (
    ayah_id INTEGER NOT NULL,
    page_id INTEGER NOT NULL,
    PRIMARY KEY (ayah_id, page_id),
    FOREIGN KEY (ayah_id) REFERENCES ayahs(id),
    FOREIGN KEY (page_id) REFERENCES pages(id)
)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_ayah_pages_ayah
ON ayah_pages(ayah_id)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_ayah_pages_page
ON ayah_pages(page_id)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS database_info (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

print("Database schema: OK")

cur.execute("DELETE FROM ayah_pages")
cur.execute("DELETE FROM pages")

for page_no in range(1, 605):
    cur.execute(
        "INSERT INTO pages(page_number) VALUES (?)",
        (page_no,)
    )

page_ids = {}

for row in cur.execute(
    "SELECT id, page_number FROM pages"
):
    page_ids[row[1]] = row[0]

for page_no, surah_no, ayah_no in source_refs:

    row = cur.execute(
        """
        SELECT a.id
        FROM ayahs a
        JOIN surahs s ON s.id = a.surah_id
        WHERE s.number = ?
          AND a.ayah_number = ?
        """,
        (surah_no, ayah_no)
    ).fetchone()

    if row is None:
        conn.rollback()
        conn.close()
        raise SystemExit(
            "ERROR: missing ayah "
            + str(surah_no) + ":" + str(ayah_no)
        )

    cur.execute(
        """
        INSERT INTO ayah_pages(ayah_id, page_id)
        VALUES (?, ?)
        """,
        (row[0], page_ids[page_no])
    )

print("Import completed:", len(source_refs), "relations")

cur.execute(
    "INSERT OR REPLACE INTO database_info(key,value) "
    "VALUES(?,?)",
    ("page_layout", "Madinah Mushaf - 604 pages")
)

cur.execute(
    "INSERT OR REPLACE INTO database_info(key,value) "
    "VALUES(?,?)",
    ("page_layout_source", "ouryhamdalaye/madinah-mushaf-json")
)

cur.execute(
    "INSERT OR REPLACE INTO database_info(key,value) "
    "VALUES(?,?)",
    ("page_layout_license", "CC BY-SA 4.0")
)

cur.execute(
    "INSERT OR REPLACE INTO database_info(key,value) "
    "VALUES(?,?)",
    ("page_layout_data_status", "imported")
)

page_count = cur.execute(
    "SELECT COUNT(*) FROM pages"
).fetchone()[0]

relation_count = cur.execute(
    "SELECT COUNT(*) FROM ayah_pages"
).fetchone()[0]

mapped_ayahs = cur.execute(
    "SELECT COUNT(DISTINCT ayah_id) FROM ayah_pages"
).fetchone()[0]

mapped_pages = cur.execute(
    "SELECT COUNT(DISTINCT page_id) FROM ayah_pages"
).fetchone()[0]

fk_errors = cur.execute(
    "PRAGMA foreign_key_check"
).fetchall()

duplicate_relations = cur.execute(
    """
    SELECT ayah_id, page_id, COUNT(*)
    FROM ayah_pages
    GROUP BY ayah_id, page_id
    HAVING COUNT(*) > 1
    """
).fetchall()

bad_ayahs = cur.execute(
    """
    SELECT COUNT(*)
    FROM (
        SELECT id
        FROM ayahs
        WHERE id NOT IN (
            SELECT ayah_id FROM ayah_pages
        )
    )
    """
).fetchone()[0]

print()
print("=== RESULT ===")
print("Pages imported:", page_count)
print("Ayah/page relations:", relation_count)
print("Ayahs mapped:", mapped_ayahs)
print("Pages mapped:", mapped_pages)
print("Foreign key errors:", len(fk_errors))
print("Duplicate relations:", len(duplicate_relations))
print("Ayahs without page:", bad_ayahs)

if page_count != 604:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - page count")

if relation_count != 6236:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - relation count")

if mapped_ayahs != 6236:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - ayah mapping")

if mapped_pages != 604:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - page mapping")

if fk_errors:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - foreign keys")

if duplicate_relations:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - duplicates")

if bad_ayahs:
    conn.rollback()
    conn.close()
    raise SystemExit("FINAL RESULT: FAIL - unmapped ayahs")

conn.commit()
conn.close()

print()
print("FINAL RESULT: PASS")
print("Backup preserved:", BACKUP)
