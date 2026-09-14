---
name: canvas-weekly-bilingual-study
description: Collect and organize published Canvas materials and lecture transcripts, then build detailed weekly HTML study guides in Chinese, English or both, grounded in slides and what the lecturer actually said. Use for Canvas downloads, weekly lecture notes, or refreshing a study archive.
---

# Canvas Weekly Bilingual Study

Create an organized source archive and one substantial HTML guide per **teaching week, per course**, using the host agent's available browser, file and reasoning tools. No particular model vendor is required.

## Modes

- **Collect and study** (default for end-to-end requests): collect, map weeks, write and verify guides.
- **Collect only**: download/classify and report verified coverage.
- **Study existing files**: use supplied/local slides and transcripts without requiring Canvas access.
- **Refresh**: discover newly published/changed resources and regenerate affected guides, retaining previous sources. Weekly organization does not imply recurring scheduling.

Infer selected courses, semester and destination from the request/context. Ask only when missing information materially changes the result. Never hard-code a university, course ID, student, path, lecture count or semester calendar.

Choose `output_language` from the user's requested **guide language**: `zh` (Chinese only), `en` (English only), or `both` (full Chinese–English). Default to `both` when unspecified; a prompt written in Chinese does not override an explicit request for English output. Preserve the selected mode when refreshing existing guides unless the user changes it. In single-language mode, author only the selected language, including titles, explanations, examples, answers, captions and interface labels. Do not require or generate an unused translation. Collection scope, teaching depth, source coverage and lecturer additions are identical in all three modes.

## 1. Collect

Read [collection.md](references/collection.md). Prefer an existing authorized connector or logged-in browser. `scripts/canvas_sync.py` is an optional read-only API route **only with an already-configured token**. Never extract browser credentials or create a token implicitly.

Inventory Modules, Home/course pages, accessible Files and relevant external teaching links. Offline Canvas export is efficient when available but may omit Ed workshops and Lecture Capture. Collect questions, published official solutions, datasets, code, slides and notes. Enter every available lecture and download its original TXT transcript. When explaining this workflow to a student, introduce a transcript as the written text of the lecture recording (课堂文字稿), which can preserve spoken material absent from the slides. Video binaries are only needed if requested.

Record each download's course, stable resource ID/URL, lecture date/title, role, size and SHA-256. Verify completed files, not button clicks. Record gaps as `not_published`, `not_generated`, `access_denied`, `download_failed` or `mapping_unresolved`. Keep question workspaces with their dependent data; distinguish a student's current Challenge from an official Solution.

Use `scripts/study_files.py` for safe ZIP extraction, draft classification and text extraction. Suggested layout:

```text
Study Archive/<course>/
  Lecture Materials/       Tutorial Questions/       Tutorial Solutions/
  Tutorial Files/          Lecture Transcripts/      Original Exports/
  metadata/manifest.json   metadata/week-map.json    extracted/
  Weekly Guides/week-01.html ...                     index.html
```

## 2. Map teaching weeks

Read [weekly-authoring.md](references/weekly-authoring.md). Reconcile the actual timetable, module labels, lecture dates and topics. Account for holidays. Tutorial weeks may lag lectures. A module PDF can span several weeks; map actual page ranges. Never pair ambiguous transcripts solely by download order or truncated filenames.

For each week, inventory **every lecture**, all assigned slide pages and the complete transcript. Preserve page/slide numbers, real timestamps and stable transcript line numbers. Plain TXT may have no timestamps: cite real line ranges instead of inventing times. Visually inspect scanned pages, diagrams and equations. Empty/poor text extraction requires OCR or visual reading, not omission.

## 3. Teach in the selected language, beyond the slides

Build a source coverage matrix before drafting and a professor-additions ledger while reading **all** assigned transcript chunks. Process long weeks in bounded chunks without dropping the remainder.

Every learner-facing knowledge unit needs a full explanation in the selected language(s): definitions, intuition, notation, assumptions, derivations, examples, figure/table explanations, code explanations, pitfalls, questions, answers and recaps. In `both` mode, Chinese and English must be substantively equivalent; neither can be a shortened summary of the other. Preserve official technical terminology and executable identifiers; explain code without breaking it.

For each substantive concept, teach what it means, why/how it works, when it applies, and a worked example or useful contrast. Add reasoning and scaffolding, not padded bullets. Cover all substantive slide topics and integrate lecturer-only examples, corrections and emphasis beside the relevant concepts.

Label provenance accurately: **Slide content / 讲义内容**, **Lecturer addition / 教授补充**, **Teaching expansion / 教学补充**, **Uncertain transcript / 转录待核对**. Lecturer additions require actual transcript evidence. Never attribute model elaboration to the professor. Remove filler and irrelevant chatter; preserve meaningful teaching corrections and consequential course guidance.

Create `week-NN.json` using [html-contract.md](references/html-contract.md), then:

```bash
python scripts/render_week.py validate path/to/week-NN.json
python scripts/render_week.py render path/to/week-NN.json --out path/to/week-NN.html
```

The renderer creates one offline HTML with search, navigation, source links and print styling. Bilingual guides include a display-language switch; single-language guides contain only the selected text and no switch to an absent translation. **The host AI writes the explanations**; the script does not generate them or prove semantic completeness. Use readable Unicode/plain formulas or embedded rendered figures; do not leave unreadable raw LaTeX as the only representation.

Write like a careful tutor: connected explanations, concrete examples, readable code and restrained page styling. Avoid slogan headings, repetitive recap boxes, decorative gradients, emoji-heavy pages and padded generic introductions.

## 4. Verify and deliver

- Reconcile expected/downloaded resources and lecture-week mappings; show missing items.
- Compare coverage against original pages and the transcript additions ledger. Every substantive unit maps to a section in the selected language(s) or an explicit reason for exclusion.
- Check notation, calculations, worked steps, code explanations and professor attributions; also check language equivalence in `both` mode. Do not execute downloaded course/student code just to read it.
- Validate the selected language, required text fields, citations, offline assets and local links. Do not mark partial coverage complete.
- Open representative HTML with the available permitted browser tool on desktop and narrow screen; exercise search, worked-answer disclosure and language controls when present.
- Deliver an index, course/week links and concise coverage report. Student course materials, transcripts and credentials stay in the student's archive, **never in a publicly shared skill package or website**.

For original Finance and Coding demonstrations, open [the example index](examples/index.html). Finance examples use timelines, assumptions and worked calculations; Coding examples explain state changes and executable identifiers. Adapt to the actual course rather than imposing either subject on unrelated materials.

For compatibility and example prompts read [getting-started.md](references/getting-started.md). Load references only as needed.
