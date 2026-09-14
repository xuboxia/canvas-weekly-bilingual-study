#!/usr/bin/env python3
"""Build a reproducible public ZIP from the skill's explicit package paths."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'canvas-weekly-bilingual-study'
ALLOWED = ['SKILL.md', 'README.md', 'LICENSE', 'VERSION', 'agents', 'scripts', 'references', 'assets', 'examples', 'tests']


def build(out):
    version = (ROOT / 'VERSION').read_text().strip()
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    dest = out / f'{NAME}-v{version}.zip'
    files = []
    for name in ALLOWED:
        p = ROOT / name
        files.extend(p.rglob('*') if p.is_dir() else [p])
    files = [p for p in files if p.is_file() and not p.is_symlink() and not any(x.startswith('.') or x == '__pycache__' for x in p.relative_to(ROOT).parts)]
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo(f'{NAME}/{path.relative_to(ROOT).as_posix()}', date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    (out / f'{dest.name}.sha256').write_text(f'{digest}  {dest.name}\n')
    with zipfile.ZipFile(dest) as archive:
        if archive.testzip(): raise ValueError('ZIP integrity check failed')
    return {'version': version, 'file': dest.name, 'bytes': dest.stat().st_size, 'sha256': digest, 'members': len(files)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--out', required=True)
    print(json.dumps(build(parser.parse_args().out), indent=2))
