import sqlite3
import xml.etree.ElementTree as ET

DB = "app/src/main/assets/data/quran.db"
XML = "quran-data.xml"

tree = ET.parse(XML)
root = tree.getroot()
suras = root.find("./suras")

if suras is None or len(suras) != 114:
    raise ValueError("Expected exactly 114 surahs")

data = []

for s in suras:
    number = int(s.attrib["index"])
    ayas = int(s.attrib["ayas"])
    name_ar = s.attrib["name"]
    tname = s.attrib["tname"]
    name_en = s.attrib["ename"]
    revelation_type = s.attrib["type"]
    order = int(s.attrib["order"])
    rukus = int(s.attrib["rukus"])

    data.append(
        (
            number,
            name_ar,
            name_en,
            tname,
            revelation_type,
            order,
            rukus,
            ayas,
        )
    )

con = sqlite3.connect(DB)

db_counts = dict(
    con.execute(
        """
        SELECT s.number, COUNT(a.id)
        FROM surahs s
        LEFT JOIN ayahs a ON a.surah_id = s.id
        GROUP BY s.number
        """
    ).fetchall()
)

for row in data:
    number = row[0]
    expected = row[7]
    actual = db_counts.get(number, 0)

    if expected != actual:
        raise ValueError(
            f"Surah {number}: Tanzil={expected}, database={actual}"
        )

con.executemany(
    """
    UPDATE surahs
    SET name_ar=?,
        name_en=?,
        tname=?,
        revelation_type=?,
        revelation_order=?,
        rukus_count=?,
        ayah_count=?
    WHERE number=?
    """,
    [
        (
            name_ar,
            name_en,
            tname,
            revelation_type,
            order,
            rukus,
            ayas,
            number,
        )
        for number, name_ar, name_en, tname,
        revelation_type, order, rukus, ayas in data
    ],
)

con.commit()

print("Metadata imported successfully.")
print("Surahs:", con.execute("SELECT COUNT(*) FROM surahs").fetchone()[0])
print("Meccan:", con.execute(
    "SELECT COUNT(*) FROM surahs WHERE revelation_type='Meccan'"
).fetchone()[0])
print("Medinan:", con.execute(
    "SELECT COUNT(*) FROM surahs WHERE revelation_type='Medinan'"
).fetchone()[0])

con.close()
