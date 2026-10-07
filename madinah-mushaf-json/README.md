# quran-pages

Static JSON dataset for rendering a **604-page Madinah mushaf** (Hafs ‘an ‘Asim), with **word-level** addressing suitable for readers, finders, and word annotations.

**Author:** [odihamd](https://github.com/ouryhamdalaye)

Derived from [zonetecde/mushaf-layout](https://github.com/zonetecde/mushaf-layout) (page layout) and [risan/quran-json](https://github.com/risan/quran-json) (surah metadata), then reshaped into the schema below. This tree is a **canonical snapshot** — there is no regeneration pipeline. Treat `word_index` values as stable identifiers.

## Layout

```
pages/
  meta.json              # 114 surahs (names, counts, start page)
  verse-to-page.json     # first verse of each page (index = page − 1)
  page-001.json … page-604.json
  notes.md               # short provenance note
```

Serve `pages/` as static assets (CDN, `public/`, object storage, etc.). Load pages on demand (e.g. current page ± a small window).

## `meta.json`

Array of 114 surah objects:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | number | Surah number `1…114` |
| `name` | string | Arabic name |
| `transliteration` | string | Latin transliteration |
| `translation` | string | French short title |
| `type` | `"meccan"` \| `"medinan"` | Revelation place |
| `total_verses` | number | Verse count |
| `start_page` | number | Mushaf page where the surah begins (`1…604`) |

Use for surah pickers and to bound verse selects (`1…total_verses`).

## `page-XXX.json`

One file per page. Zero-padded names: `page-001.json` … `page-604.json`.

```json
{
  "page": 1,
  "verses": [ /* content */ ],
  "lines": [ /* visual layout */ ]
}
```

### `verses` — content dictionary

Each entry is a full ayah that appears on this page (even if the ayah continues on the next page, only the words present on *this* page are listed):

```json
{
  "surah_number": 1,
  "ayah_number": 1,
  "words": [
    { "word_index": 0, "text": "بِسْمِ" },
    { "word_index": 1, "text": "ٱللَّهِ" }
  ]
}
```

- `word_index` is **0-based within the ayah**, and is the stable key for annotations: `(surah_number, ayah_number, word_index)`.
- `text` is Uthmani orthography (including diacritics / pause marks where present).
- Resolve display text with `verses` + a token `(s, a, w)` from `lines`.

### `lines` — Madinah line layout

Ordered top → bottom. Two line kinds:

**Surah title**

```json
{ "type": "surah-header", "text": "سُورَةُ ٱلْفَاتِحَةِ" }
```

**Text line** — tokens point into `verses` (`s` = surah, `a` = ayah, `w` = `word_index`):

```json
{
  "type": "ayah-line",
  "tokens": [
    { "s": 1, "a": 1, "w": 0 },
    { "s": 1, "a": 1, "w": 1 },
    { "s": 1, "a": 1, "w": 2 },
    { "s": 1, "a": 1, "w": 3 }
  ]
}
```

A single visual line may mix several ayahs (e.g. end of ayah 3 + start of ayah 4 on page 1). Prefer rendering from `lines` when present so pagination matches the printed mushaf; fall back to concatenating `verses` only if you do not need faithful line breaks.

### Minimal render sketch

```js
function wordText(page, { s, a, w }) {
  const verse = page.verses.find(
    (v) => v.surah_number === s && v.ayah_number === a
  );
  return verse.words.find((word) => word.word_index === w).text;
}

for (const line of page.lines) {
  if (line.type === "surah-header") {
    // render title
  } else {
    const texts = line.tokens.map((t) => wordText(page, t));
    // render RTL line of words; optionally show ayah number after the last word of an ayah
  }
}
```

Use an Arabic mushaf font (e.g. Amiri Quran), `dir="rtl"`, and treat each word as its own inline element so shaping and click/tap targets stay correct.

## `verse-to-page.json`

Array of length **604**. Index `i` is page `i + 1`. Each entry is the **first** `(surah, ayah)` that starts on that page:

```json
[
  { "surah": 1, "ayah": 1 },
  { "surah": 2, "ayah": 1 },
  { "surah": 2, "ayah": 6 }
]
```

To jump to the page containing verse `(surah, ayah)`, find the **largest** page whose first verse is ≤ the target (surah/ayah order). Combined with `meta.json`, this powers a surah → ayah → page finder.

## Stability warning

If you store user data keyed by `word_index` (highlights, tajweed marks, mistakes, etc.), **do not re-segment words** in these files without a migration. Changing tokenization silently invalidates historical references.

Corrections that keep the same `(surah, ayah, word_index)` → text mapping are fine; renumbering or splitting words is not.

## Suggested integration

1. Ship or fetch `meta.json` + `verse-to-page.json` at startup.
2. Lazy-load `page-NNN.json` around the current page.
3. Render with `lines` + word lookup from `verses`.
4. Optionally annotate by attaching UI state to `(s, a, w)`.

## License

This dataset is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — see [`LICENSE`](./LICENSE).

You must give attribution and share adaptations under the same licence. The Quranic text itself is not copyrighted; packaging, layout data, and translations may be.

## Sources

- Layout heritage: [zonetecde/mushaf-layout](https://github.com/zonetecde/mushaf-layout) (no licence declared upstream — verify before commercial redistribution)
- Surah metadata heritage: [risan/quran-json](https://github.com/risan/quran-json) (CC BY-SA 4.0)

This repository’s JSON structure is a derivative rework, not a verbatim upstream dump. Also check any font you pair with the text.

## Scope

- Included: 604 Madinah pages, French surah titles in `meta.json`, word + line layout.
- Not included: audio, translations of ayahs, fonts, or a renderer — bring your own UI.
