import sqlite3

DB = "app/src/main/assets/data/quran.db"
SRC = "quran-uthmani.txt"

con = sqlite3.connect(DB)
con.execute("PRAGMA foreign_keys = ON")

rows = []
global_number = 1

with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split("|", 2)

        if len(parts) != 3:
            raise ValueError(f"Invalid line: {line}")

        surah, ayah, text = parts
        surah = int(surah)
        ayah = int(ayah)

        rows.append((surah, ayah, global_number, text))
        global_number += 1

if len(rows) != 6236:
    raise ValueError(f"Expected 6236 ayahs, got {len(rows)}")

if [r[2] for r in rows] != list(range(1, 6237)):
    raise ValueError("Invalid global numbering")

con.execute("DELETE FROM ayahs")
con.execute("DELETE FROM surahs")

for number in range(1, 115):
    count = sum(r[0] == number for r in rows)

    con.execute(
        """
        INSERT INTO surahs
        (number, name_ar, name_fa, ayah_count)
        VALUES (?, ?, ?, ?)
        """,
        (number, f"سوره {number}", None, count)
    )

surah_ids = {
    row[0]: row[1]
    for row in con.execute("SELECT number, id FROM surahs").fetchall()
}

if len(surah_ids) != 114:
    raise ValueError(f"Expected 114 surahs, got {len(surah_ids)}")

if 1 not in surah_ids or 114 not in surah_ids:
    raise ValueError("Surah ID mapping is incomplete")

ayah_rows = [
    (surah_ids[surah], ayah, global_number, text)
    for surah, ayah, global_number, text in rows
]

con.executemany(
    """
    INSERT INTO ayahs
    (surah_id, ayah_number, global_number, text_ar)
    VALUES (?, ?, ?, ?)
    """,
    ayah_rows
)

con.execute(
    "UPDATE database_info SET value=? WHERE key='data_status'",
    ("imported",)
)

con.execute(
    "UPDATE database_info SET value=? WHERE key='quran_text_source'",
    ("Tanzil Uthmani 1.1",)
)

con.commit()

print("Quran imported successfully.")
print("Surahs:", con.execute("SELECT COUNT(*) FROM surahs").fetchone()[0])
print("Ayahs:", con.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0])
print(
    "Global range:",
    con.execute(
        "SELECT MIN(global_number), MAX(global_number) FROM ayahs"
    ).fetchone()
)

con.close()
