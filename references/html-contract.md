# Weekly guide contract (schema v1, renderer 1.1+)

The host agent authors JSON after reading sources. `scripts/render_week.py` validates declared coverage and renders it; it does not call a model or prove correctness. See the original Coding example at `examples/week-01.json` and Finance example at `examples/finance/week-01.json`; open `examples/index.html` for both.

Set `output_language` to `"zh"`, `"en"` or `"both"`. Omission defaults to `"both"`, so existing v1 guides still work. Every **localized** value follows the selected mode:

| Output mode | Required authored value |
| --- | --- |
| `en` — English only | `{"en": "Full English explanation"}` |
| `zh` — 中文 | `{"zh": "中文完整讲解"}` |
| `both` — 中英双语 (default) | `{"zh": "中文完整讲解", "en": "Full English explanation"}` |

Unused language keys may be omitted. If present in a single-language export, they are not rendered. The host AI should author only the requested language(s), with equal teaching depth and source coverage in every mode. Use ordinary text with paragraph breaks. Code and formulas may be shared; each requested explanation must be complete. HTML text is escaped. Use readable Unicode formulas; supply rendered PNG/JPEG/WebP figures when needed.

Required top-level fields:

- `output_language: "both" | "zh" | "en"` (optional; default `"both"`).
- `schema_version: 1`, `course` (localized), `title` (localized), `week` (positive teaching-week integer).
- `status: "partial" | "complete"`, `reviewed` (boolean), `missing` (list of localized gap descriptions; empty if none).
- `sources`: list of `{id, kind, title, path, units}`. IDs are unique lowercase slugs. `kind` is slides/transcript/tutorial/solution/other. `title` is localized. `path` is a relative local path from the JSON file. `units` contains all assigned pages/slides/transcript chunks, using actual locators such as `page 3`, `lines 42–90`. Sources must exist when rendering. Keep the archive layout intact when moving a guide.
- `lectures`: list of `{date: "YYYY-MM-DD", title: localized, sources: [source IDs]}` for every lecture in the week.
- `goals`: nonempty list of localized learning goals.
- `sections`: nonempty list of `{id, title: localized, blocks}`. Section IDs are unique lowercase slugs.
- `coverage`: one entry for every `(source, locator)` declared under sources. Use `{source, locator, section}` for taught material; that section must cite the same unit. Otherwise use `{source, locator, disposition: "excluded" | "unresolved", reason: localized}`. Legitimate exclusion includes repeated content or irrelevant housekeeping; never exclude a substantive topic for lack of time.
- Optional `glossary`: list of `{term: localized, definition: localized}`.

Each block has `kind: "slide" | "lecturer_addition" | "teaching_expansion" | "uncertain"`, `text` (localized), and `citations: [{source, locator}]`. Citations must use inventoried locators. Source-derived blocks require citations; lecturer additions require at least one actual transcript citation. Teaching expansion is the model's explanation, not something falsely attributed to the teacher.

Optional block fields:

- `title`: localized subheading.
- `code`: shared literal source code or readable formula.
- `answer`: localized worked answer revealed by a disclosure control; the block text supplies the question.
- `table: {headers: [localized values], rows: [[localized values]]}` with consistent column counts.
- `image: {path, caption: localized}`. PNG/JPEG/WebP must live alongside or below the JSON file and be at most 20 MiB. The renderer embeds it for offline use. Caption also provides alt text in the selected language(s).

`complete` requires `reviewed: true`, no missing sources, no unresolved units and no uncertain blocks. Review each selected language explanation, each worked example, the original slide coverage, and the full transcript/additions ledger before setting it. A false inventory can still pass structural validation; the author must reconcile it to originals.

Render example:

```bash
python scripts/render_week.py validate examples/week-01.json
python scripts/render_week.py render examples/week-01.json --out examples/week-01.html
```

To export only existing English text from a bilingual JSON file, use:

```bash
python scripts/render_week.py render examples/week-01.json --language en --out week-01-en.html
```

`--language` overrides the JSON mode for this command only; it selects authored text and never translates or invents a missing language. Validation fails if any required selected-language field is absent. Single-language HTML localizes its page title, navigation, provenance labels, answer controls, captions/alt text and notices, without emitting the other language's content or a language switch. Bilingual HTML includes all three display options.

The HTML is self-contained for reading. Source links point to the accompanying private archive and need those source files to remain available. Publishing the generic skill does not authorize publishing anyone's course materials or derived guides.
