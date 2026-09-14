# Get started / 开始使用

This skill uses the capabilities of the AI agent that loads it. It does not include a model subscription, Canvas login, browser access or API credentials.

## Copy a prompt / 复制后开始

> 请使用这个 skill：整理我选定的 Canvas 课程资料，下载每节 lecture 的 TXT transcript，并按教学周生成详细的中英文 HTML。教授在课堂上补充、纠错或强调而 slides 没写出的内容也要放进去，并给出来源。先核对课程和教学周，再开始。

Already have files / 已有资料：

> 请使用这个 skill，把我上传的第 3 周 slides 和 transcript 做成详细中英文 HTML。所有解释、例题、解题步骤和教授补充都要双语，不要只翻译 slides。

Refresh / 更新：

> 更新这些课程新发布的资料和 transcript，只重做来源改变的每周 HTML，保留原文件和缺失说明。

## Choose the output language / 选择生成语言

Use `English only`, `中文` or `Chinese–English bilingual` in your request. Default: bilingual. The language you type the request in is separate from the requested guide language. Single-language mode does not need to generate another translation first; every mode retains the complete explanations, worked answers, transcript additions and source checks.

- **English only:** “Use this skill with my slides and lecture transcripts to create detailed weekly HTML guides entirely in English. Include all worked steps and lecturer additions with sources. Use English for headings, captions, answers and navigation too.”
- **中文：** “使用这个 skill，结合 slides 和完整 transcript，按教学周生成纯中文 HTML。正文、例题、解答、图注和界面都用中文，纳入教授补充并标注来源，保留必要技术术语和代码标识符。”
- **中英双语：** “生成完整中英双语讲义，每个概念和解题步骤都在两种语言中讲清楚。”

The author records the choice as `output_language: "en"`, `"zh"` or `"both"` in each guide JSON. Refresh keeps that choice unless you request a change. Bilingual HTML has display-language controls; single-language HTML contains only the chosen language.

## Compatibility / 兼容方式

- **Codex / Agent Skills-compatible coding agents:** load the folder through the agent's normal skill mechanism. Scripts need Python 3.10+; extraction of PDF/PPTX optionally needs `pypdf`/`python-pptx`.
- **Claude:** upload a ZIP containing one skill folder with `SKILL.md` through custom skills, where supported. Tool availability depends on the workspace. [Official creation guide](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills), [usage guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
- **ChatGPT / file-capable chat:** upload the ZIP and ask it to unpack and follow `SKILL.md`, if its file tools support this. This is an instruction bundle, not a promise of automatic installation. If ZIP reading is unavailable, provide `SKILL.md` and the source files. If the chat cannot access your logged-in Canvas browser, upload downloaded slides/TXT and use existing-files mode.
- **Other agents:** need file reading to follow the skill. Automatic collection additionally needs an authorized browser/connector or configured Canvas API path. Creating downloadable HTML requires file creation/code execution; otherwise provide HTML source without claiming a file was created.

不要把密码或 token 发进聊天。已有登录浏览器的工作流不需要新建 API token。可选 API 脚本只从已配置的 `CANVAS_TOKEN` 环境变量读取凭据。

## Helpers / 辅助命令

```bash
python scripts/study_files.py extract-zip export.zip --out extracted-export
python scripts/study_files.py inventory "Study Archive" --out inventory.json
python scripts/study_files.py extract slides.pdf --out extracted/slides.json
python scripts/study_files.py extract lecture.txt --out extracted/transcript.json
python scripts/render_week.py render week-03.json --out week-03.html
```

The host AI reads sources and writes teaching content in the chosen language(s). Scripts perform deterministic file operations and never call a paid model API behind the scenes.
