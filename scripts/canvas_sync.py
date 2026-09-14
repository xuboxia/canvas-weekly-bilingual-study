#!/usr/bin/env python3
"""Read-only Canvas collector. Uses an existing CANVAS_TOKEN; no browser credential extraction."""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import tempfile
import time
import urllib.error
import urllib.parse as U
import urllib.request as R
from html.parser import HTMLParser
from pathlib import Path
from study_files import classify, safe_name, sha256


def origin(url):
    u = U.urlsplit(url)
    return u.scheme.lower(), u.hostname, u.port or (443 if u.scheme == 'https' else 80)


class ScopedRedirect(R.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if U.urlsplit(newurl).scheme != 'https' and U.urlsplit(newurl).hostname not in {'127.0.0.1', 'localhost'}:
            raise ValueError('Refused insecure redirect')
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new and origin(req.full_url) != origin(newurl):
            new.remove_header('Authorization')
        return new


class Client:
    def __init__(self, base, token, opener=None):
        self.base = base.rstrip('/')
        u = U.urlsplit(self.base)
        if u.scheme != 'https' and u.hostname not in {'127.0.0.1', 'localhost'}:
            raise ValueError('Canvas base URL must use HTTPS')
        if u.username or u.password or u.query or u.fragment or u.path not in {'', '/'}:
            raise ValueError('Supply only the Canvas origin, without path/credentials/query')
        self.token = token
        self.opener = opener or R.build_opener(ScopedRedirect())

    def request(self, url, api=False):
        if api:
            url = self.base + url if url.startswith('/') else url
            if origin(url) != origin(self.base) or not U.urlsplit(url).path.startswith('/api/v1/'):
                raise ValueError('Refused off-origin API/pagination URL')
        if U.urlsplit(url).scheme != 'https' and U.urlsplit(url).hostname not in {'localhost', '127.0.0.1'}:
            raise ValueError('Refused non-HTTPS file URL')
        headers = {'User-Agent': 'CanvasWeeklyStudy/1.0', 'Accept': 'application/json' if api else '*/*'}
        if origin(url) == origin(self.base): headers['Authorization'] = 'Bearer ' + self.token
        for attempt in range(3):
            try: return self.opener.open(R.Request(url, headers=headers), timeout=45)
            except urllib.error.HTTPError as e:
                if e.code not in {429, 500, 502, 503, 504} or attempt == 2: raise
                retry = e.headers.get('Retry-After', '')
                time.sleep(min(5, int(retry)) if retry.isdigit() else 1 + attempt)
            except (urllib.error.URLError, TimeoutError):
                if attempt == 2: raise
                time.sleep(1 + attempt)

    def get(self, path):
        with self.request(path, api=True) as response:
            return json.load(response)

    def pages(self, path):
        url = path + ('&' if '?' in path else '?') + 'per_page=100'
        seen = set()
        while url:
            if url in seen: raise ValueError('Pagination loop detected')
            seen.add(url)
            with self.request(url, api=True) as response:
                data = json.load(response)
                if not isinstance(data, list): raise ValueError('Expected paginated list')
                link = response.headers.get('Link', '')
            yield from data
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            url = match.group(1) if match else None


class Links(HTMLParser):
    def __init__(self): super().__init__(); self.urls = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src'} and value: self.urls.append(value)


def error_label(exc):
    # Never log an exception URL; storage redirects may contain signed credentials.
    if isinstance(exc, urllib.error.HTTPError): return f'HTTP {exc.code}'
    return type(exc).__name__


def sync_course(client, course_id, root, include_video=False):
    cid = str(int(course_id))
    info = client.get(f'/api/v1/courses/{cid}')
    course = Path(root) / f'{cid} - {safe_name(info.get("name", cid))}'
    meta = course / 'metadata'; meta.mkdir(parents=True, exist_ok=True)
    original = course / 'Original Exports'; original.mkdir(exist_ok=True)
    previous_path = meta / 'manifest.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    old = {str(f['resource_id']): f for f in previous.get('resources', [])}
    report = {'course_id': cid, 'course': info.get('name', cid),
              'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'resources': [], 'gaps': [], 'external_links': [], 'status': 'partial'}
    contexts, file_ids, file_meta, page_items = {}, set(), {}, []
    def read_list(path, label):
        try: return list(client.pages(path))
        except Exception as e:
            report['gaps'].append({'area': label, 'status': 'access_denied' if isinstance(e, urllib.error.HTTPError) and e.code in {401,403} else 'download_failed', 'reason': error_label(e)})
            return []
    def collect_links(body, context):
        p = Links(); p.feed(body)
        for url in p.urls:
            absolute = U.urljoin(client.base + '/', url)
            split = U.urlsplit(absolute)
            match = re.search(r'/(?:api/v1/)?(?:courses/\d+/)?files/(\d+)(?:/|$)', split.path)
            if origin(absolute) == origin(client.base) and match:
                fid = match.group(1); file_ids.add(fid); contexts.setdefault(fid, []).append(context)
            elif split.scheme in {'http','https'} and origin(absolute) != origin(client.base):
                # A review queue, not a crawler. Strip query tokens in persisted metadata.
                report['external_links'].append({'url': U.urlunsplit((split.scheme, split.netloc, split.path, '', '')), 'context': context, 'status': 'browser_review_required'})
    modules = read_list(f'/api/v1/courses/{cid}/modules', 'modules')
    for module in modules:
        mid = module['id']
        items = read_list(f'/api/v1/courses/{cid}/modules/{mid}/items', f'module {mid}')
        module['items'] = items
        for item in items:
            context = module.get('name', '') + ' / ' + item.get('title', '')
            if item.get('type') == 'File':
                fid = str(item['content_id']); file_ids.add(fid); contexts.setdefault(fid, []).append(context)
            if item.get('external_url'): collect_links('<a href="' + item['external_url'].replace('"', '&quot;') + '">', context)
    page_items = read_list(f'/api/v1/courses/{cid}/pages?include[]=body', 'pages')
    try:
        front = client.get(f'/api/v1/courses/{cid}/front_page')
        if front.get('page_id') not in {p.get('page_id') for p in page_items}: page_items.append(front)
    except urllib.error.HTTPError as e:
        if e.code != 404: report['gaps'].append({'area': 'front_page', 'reason': error_label(e)})
    for p in page_items:
        if 'body' not in p:
            try: p.update(client.get(f'/api/v1/courses/{cid}/pages/' + U.quote(str(p['url']), safe='')))
            except Exception as e:
                report['gaps'].append({'area': 'page', 'id': p.get('page_id'), 'reason': error_label(e)}); continue
        collect_links(p.get('body') or '', p.get('title', ''))
    for f in read_list(f'/api/v1/courses/{cid}/files', 'files listing'):
        fid = str(f['id']); file_ids.add(fid); file_meta[fid] = f
    # Page bodies are course sources; keep them local, never in a public skill release.
    (meta / 'pages.json').write_text(json.dumps(page_items, ensure_ascii=False, indent=2))
    (meta / 'modules.json').write_text(json.dumps(modules, ensure_ascii=False, indent=2))
    for fid in sorted(file_ids, key=int):
        entry = {'resource_id': fid, 'source_url': f'{client.base}/courses/{cid}/files/{fid}', 'context': contexts.get(fid, []), 'week': None, 'mapping_status': 'unreviewed'}
        try:
            f = file_meta.get(fid) or client.get(f'/api/v1/courses/{cid}/files/{fid}')
            if f.get('locked_for_user') or f.get('hidden_for_user'):
                entry['status'] = 'access_denied'; report['resources'].append(entry); continue
            name = safe_name(f.get('display_name') or f.get('filename') or fid)
            role = classify(name, ' '.join(entry['context']))
            entry.update({'original_name': name, 'role': role, 'source_updated_at': f.get('updated_at')})
            if not include_video and (Path(name).suffix.lower() in {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'} or str(f.get('content-type', '')).startswith('video/')):
                entry['status'] = 'out_of_scope'; report['resources'].append(entry); continue
            prev = old.get(fid, {})
            prev_file = course / prev.get('path', '__missing__')
            if prev.get('source_updated_at') and prev.get('source_updated_at') == f.get('updated_at') and prev_file.is_file() and sha256(prev_file) == prev.get('sha256'):
                entry.update({k:prev[k] for k in ['path','sha256','bytes']}); entry['status'] = 'verified'
            else:
                fd, temp = tempfile.mkstemp(prefix='canvas-', suffix='.part', dir=meta); os.close(fd)
                try:
                    with client.request(f['url']) as response, open(temp, 'wb') as out:
                        content_type = response.headers.get('Content-Type', '')
                        shutil.copyfileobj(response, out)
                    temp = Path(temp)
                    if temp.stat().st_size == 0: raise ValueError('Empty download')
                    if f.get('size') is not None and temp.stat().st_size != f['size']: raise ValueError('Size mismatch')
                    with temp.open('rb') as check:
                        if name.lower().endswith('.pdf') and check.read(5) != b'%PDF-': raise ValueError('PDF header mismatch')
                    if 'text/html' in content_type and not name.lower().endswith(('.html','.htm')): raise ValueError('Unexpected HTML login/error response')
                    digest = sha256(temp)
                    dest = course / role / f'{fid}-{digest[:12]}-{name}'
                    dest.parent.mkdir(exist_ok=True)
                    if dest.exists(): temp.unlink()
                    else: temp.replace(dest)
                    entry.update({'path': dest.relative_to(course).as_posix(), 'bytes': dest.stat().st_size, 'sha256': digest, 'status': 'verified'})
                finally:
                    Path(temp).unlink(missing_ok=True)
        except Exception as e:
            entry.update({'status': 'download_failed', 'reason': error_label(e)})
        report['resources'].append(entry)
        previous_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    report['external_links'] = list({(e['url'],e['context']):e for e in report['external_links']}.values())
    # External pages/transcripts always require the browser coverage audit.
    report['status'] = 'canvas_files_verified' if not report['gaps'] and all(x['status'] in {'verified', 'out_of_scope'} for x in report['resources']) else 'partial'
    report['lecture_capture_status'] = 'browser_review_required'
    previous_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return {'course_id':cid, 'status':report['status'], 'verified':sum(x['status']=='verified' for x in report['resources']), 'gaps':len(report['gaps']), 'external_links':len(report['external_links'])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['courses','sync']); p.add_argument('--base', required=True)
    p.add_argument('--course', action='append', default=[]); p.add_argument('--out', default='Study Archive')
    p.add_argument('--include-video', action='store_true', help='Download attached video files only if the user requested them')
    a = p.parse_args(); token = os.environ.get('CANVAS_TOKEN')
    if not token: p.error('CANVAS_TOKEN is not configured; use the authenticated browser workflow')
    client = Client(a.base, token)
    if a.command == 'courses':
        print(json.dumps([{'id':c['id'],'name':c.get('name'),'course_code':c.get('course_code')} for c in client.pages('/api/v1/courses?enrollment_state=active')],ensure_ascii=False,indent=2)); return
    if not a.course: p.error('Supply at least one explicitly selected --course ID')
    partial = False
    for cid in a.course:
        try:
            result = sync_course(client,cid,a.out,a.include_video); partial |= result['status']=='partial'; print(json.dumps(result,ensure_ascii=False))
        except Exception as e:
            partial = True; print(json.dumps({'course_id':cid,'status':'failed','reason':error_label(e)}))
    raise SystemExit(2 if partial else 0)


if __name__ == '__main__': main()
