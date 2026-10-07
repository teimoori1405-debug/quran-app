import json
from pathlib import Path

BASE = Path("madinah-mushaf-json/pages")

page_files = sorted(BASE.glob("page-*.json"))

print("Page files:", len(page_files))

if len(page_files) != 604:
    raise ValueError(f"Expected 604 page files, got {len(page_files)}")

pages = set()
verse_pages = {}

for path in page_files:
    number = int(path.stem.split("-")[1])
    pages.add(number)

    if number < 1 or number > 604:
        raise ValueError(f"Invalid page number: {number}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("page") != number:
        raise ValueError(
            f"Page mismatch: file={path.name}, json={data.get('page')}"
        )

    if not isinstance(data.get("verses"), list):
        raise ValueError(f"Invalid verses list: {path.name}")

    for verse in data["verses"]:
        surah = verse["surah_number"]
        ayah = verse["ayah_number"]

        if not (1 <= surah <= 114):
            raise ValueError(f"Invalid surah: {surah} in {path.name}")

        if ayah < 1:
            raise ValueError(f"Invalid ayah: {surah}:{ayah}")

        key = (surah, ayah)
        verse_pages.setdefault(key, set()).add(number)

if pages != set(range(1, 605)):
    missing = sorted(set(range(1, 605)) - pages)
    extra = sorted(pages - set(range(1, 605)))
    raise ValueError(
        f"Page range invalid. Missing={missing}, extra={extra}"
    )

print("Pages validated:", len(pages))
print("Unique ayahs referenced:", len(verse_pages))
print(
    "Unique ayah/page references:",
    sum(len(v) for v in verse_pages.values())
)

expected = 6236

if len(verse_pages) != expected:
    print(
        f"WARNING: expected {expected} unique ayahs, "
        f"got {len(verse_pages)}"
    )

multi_page = {
    key: sorted(value)
    for key, value in verse_pages.items()
    if len(value) > 1
}

print("Ayahs spanning multiple pages:", len(multi_page))
print("First ayah:", min(verse_pages))
print("Last ayah:", max(verse_pages))

with open("mushaf_validation.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "pages": len(pages),
            "unique_ayahs": len(verse_pages),
            "ayah_page_references": sum(len(v) for v in verse_pages.values()),
            "multi_page_ayahs": len(multi_page),
        },
        f,
        ensure_ascii=False,
        indent=2,
    )

print("Validation report: mushaf_validation.json")
print("OK")
