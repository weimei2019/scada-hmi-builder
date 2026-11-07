#!/usr/bin/env python3
"""Build a portable skill ZIP; add WorkBuddy metadata only to its package."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
NAME = 'scada-25d-builder'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['standard', 'workbuddy'], default='standard')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f'{NAME}-{args.target}.zip'
    files = [ROOT / name for name in ('SKILL.md', 'README.md', 'LICENSE')]
    for directory in ('agents', 'references', 'scripts', 'assets'):
        files.extend(p for p in (ROOT / directory).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(files):
            data = path.read_bytes()
            if args.target == 'workbuddy' and path.name == 'SKILL.md':
                text = data.decode('utf-8')
                frontmatter, body = text.removeprefix('---\n').split('\n---\n', 1)
                metadata = {
                    'display_name': 'SCADA 2.5D 组态构建器',
                    'display_name_en': 'SCADA 2.5D Builder',
                    'description_zh': '制作三维组态演示，包含工艺仿真、报警联锁和素材导出。',
                    'description_en': 'Build SCADA demos with simulation, alarms and asset export.',
                    'version': '1.1.0',
                    'author': 'HowardChan (Howe829)',
                }
                extra = '\n'.join(f'{key}: {json.dumps(value, ensure_ascii=False)}'
                                  for key, value in metadata.items())
                data = f'---\n{frontmatter}\n{extra}\n---\n{body}'.encode('utf-8')
            archive.writestr(f'{NAME}/{path.relative_to(ROOT)}', data)
    print(output)


if __name__ == '__main__':
    main()
