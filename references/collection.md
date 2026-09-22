# Collection and recovery

## Browser route

Use the host's permitted browser/computer tool. Inspect live tabs and select the actual school account: an extension may expose a different profile from the native foreground window. Re-read UI state after actions and never reuse stale element indices.

1. Inventory requested courses/semester from Modules, Home and accessible Files. Inline course-page explanations also count as sources. Check Final, Exam Preparation, Sample/Mock Exam and Past Papers pages explicitly, including links inside pages and assignment descriptions. Collect published Final papers, official solutions, formula sheets and exam instructions. Record not-found, not-published and download-failed separately. Do not start a quiz or attempt to reveal a locked answer. MST/midterm collection is opt-in.
2. If offered, start **Export Subject Content** and work in other course tabs while it processes. Some exports download automatically. Check the finished ZIP's course-data and attachments against the inventory; preserve the original ZIP.
3. If export is unavailable, use file-preview downloads. Native browser Escape can cancel an in-flight download: wait for completion or use the preview's Close control. A success requires a completed local file, not a click.
4. Follow relevant course-linked platforms. Dropbox shared-folder Download may collect all slides. In Ed enumerate every slide/challenge within each weekly lesson, not just the last visited one. File-tree **Download All** can preserve notebook/data/image dependencies. Explicitly check Challenge vs Solution mode/URL: changing slides may preserve Solution mode. Never reset, edit, run or submit a student's workspace. Keep official solutions distinguishable beside their questions inside the same tutorial folder.
5. In Lecture Capture/Echo360 enumerate completed recordings separately from future scheduled sessions. Open each recording → Transcripts panel → download transcripts → **Plain Text Format File**. Record the lecture ID/date/title before downloading; filenames may collide/truncate. Download time is not lecture date. Serialize ambiguous same-named downloads or isolate destinations, and register each completed file promptly.
6. If transcripts have no timestamps, preserve text and later cite actual line numbers. Record unavailable transcripts and continue other lectures.

Use a few independently loading tabs to overlap network work without losing the download-to-source mapping. Keep a durable discovered/downloaded/verified/unavailable queue for resumption.

## Optional API route

The CLI is read-only and requires `CANVAS_TOKEN` already configured in the environment. It follows paginated files/modules/pages, saves source metadata, discovers page-linked files when possible and records external links for browser follow-up. It restricts credentials to the Canvas origin and preserves changed files as separate content-addressed versions. It does **not** retrieve Echo360 or Ed via the Canvas Files API.

```bash
python scripts/canvas_sync.py courses --base https://canvas.example.edu
python scripts/canvas_sync.py sync --base https://canvas.example.edu --course 123 --out "Study Archive"
```

Repeat `--course` for explicitly selected courses. A failed endpoint/file produces a partial report, never a success-shaped empty archive. Retry transient read errors up to three times with short backoff; authentication/permission errors need normal login or a precise gap explanation.

API references checked 2026-09-15: [Files](https://developerdocs.instructure.com/services/canvas/resources/files.md), [Modules](https://developerdocs.instructure.com/services/canvas/resources/modules.md), [Pages](https://developerdocs.instructure.com/services/canvas/resources/pages), [pagination](https://developerdocs.instructure.com/services/canvas/basics/file.pagination.md).

## Evidence and classification

Manifest fields: course/resource ID, stable source URL, title/module, original filename, role, lecture date, teaching week, acquired/source-modified times, bytes, SHA-256, path, status and mapping evidence. Do not put tokens, cookies or expiring signed URLs in the manifest. Saved original course-page bodies may contain private or temporary links; keep these source snapshots local as well.

Classify with page/module context and filename together. Use the four primary folders in SKILL.md. Review ambiguous `_Archive/Needs Review` items; source context takes precedence over a loose filename match. Final answer keys stay with Final papers, and a midterm document with a `final` revision suffix is not a Final exam. ZIP extension alone does not distinguish lecture examples, official solutions and student workspaces. Preserve originals and relative paths even if the same file supports multiple weeks. Keep the original ZIP; safe extraction may omit hidden caches/symlinks but must not flatten dependencies.

On reorganisation, move whole dependency bundles, preserve all original bytes and versions, and repair paths in manifests, inventories and local indexes. Verify before/after hashes and file counts. Keep a reversible old-to-new path map in `_Archive/metadata`; do not leave multiple competing top-level copies of the same categories. Existing unrelated project work stays intact.
