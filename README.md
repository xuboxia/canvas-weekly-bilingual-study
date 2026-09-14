# Canvas Study Kit

**Course files → teaching weeks → detailed HTML guides in English, Chinese or both.**

A reusable AI skill from [H1 Potential](https://h1potential.com/tools). Ask your browser-enabled AI agent to **automatically collect Canvas lecture slides, tutorial questions, official solutions and lecture transcripts (the written text of the recording)**, and organise the downloaded files by subject. Then combine each week's lectures into a detailed guide in your chosen language, including what the lecturer added beyond the slides.

**课程资料 → 教学周 → 中文、英文或中英双语 HTML 讲义。** **让具备浏览器或 Canvas 访问能力的 AI 自动抓取 slides、tutorial questions、官方解答和每节录播的 transcript（课堂文字稿）**，按科目分类保存，把 slides 与完整文字稿对应，保留老师补充的解释、例子和纠错。按所选语言完整讲清每个概念、例题和步骤；默认中英双语。

## Download and use / 下载与使用

1. [Download the ZIP directly](https://h1potential.com/downloads/canvas-weekly-bilingual-study-v1.2.0.zip), or get it from [GitHub Releases](https://github.com/xuboxia/canvas-weekly-bilingual-study/releases/latest).
2. Give the package to your AI assistant, or install its `canvas-weekly-bilingual-study` folder using the assistant's supported skill mechanism.
3. Use the prompt below. The [getting-started guide](references/getting-started.md) explains capabilities and setup choices.

> 使用这个 skill，按科目整理我的 Canvas 资料，下载每节 lecture 的 TXT transcript，再按教学周生成详细中英双语 HTML。所有概念、例题和解题步骤都要完整双语；老师在 transcript 中补充的内容必须纳入并标注来源。讲义写得自然、清楚，少用口号和装饰性卡片。

> Use this skill to organise my Canvas materials by subject, collect the TXT transcript for each lecture, and create detailed bilingual Chinese–English HTML guides by teaching week. Explain every concept, example and worked step in both languages. Include source-backed lecturer additions. Write clear, natural teaching prose with restrained formatting.

If Canvas access is unavailable, upload already-downloaded materials and request **study existing files** mode. 已有资料也可以直接使用，无需先连上 Canvas。

## What is a transcript? / Transcript 是什么？

A lecture transcript is the **written text of a lecture recording**. It can contain the teacher's spoken examples, corrections and explanations that are absent from the slides. With authorised browser access, the agent opens each available recording in Lecture Capture/Echo360 (or the school's equivalent), finds Transcript and downloads TXT where available. Access and download labels vary by school; recordings without an available transcript are reported as gaps.

**Transcript 就是课堂录音的文字稿。** 很多内容只在老师讲课时出现，slides 上没有。这个 skill 会指导有访问能力的 AI 进入每节可访问的录播，下载可用的 TXT 文字稿，再与该周 slides 合起来写讲义。学校未生成或不允许下载的文字稿会明确标记，不会假装已经抓取。

## Two worked examples / 两类成品示例

Open [the example index](examples/index.html) after downloading the ZIP; GitHub shows HTML source rather than rendering the guide.

| Example | What the guide explains | Files |
| --- | --- | --- |
| Finance / 金融 | Cash-flow timing, discounting, NPV and a worked timing change / 现金流、折现、净现值及收款推迟的影响 | [HTML](examples/finance/week-01.html) · [JSON](examples/finance/week-01.json) |
| Coding / 编程 | Reference copying, mutation, reassignment and program output / 引用复制、修改对象、重新赋值与程序输出 | [HTML](examples/week-01.html) · [JSON](examples/week-01.json) |

Both use original synthetic slides and transcripts, with full explanations, worked answers and source citations. They demonstrate the same course-neutral workflow; the skill is not limited to these subjects. 两类示例均为原创演示，并非真实课程记录。

The finance arithmetic uses a fictional case. For the general NPV method, see [OpenStax, Principles of Finance 2e, §16.2](https://openstax.org/books/principles-finance-2e/pages/16-2-net-present-value-npv-method).

## Choose your guide language / 选择讲义语言

Specify the output language in your request; the default is **Chinese–English bilingual**. All three modes include the same full explanations, worked answers and source-backed lecturer additions. English-only and Chinese-only modes author only the requested language; you do not need to generate an unused translation first.

| Mode / 模式 | Add to your prompt / 在提示词中说明 |
| --- | --- |
| English only | “Generate the guides entirely in English, including examples, answers, captions and navigation.” |
| 中文 | “只生成中文版，正文、例题、答案、图注和界面都用中文；保留必要的技术术语和代码标识符。” |
| 中英双语 / Bilingual | “Generate complete Chinese and English explanations for every concept and worked step.” |

例如：**“使用这个 skill，按周生成纯英文 HTML 讲义，包含教授补充和完整例题。”** 即使提示词用中文，成品也会按明确要求只用英文。双语成品支持显示切换；单语成品只包含所选语言。

## What it includes

- Browser workflow for Canvas, Lecture Capture/Echo360 and linked teaching resources.
- Optional read-only Canvas API collector with pagination, hashed downloads and refresh support.
- Safe ZIP extraction, draft classification, PDF/PPTX/text/notebook extraction helpers.
- Teaching-week mapping and full-source coverage guidance.
- A language-selectable authoring contract, provenance checks and offline HTML renderer.
- [Finance and Coding examples](examples/index.html), original demo slides/transcripts and automated helper tests.

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
