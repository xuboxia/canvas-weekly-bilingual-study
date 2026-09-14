# Canvas Study Kit

**Course files → teaching weeks → detailed Chinese–English HTML guides.**

A reusable AI skill from [H1 Potential](https://h1potential.com/tools). Collect published Canvas slides, tutorial questions, official solutions, code/data and lecture TXT transcripts. Then combine each week's lectures into a detailed bilingual guide, including what the lecturer added beyond the slides.

**课程资料 → 教学周 → 详细中英双语 HTML 讲义。** 按科目整理材料，把 slides 与完整 transcript 对应，保留老师补充的解释、例子和纠错。每个概念、例题和步骤都用中文和英文讲清楚。

## Download and use / 下载与使用

1. [Download the ZIP directly](https://h1potential.com/downloads/canvas-weekly-bilingual-study-v1.0.0.zip), or get it from [GitHub Releases](https://github.com/xuboxia/canvas-weekly-bilingual-study/releases/latest).
2. Give the package to your AI assistant, or install its `canvas-weekly-bilingual-study` folder using the assistant's supported skill mechanism.
3. Use the prompt below. The [getting-started guide](references/getting-started.md) explains capabilities and setup choices.

> 使用这个 skill，按科目整理我的 Canvas 资料，下载每节 lecture 的 TXT transcript，再按教学周生成详细中英双语 HTML。所有概念、例题和解题步骤都要完整双语；老师在 transcript 中补充的内容必须纳入并标注来源。讲义写得自然、清楚，少用口号和装饰性卡片。

> Use this skill to organise my Canvas materials by subject, collect the TXT transcript for each lecture, and create detailed bilingual Chinese–English HTML guides by teaching week. Explain every concept, example and worked step in both languages. Include source-backed lecturer additions. Write clear, natural teaching prose with restrained formatting.

If Canvas access is unavailable, upload already-downloaded materials and request **study existing files** mode. 已有资料也可以直接使用，无需先连上 Canvas。

## What it includes

- Browser workflow for Canvas, Lecture Capture/Echo360 and linked teaching resources.
- Optional read-only Canvas API collector with pagination, hashed downloads and refresh support.
- Safe ZIP extraction, draft classification, PDF/PPTX/text/notebook extraction helpers.
- Teaching-week mapping and full-source coverage guidance.
- A bilingual authoring contract, provenance checks and offline HTML renderer.
- A small [synthetic example](examples/week-01.html), original demo sources and automated helper tests.

This is an **agent workflow**, not a standalone AI service. Your assistant reads the sources and writes the explanations. The included scripts do deterministic file operations and rendering; they do not call paid model APIs. Browser collection uses whichever authorised browser/connector tools your assistant actually provides. The Canvas API helper does not download Echo360/Ed content automatically; those are separate browser steps.

## Compatibility

Works with file-capable agents such as Codex, Claude and ChatGPT where the necessary tools are available. Custom-skill installation and ZIP/file handling vary by product. Ordinary file-upload chat cannot automatically control your logged-in Canvas browser. See [compatibility and fallback instructions](references/getting-started.md).

Python helpers require Python 3.10+. Only PDF/PPTX extraction needs optional packages (`pypdf`, `python-pptx`); you can use the assistant's existing document tools instead.

```bash
python scripts/study_files.py inventory "Study Archive" --out inventory.json
python scripts/render_week.py validate examples/week-01.json
python scripts/render_week.py render examples/week-01.json --out examples/week-01.html
python -m unittest discover -s tests -v
```

## Source fidelity and privacy

“More detailed” means complete explanations and worked reasoning, not padded summaries. Lecturer additions require transcript evidence; the model's own examples are labelled teaching expansions. Missing sources remain visible. Structural validation cannot prove factual accuracy or translation quality; the agent must compare the final guide with the originals.

Use materials you are authorised to access. Keep course files, transcripts and derived guides in your own study archive. This repository contains only reusable instructions, original code and synthetic demonstration content. H1 Potential does not receive your course files through the download page. Never paste Canvas passwords or API tokens into chat. The optional API collector reads only an already-configured `CANVAS_TOKEN` environment variable.

## License

[MIT](LICENSE) for the skill's original instructions, code and demo content. Third-party course materials retain their own rights and are not included or relicensed.
