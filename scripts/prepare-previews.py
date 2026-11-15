#!/usr/bin/env python3
"""Create light JPEG page previews from existing web copies, preserving full images."""
import concurrent.futures
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
MANIFEST = ROOT / 'src/assets.json'


def image_path(relative):
    path = (DOCS / relative).resolve()
    if not path.is_relative_to(DOCS.resolve()):
        raise ValueError(f'Image path escapes docs: {relative}')
    return path


def dimensions(path):
    info = subprocess.check_output(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(path)], text=True)
    return {line.strip().split(': ')[0]: int(line.strip().split(': ')[1])
            for line in info.splitlines() if ': ' in line}


def jpeg_copy(source, target, size=None):
    if source == target:
        raise ValueError(f'Refusing to overwrite source: {source}')
    if not target.exists() or target.stat().st_mtime_ns < source.stat().st_mtime_ns:
        temporary = target.with_name(f'{target.stem}.tmp.jpg')
        command = ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '82']
        if size:
            command += ['-Z', str(size)]
        try:
            subprocess.run(command + [str(source), '--out', str(temporary)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    return dimensions(target)


def prepare(asset):
    asset = dict(asset)
    full = image_path(asset['full'])
    display = full.with_name(full.stem.removesuffix('-full') + '-display.jpg')
    size = min(1400, max(asset['width'], asset['height']))
    dims = jpeg_copy(full, display, size)
    asset.update(display=str(display.relative_to(DOCS)),
                 display_width=dims['pixelWidth'], display_height=dims['pixelHeight'])
    thumb = image_path(asset['thumb'])
    if thumb.suffix.lower() == '.png':
        jpeg = thumb.with_suffix('.jpg')
        dims = jpeg_copy(thumb, jpeg)
        asset.update(thumb=str(jpeg.relative_to(DOCS)), thumb_width=dims['pixelWidth'])
    return asset


def main():
    assets = json.loads(MANIFEST.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(prepare, assets))
    MANIFEST.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(f'Prepared {len(result)} JPEG display previews (up to 1400 px) and lightweight thumbnails; full images unchanged.')


if __name__ == '__main__':
    main()
