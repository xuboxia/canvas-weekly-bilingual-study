#!/usr/bin/env python3
"""Render a Chinese, English or bilingual offline weekly guide. No model calls."""
import argparse
import base64
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
KINDS = {
    'slide': ('讲义内容', 'Slide content'),
    'lecturer_addition': ('教授补充', 'Lecturer addition'),
    'teaching_expansion': ('教学补充', 'Teaching expansion'),
    'uncertain': ('转录待核对', 'Uncertain transcript'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def selected_languages(mode):
    require(isinstance(mode, str) and mode in {'both', 'zh', 'en'}, 'output_language must be both, zh or en')
    return ('zh', 'en') if mode == 'both' else (mode,)


def localized(value, label, languages):
    require(isinstance(value, dict), f'{label}: expected a language-keyed object')
    for language in languages:
        text = value.get(language)
        require(isinstance(text, str) and text.strip(), f'{label}: {language} is required')
        pattern = r'[\u3400-\u9fff]' if language == 'zh' else r'[A-Za-z]'
        require(re.search(pattern, text), f'{label}: {language} explanation is missing')


def local_path(value):
    require(isinstance(value, str) and value.strip(), 'Expected a relative source path')
    p = urlsplit(value)
    decoded = unquote(p.path).replace('\\', '/')
    require(not p.scheme and not p.netloc and not p.query and not p.fragment and not decoded.startswith('/') and ':' not in decoded, 'Only relative local paths are allowed')
    return value


def validate(d):
    require(d.get('schema_version') == 1, 'schema_version must be 1')
    languages = selected_languages(d.get('output_language', 'both'))
    def pair(value, label):
        localized(value, label, languages)
    for field in ('course', 'title'):
        pair(d.get(field), field)
    require(type(d.get('week')) is int and d['week'] > 0, 'week must be a positive teaching-week number')
    require(d.get('status') in {'partial', 'complete'}, 'status must be partial or complete')
    require(isinstance(d.get('missing'), list), 'missing must be a list, including when empty')
    for value in d['missing']:
        pair(value, 'missing source')
    require(isinstance(d.get('sources'), list) and d['sources'], 'sources are required')
    sources, units = {}, set()
    for source in d['sources']:
        sid = source.get('id')
        require(isinstance(sid, str) and re.fullmatch(r'[a-z][a-z0-9-]*', sid) and sid not in sources, 'Source IDs must be unique slugs')
        pair(source.get('title'), f'source {sid}')
        require(source.get('kind') in {'slides', 'transcript', 'tutorial', 'solution', 'other'}, f'{sid}: invalid source kind')
        local_path(source.get('path'))
        require(isinstance(source.get('units'), list) and source['units'] and all(isinstance(x, str) and x.strip() for x in source['units']), f'{sid}: inventory source unit locators')
        require(len(source['units']) == len(set(source['units'])), f'{sid}: duplicate source units')
        units.update((sid, x) for x in source['units'])
        sources[sid] = source
    require(isinstance(d.get('lectures'), list) and d['lectures'], 'List every lecture in this teaching week')
    for lecture in d['lectures']:
        pair(lecture.get('title'), 'lecture title')
        require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', lecture.get('date', '')), 'Lecture dates must be YYYY-MM-DD')
        require(isinstance(lecture.get('sources'), list) and lecture['sources'] and all(s in sources for s in lecture['sources']), 'Lecture references an unknown source')
    require(isinstance(d.get('goals'), list) and d['goals'], 'goals are required')
    for goal in d['goals']:
        pair(goal, 'learning goal')
    require(isinstance(d.get('sections'), list) and d['sections'], 'sections are required')
    ids, citations = set(), set()
    uncertain = False
    for section in d['sections']:
        sid = section.get('id')
        require(isinstance(sid, str) and re.fullmatch(r'[a-z][a-z0-9-]*', sid) and sid not in ids, 'Section IDs must be unique slugs')
        ids.add(sid)
        pair(section.get('title'), f'section {sid}')
        require(isinstance(section.get('blocks'), list) and section['blocks'], f'{sid}: empty section')
        for block in section['blocks']:
            kind = block.get('kind')
            require(kind in KINDS, f'{sid}: invalid provenance kind')
            uncertain |= kind == 'uncertain'
            pair(block.get('text'), f'{sid}: explanation')
            for field in ('title', 'answer'):
                if field in block:
                    pair(block[field], f'{sid}: {field}')
            if 'code' in block:
                require(isinstance(block['code'], str) and block['code'].strip(), f'{sid}: code must be text')
            refs = block.get('citations', [])
            require(isinstance(refs, list), f'{sid}: citations must be a list')
            for ref in refs:
                key = (ref.get('source'), ref.get('locator'))
                require(key in units, f'{sid}: citation must match an inventoried source unit')
                citations.add((key[0], key[1], sid))
            if kind in {'slide', 'lecturer_addition', 'uncertain'}:
                require(refs, f'{sid}: source-derived content needs citations')
            if kind == 'lecturer_addition':
                require(any(sources[r['source']]['kind'] == 'transcript' for r in refs), f'{sid}: lecturer additions need transcript evidence')
            if 'table' in block:
                table = block['table']
                require(table.get('headers') and table.get('rows'), f'{sid}: table needs headers and rows')
                for cell in table['headers']:
                    pair(cell, f'{sid}: table header')
                for row in table['rows']:
                    require(len(row) == len(table['headers']), f'{sid}: table columns do not match')
                    for cell in row:
                        pair(cell, f'{sid}: table cell')
            if 'image' in block:
                local_path(block['image'].get('path'))
                pair(block['image'].get('caption'), f'{sid}: image caption and alt text')
    require(isinstance(d.get('coverage'), list), 'coverage is required')
    covered = set()
    unresolved = False
    for item in d['coverage']:
        key = (item.get('source'), item.get('locator'))
        require(key in units and key not in covered, 'Coverage has an unknown or repeated source unit')
        covered.add(key)
        if item.get('section'):
            require((*key, item['section']) in citations, 'Coverage must point to a section with a matching citation')
        else:
            require(item.get('disposition') in {'excluded', 'unresolved'}, 'Unmapped coverage needs excluded or unresolved disposition')
            pair(item.get('reason'), 'coverage reason')
            unresolved |= item['disposition'] == 'unresolved'
    require(covered == units, 'Coverage must account for every inventoried source unit, including unresolved units')
    if d['status'] == 'complete':
        require(d.get('reviewed') is True and not d['missing'] and not unresolved and not uncertain, 'Complete requires semantic review and no unresolved coverage or missing sources')
    for entry in d.get('glossary', []):
        pair(entry.get('term'), 'glossary term')
        pair(entry.get('definition'), 'glossary definition')
    return d


def esc(text):
    return html.escape(str(text), quote=True)


def render(d, source_dir):
    validate(d)
    mode = d.get('output_language', 'both')
    languages = selected_languages(mode)
    def bi(value, tag='span'):
        return ''.join(f'<{tag} lang="{"zh-CN" if key == "zh" else "en"}" class="lang-{key}">{esc(value[key])}</{tag}>' for key in languages)
    def label(zh, en):
        return bi({'zh': zh, 'en': en})
    def plain(zh, en):
        return ' / '.join({'zh': zh, 'en': en}[key] for key in languages)
    source_dir = Path(source_dir).resolve()
    for source in d['sources']:
        require((source_dir / source['path']).is_file(), f'Missing local source: {source["path"]}')
    sections = []
    for section in d['sections']:
        blocks = []
        for block in section['blocks']:
            zh, en = KINDS[block['kind']]
            body = f'<p class="provenance">{label(zh, en)}</p>'
            if block.get('title'):
                body += '<h3>' + bi(block['title']) + '</h3>'
            body += '<div class="bilingual">' + bi(block['text'], 'p') + '</div>'
            if 'code' in block:
                body += '<pre><code>' + esc(block['code']) + '</code></pre>'
            if 'table' in block:
                table = block['table']
                body += '<div class="table-wrap"><table><thead><tr>' + ''.join('<th>' + bi(v) + '</th>' for v in table['headers']) + '</tr></thead><tbody>'
                body += ''.join('<tr>' + ''.join('<td>' + bi(v) + '</td>' for v in row) + '</tr>' for row in table['rows']) + '</tbody></table></div>'
            if 'image' in block:
                item = block['image']; file = (source_dir / item['path']).resolve()
                require(file.is_relative_to(source_dir), 'Embed image files from the guide JSON folder or its subfolders')
                mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(file.suffix.lower())
                require(mime and file.is_file(), 'Use a local PNG/JPEG/WebP figure')
                require(file.stat().st_size <= 20 * 1024**2, 'Image exceeds the 20 MiB embedding limit')
                data = base64.b64encode(file.read_bytes()).decode('ascii')
                alt = ' / '.join(item['caption'][key] for key in languages)
                body += f'<figure><img src="data:{mime};base64,{data}" alt="{esc(alt)}"><figcaption>{bi(item["caption"])}</figcaption></figure>'
            if 'answer' in block:
                body += '<details><summary>' + label('参考解答', 'Worked answer') + '</summary><div class="bilingual">' + bi(block['answer'], 'p') + '</div></details>'
            if block.get('citations'):
                body += '<p class="citations">' + label('来源', 'Sources') + ': ' + ' · '.join(f'<a href="#source-{esc(r["source"])}">{esc(r["source"])} — {esc(r["locator"])}</a>' for r in block['citations']) + '</p>'
            blocks.append('<article class="block">' + body + '</article>')
        sections.append(f'<section class="lesson" id="{esc(section["id"])}"><h2>{bi(section["title"])}</h2>' + ''.join(blocks) + '</section>')
    navigation = ''.join(f'<a href="#{esc(s["id"])}">{bi(s["title"])}</a>' for s in d['sections'])
    lectures = ''.join(f'<li><time>{esc(x["date"])}</time> {bi(x["title"])} <small>{esc(", ".join(x["sources"]))}</small></li>' for x in d['lectures'])
    sources = ''.join(f'<li id="source-{esc(s["id"])}"><strong>{esc(s["id"])}</strong> <a href="{esc(s["path"])}">{bi(s["title"])}</a></li>' for s in d['sources'])
    coverage = ''.join('<tr><td>' + esc(x['source']) + '</td><td>' + esc(x['locator']) + '</td><td>' + (f'<a href="#{esc(x["section"])}">{esc(x["section"])}</a>' if x.get('section') else bi(x['reason'])) + '</td></tr>' for x in d['coverage'])
    glossary = ''.join('<dt>' + bi(x['term']) + '</dt><dd>' + bi(x['definition']) + '</dd>' for x in d.get('glossary', []))
    missing = ''.join('<li>' + bi(x) + '</li>' for x in d['missing'])
    status = label('已完成来源复核', 'Source review completed') if d['status'] == 'complete' else label('部分完成：请查看缺失与待核对项', 'Partial: check missing and unresolved items')
    css = (ROOT / 'assets/guide.css').read_text(encoding='utf-8')
    js = (ROOT / 'assets/guide.js').read_text(encoding='utf-8')
    controls = '<div role="group" aria-label="Language / 语言"><button data-language="both" aria-pressed="true">中 / EN</button><button data-language="zh" aria-pressed="false">中文</button><button data-language="en" aria-pressed="false">English</button></div>' if mode == 'both' else ''
    page_title = ' / '.join(d['course'][key] for key in languages) + f' · {plain("教学周", "Week")} {d["week"]:02d} · ' + ' / '.join(d['title'][key] for key in languages)
    return f'''<!doctype html>
<html lang="{'zh-CN' if mode == 'zh' else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<style>{css}</style></head><body data-language="{mode}">
<header class="toolbar"><a href="#top">{label('每周学习讲义', 'Weekly study guide')}</a>{controls}<button id="print">{label('打印', 'Print')}</button></header>
<div class="layout"><aside><label for="search">{label('搜索本周内容', 'Search this week')}</label><input id="search" type="search"><nav aria-label="{esc(plain('目录', 'Contents'))}">{navigation}</nav></aside>
<main id="top"><header class="intro"><p>{bi(d['course'])} · {label('教学周', 'Teaching week')} {d['week']:02d}</p><h1>{bi(d['title'])}</h1><p class="status">{status}</p>{'<ul class="missing">' + missing + '</ul>' if missing else ''}<h2>{label('本周课堂', 'This week’s lectures')}</h2><ul>{lectures}</ul><h2>{label('学习目标', 'Learning goals')}</h2><ul>{''.join('<li>' + bi(g) + '</li>' for g in d['goals'])}</ul></header>
<p id="search-empty" hidden>{label('没有匹配的章节。', 'No matching sections.')}</p>{''.join(sections)}
<section class="glossary"><h2>{label('术语对照', 'Glossary')}</h2><dl>{glossary}</dl></section>
<section><h2>{label('原始材料', 'Original sources')}</h2><p>{label('原始材料链接需要相邻保存的来源文件；讲义正文可离线阅读。', 'Source links need the accompanying local files; the guide text works offline.')}</p><ul>{sources}</ul><details><summary>{label('来源覆盖记录', 'Source coverage record')}</summary><div class="table-wrap"><table><thead><tr><th>{label('来源', 'Source')}</th><th>{label('位置', 'Locator')}</th><th>{label('讲解章节或说明', 'Section or explanation')}</th></tr></thead><tbody>{coverage}</tbody></table></div></details></section>
<footer>{label('由课程材料整理。自动格式检查不能代替内容核对。', 'Prepared from course materials. Format validation does not replace content review.')}</footer></main></div><script>{js}</script></body></html>'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['validate', 'render']); p.add_argument('source'); p.add_argument('--out')
    p.add_argument('--language', choices=['both', 'zh', 'en'], help='Override output_language; selects existing authored text, never translates it')
    a = p.parse_args(); source = Path(a.source)
    data = json.loads(source.read_text(encoding='utf-8-sig'))
    if a.language:
        data['output_language'] = a.language
    validate(data)
    if a.command == 'validate':
        print('Structure and declared coverage validated; semantic review is still required.'); return
    if not a.out: p.error('render requires --out')
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    document = render(data, source.parent)
    # Keep source hyperlinks valid when the HTML is saved in another folder.
    import os
    for item in data['sources']:
        relative = Path(os.path.relpath((source.parent / item['path']).resolve(), out.parent.resolve())).as_posix()
        document = document.replace('href="' + esc(item['path']) + '"', 'href="' + esc(relative) + '"')
    out.write_text(document, encoding='utf-8')
    print(f'Wrote {out.name}')


if __name__ == '__main__':
    main()
