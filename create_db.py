import sqlite3
from pathlib import Path

db = Path("app/src/main/assets/data/quran.db")
db.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(db)
con.execute("PRAGMA foreign_keys = ON")

con.executescript("""
CREATE TABLE surahs (
    id INTEGER PRIMARY KEY,
    number INTEGER NOT NULL UNIQUE,
    name_ar TEXT NOT NULL,
    name_fa TEXT,
    ayah_count INTEGER NOT NULL,
    revelation_order INTEGER
);

CREATE TABLE ayahs (
    id INTEGER PRIMARY KEY,
    surah_id INTEGER NOT NULL,
    ayah_number INTEGER NOT NULL,
    global_number INTEGER NOT NULL UNIQUE,
    text_ar TEXT NOT NULL,
    UNIQUE(surah_id, ayah_number),
    FOREIGN KEY(surah_id) REFERENCES surahs(id)
);

CREATE TABLE translations (
    id INTEGER PRIMARY KEY,
    language TEXT NOT NULL,
    name TEXT NOT NULL,
    translator TEXT,
    version TEXT
);

CREATE TABLE ayah_translations (
    id INTEGER PRIMARY KEY,
    ayah_id INTEGER NOT NULL,
    translation_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    UNIQUE(ayah_id, translation_id),
    FOREIGN KEY(ayah_id) REFERENCES ayahs(id),
    FOREIGN KEY(translation_id) REFERENCES translations(id)
);

CREATE TABLE pages (
    id INTEGER PRIMARY KEY,
    page_number INTEGER NOT NULL UNIQUE
        CHECK(page_number BETWEEN 1 AND 604)
);

CREATE TABLE ayah_pages (
    ayah_id INTEGER NOT NULL,
    page_id INTEGER NOT NULL,
    PRIMARY KEY(ayah_id, page_id),
    FOREIGN KEY(ayah_id) REFERENCES ayahs(id),
    FOREIGN KEY(page_id) REFERENCES pages(id)
);

CREATE TABLE database_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX idx_ayahs_surah
ON ayahs(surah_id);

CREATE INDEX idx_ayah_translations_ayah
ON ayah_translations(ayah_id);

CREATE INDEX idx_ayah_pages_page
ON ayah_pages(page_id);
""")

con.executemany(
    "INSERT INTO pages(page_number) VALUES (?)",
    [(n,) for n in range(1, 605)]
)

con.executemany(
    "INSERT INTO database_info(key, value) VALUES (?, ?)",
    [
        ("schema_version", "2"),
        ("quran_text_source", "Tanzil - pending import"),
        ("page_layout", "Madinah Mushaf - 604 pages"),
        ("data_status", "schema_only")
    ]
)

con.commit()
con.close()
print("Database schema v2 created; 604 empty page records added.")
