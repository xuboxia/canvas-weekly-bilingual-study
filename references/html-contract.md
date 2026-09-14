# Weekly guide contract (v1)

The host agent authors JSON after reading sources. `scripts/render_week.py` validates declared coverage and renders it; it does not call a model or prove correctness. See the working synthetic example at `examples/week-01.json`.

All bilingual values have the shape `{"zh": "中文全文", "en": "Full English explanation"}`. Use ordinary text with paragraph breaks. Code and formulas may be shared; explanations must be complete in both languages. HTML text is escaped. Use readable Unicode formulas; supply rendered PNG/JPEG/WebP figures when needed.

Required top-level fields:

- `schema_version: 1`, `course` (bilingual), `title` (bilingual), `week` (positive teaching-week integer).
- `status: "partial" | "complete"`, `reviewed` (boolean), `missing` (list of bilingual gap descriptions; empty if none).
- `sources`: list of `{id, kind, title, path, units}`. IDs are unique lowercase slugs. `kind` is slides/transcript/tutorial/solution/other. `title` is bilingual. `path` is a relative local path from the JSON file. `units` contains all assigned pages/slides/transcript chunks, using actual locators such as `page 3`, `lines 42–90`. Sources must exist when rendering. Keep the archive layout intact when moving a guide.
- `lectures`: list of `{date: "YYYY-MM-DD", title: bilingual, sources: [source IDs]}` for every lecture in the week.
- `goals`: nonempty list of bilingual learning goals.
- `sections`: nonempty list of `{id, title: bilingual, blocks}`. Section IDs are unique lowercase slugs.
- `coverage`: one entry for every `(source, locator)` declared under sources. Use `{source, locator, section}` for taught material; that section must cite the same unit. Otherwise use `{source, locator, disposition: "excluded" | "unresolved", reason: bilingual}`. Legitimate exclusion includes repeated content or irrelevant housekeeping; never exclude a substantive topic for lack of time.
- Optional `glossary`: list of `{term: bilingual, definition: bilingual}`.

Each block has `kind: "slide" | "lecturer_addition" | "teaching_expansion" | "uncertain"`, `text` (bilingual), and `citations: [{source, locator}]`. Citations must use inventoried locators. Source-derived blocks require citations; lecturer additions require at least one actual transcript citation. Teaching expansion is the model's explanation, not something falsely attributed to the teacher.

Optional block fields:

- `title`: bilingual subheading.
- `code`: shared literal source code or readable formula.
- `answer`: bilingual worked answer revealed by a disclosure control; the block text supplies the question.
- `table: {headers: [bilingual values], rows: [[bilingual values]]}` with consistent column counts.
- `image: {path, caption: bilingual}`. PNG/JPEG/WebP must live alongside or below the JSON file and be at most 20 MiB. The renderer embeds it for offline use. Caption also provides bilingual alt text.

`complete` requires `reviewed: true`, no missing sources, no unresolved units and no uncertain blocks. Review both language explanations, each worked example, the original slide coverage, and the full transcript/additions ledger before setting it. A false inventory can still pass structural validation; the author must reconcile it to originals.

Render example:

```bash
python scripts/render_week.py validate examples/week-01.json
python scripts/render_week.py render examples/week-01.json --out examples/week-01.html
```

The HTML is self-contained for reading. Source links point to the accompanying private archive and need those source files to remain available. Publishing the generic skill does not authorize publishing anyone's course materials or derived guides.
