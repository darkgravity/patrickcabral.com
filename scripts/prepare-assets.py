#!/usr/bin/env python3
"""Create web copies: TIFF sources become PNG; other artwork uses JPEG (macOS sips)."""
import concurrent.futures, json, struct, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/assets/art'
DEST.mkdir(parents=True, exist_ok=True)
files = sorted(p for p in (ROOT / 'art').iterdir() if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'})
def convert(pair):
    i, source = pair
    is_tiff = source.suffix.lower() in {'.tif', '.tiff'}
    extension, image_format = ('png', 'png') if is_tiff else ('jpg', 'jpeg')
    outputs = {}
    for label, size in [('thumb', 720), ('full', 2000)]:
        target = DEST / f'{i:03d}-{label}.{extension}'
        if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
            temporary = target.with_name(f'{target.stem}.tmp.{extension}')
            command = ['sips', '-s', 'format', image_format]
            if not is_tiff:
                command += ['-s', 'formatOptions', '82']
            subprocess.run(command + ['-Z', str(size), str(source), '--out', str(temporary)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            temporary.replace(target)
        if is_tiff:
            with target.open('rb') as image:
                header = image.read(24)
            assert header[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {target}'
            width, height = struct.unpack('>II', header[16:24])
            assert 0 < width <= size and 0 < height <= size, f'Invalid PNG dimensions: {target}'
        outputs[label] = f'assets/art/{target.name}'
    dims = subprocess.check_output(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(DEST / f'{i:03d}-full.{extension}')], text=True)
    values = {line.strip().split(': ')[0]: int(line.strip().split(': ')[1]) for line in dims.splitlines() if ': ' in line}
    thumb_dims = subprocess.check_output(['sips', '-g', 'pixelWidth', str(DEST / f'{i:03d}-thumb.{extension}')], text=True)
    thumb_width = int(thumb_dims.split('pixelWidth: ')[1].strip())
    return {'thumb_width': thumb_width, 'id': i, 'source': str(source.relative_to(ROOT)), **outputs, 'width': values['pixelWidth'], 'height': values['pixelHeight']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    result = list(pool.map(convert, enumerate(files)))
(ROOT / 'src/assets.json').write_text(json.dumps(result, indent=2) + '\n')
for asset in result:
    if Path(asset['source']).suffix.lower() in {'.tif', '.tiff'}:
        for label in ('thumb', 'full'):
            (DEST / f'{asset["id"]:03d}-{label}.jpg').unlink(missing_ok=True)
print(f'Prepared {len(result)} original images in two sizes; {sum(Path(a["source"]).suffix.lower() in {".tif", ".tiff"} for a in result)} TIFF sources use PNG.')
