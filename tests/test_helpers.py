import copy
import io
import json
import stat
import sys
import tempfile
import unittest
import urllib.request as R
import zipfile
from pathlib import Path
from email.message import Message

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from study_files import extract_zip, extract, sha256
from canvas_sync import Client, ScopedRedirect, sync_course
from render_week import validate, render


class Response(io.BytesIO):
    def __init__(self, body, headers=None):
        super().__init__(body)
        self.headers = headers or {}


class FakeOpener:
    def __init__(self, responses):
        self.responses = responses
        self.requests = []
    def open(self, request, timeout):
        self.requests.append(request)
        body, headers = self.responses[request.full_url]
        return Response(body, headers)


class FilesTest(unittest.TestCase):
    def test_zip_preserves_structure_and_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'a.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('code/main.py', 'print(1)'); z.writestr('code/data.csv', 'a,b\n1,2')
                link = zipfile.ZipInfo('link'); link.create_system = 3; link.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(link, '/etc/passwd')
            result = extract_zip(archive, root / 'out')
            self.assertEqual(result['written'], 2)
            self.assertFalse((root / 'out/link').exists())
            self.assertEqual((root / 'out/code/data.csv').read_text(), 'a,b\n1,2')
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('good.txt', 'safe'); z.writestr('../escape.txt', 'unsafe')
            with self.assertRaises(ValueError): extract_zip(archive, root / 'bad')
            self.assertFalse((root / 'bad/good.txt').exists())
            self.assertFalse((root / 'escape.txt').exists())

    def test_changed_zip_member_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'a.zip'; out = root / 'out'; out.mkdir()
            (out / 'notes.txt').write_text('original')
            with zipfile.ZipFile(archive, 'w') as z: z.writestr('notes.txt', 'changed')
            with self.assertRaises(ValueError): extract_zip(archive, out)
            self.assertEqual((out / 'notes.txt').read_text(), 'original')

    def test_transcript_line_numbers_and_notebook_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            text = Path(folder) / 'lecture.txt'; text.write_text('first\n\nthird\n')
            self.assertEqual(extract(text)['units'][2], {'locator': 'line 3', 'text': 'third'})
            notebook = Path(folder) / 'exercise.ipynb'
            notebook.write_text(json.dumps({'cells': [{'cell_type': 'code', 'source': ['raise RuntimeError("do not run")']}]}))
            self.assertIn('raise RuntimeError', extract(notebook)['units'][0]['text'])


class CollectorTest(unittest.TestCase):
    def test_opaque_pagination_and_no_cross_origin_token(self):
        base = 'https://canvas.example.edu'
        opener = FakeOpener({base + '/api/v1/files?per_page=100': (b'[1]', {'Link': '<' + base + '/api/v1/files?cursor=opaque>; rel="next"'}), base + '/api/v1/files?cursor=opaque': (b'[2]', {}), 'https://storage.example.edu/file': (b'file', {})})
        client = Client(base, 'test-only-token', opener)
        self.assertEqual(list(client.pages('/api/v1/files')), [1, 2])
        client.request('https://storage.example.edu/file').close()
        self.assertIsNone(opener.requests[-1].get_header('Authorization'))
        with self.assertRaises(ValueError): client.get('https://storage.example.edu/api/v1/files')
        redirected = ScopedRedirect().redirect_request(R.Request(base + '/file', headers={'Authorization': 'Bearer test-only-token'}), None, 302, 'redirect', Message(), 'https://storage.example.edu/file')
        self.assertIsNone(redirected.get_header('Authorization'))

    def test_download_identity_refresh_and_bad_pdf(self):
        class FakeClient:
            base = 'https://canvas.example.edu'
            changed = False
            downloads = 0
            def get(self, path):
                if path.endswith('/front_page'): return {'page_id': 1, 'body': '', 'title': 'Home'}
                return {'name': 'Example Course'}
            def pages(self, path):
                if path.endswith('/files'):
                    return [{'id': n, 'display_name': 'slides.pdf', 'updated_at': 'new' if self.changed else 'old', 'url': f'https://storage.example.edu/{n}', 'size': 8} for n in [1, 2]]
                return []
            def request(self, url):
                self.downloads += 1
                return Response(b'%PDF-two' if self.changed else b'%PDF-one', {'Content-Type': 'application/pdf'})
        with tempfile.TemporaryDirectory() as folder:
            client = FakeClient(); sync_course(client, 1, folder)
            root = next(Path(folder).iterdir()); manifest = root / 'metadata/manifest.json'
            first = json.loads(manifest.read_text())['resources']
            self.assertNotEqual(first[0]['path'], first[1]['path'])
            self.assertEqual(client.downloads, 2)
            sync_course(client, 1, folder); self.assertEqual(client.downloads, 2)
            client.changed = True; sync_course(client, 1, folder)
            new = json.loads(manifest.read_text())['resources']
            self.assertNotEqual(first[0]['sha256'], new[0]['sha256'])
            self.assertTrue((root / first[0]['path']).is_file())
            client.request = lambda url: Response(b'<html>xx', {'Content-Type': 'text/html'})
            client.changed = False
            result = sync_course(client, 1, folder)
            self.assertEqual(result['status'], 'partial')


class RendererTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/week-01.json').read_text())
    def test_render_escapes_text_and_keeps_both_languages(self):
        self.data['sections'][0]['blocks'][0]['text']['en'] += '<script>alert(1)</script>'
        document = render(self.data, ROOT / 'examples')
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', document)
        self.assertNotIn('<script>alert(1)', document)
        self.assertIn('lang="zh-CN"', document)
        self.assertIn('lang="en"', document)
        self.assertIn('demo-transcript.txt', document)
    def test_reject_missing_language_and_false_complete(self):
        for mutate in [lambda d: d['title'].pop('zh'), lambda d: d['coverage'].pop(), lambda d: d.update(reviewed=False), lambda d: d['missing'].append({'zh': '缺少来源', 'en': 'Missing source'})]:
            data = copy.deepcopy(self.data); mutate(data)
            with self.assertRaises(ValueError): validate(data)
    def test_lecturer_addition_requires_transcript(self):
        self.data['sections'][0]['blocks'][1]['citations'] = [{'source': 'slides', 'locator': 'line 3'}]
        with self.assertRaises(ValueError): validate(self.data)
    def test_explicit_partial_coverage_is_supported(self):
        self.data['status'] = 'partial'; self.data['reviewed'] = False
        self.data['coverage'][-1] = {'source': 'transcript', 'locator': 'line 3', 'disposition': 'unresolved', 'reason': {'zh': '待核对录音', 'en': 'Audio review pending'}}
        validate(self.data)
    def test_external_source_links_rejected(self):
        self.data['sources'][0]['path'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError): validate(self.data)


if __name__ == '__main__': unittest.main()
