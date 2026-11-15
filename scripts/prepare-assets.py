#!/usr/bin/env python3
"""Create JPEG thumbnails and web details; TIFF full-size copies remain PNG."""
import concurrent.futures, json, struct, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/assets/art'
DEST.mkdir(parents=True, exist_ok=True)
files = sorted(p for p in (ROOT / 'art').iterdir() if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'})
manifest = ROOT / 'src/assets.json'
existing = json.loads(manifest.read_text()) if manifest.exists() else []
originals = [a for a in existing if a['source'].startswith('art/') and not a.get('source_type')]
if originals and ([a['source'] for a in originals] != [str(p.relative_to(ROOT)) for p in files]
                  or [a['id'] for a in originals] != list(range(len(files)))):
    raise SystemExit('Original files changed. Update their stable asset IDs and project mappings before preparing images.')
def convert(pair):
    i, source = pair
    is_tiff = source.suffix.lower() in {'.tif', '.tiff'}
    outputs = {}
    for label, size in [('thumb', 720), ('full', 2000)]:
        use_png = is_tiff and label == 'full'
        extension, image_format = ('png', 'png') if use_png else ('jpg', 'jpeg')
        target = DEST / f'{i:03d}-{label}.{extension}'
        if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
            temporary = target.with_name(f'{target.stem}.tmp.{extension}')
            command = ['sips', '-s', 'format', image_format]
            if not use_png:
                command += ['-s', 'formatOptions', '82']
            subprocess.run(command + ['-Z', str(size), str(source), '--out', str(temporary)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            temporary.replace(target)
        if use_png:
            with target.open('rb') as image:
                header = image.read(24)
            assert header[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {target}'
            width, height = struct.unpack('>II', header[16:24])
            assert 0 < width <= size and 0 < height <= size, f'Invalid PNG dimensions: {target}'
        outputs[label] = f'assets/art/{target.name}'
    dims = subprocess.check_output(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(DEST / f'{i:03d}-full.{extension}')], text=True)
    values = {line.strip().split(': ')[0]: int(line.strip().split(': ')[1]) for line in dims.splitlines() if ': ' in line}
    thumb_dims = subprocess.check_output(['sips', '-g', 'pixelWidth', str(DEST / f'{i:03d}-thumb.jpg')], text=True)
    thumb_width = int(thumb_dims.split('pixelWidth: ')[1].strip())
    return {'thumb_width': thumb_width, 'id': i, 'source': str(source.relative_to(ROOT)), **outputs, 'width': values['pixelWidth'], 'height': values['pixelHeight']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    result = list(pool.map(convert, enumerate(files)))
# Preserve provenance and appended media when refreshing the originals.
result = [{**(existing[i] if i < len(existing) else {}), **a} for i, a in enumerate(result)]
manifest.write_text(json.dumps(result + existing[len(files):], indent=2, ensure_ascii=False) + '\n')
print(f'Prepared {len(result)} original images with JPEG thumbnails; {sum(Path(a["source"]).suffix.lower() in {".tif", ".tiff"} for a in result)} TIFF sources retain full PNG copies.')
subprocess.run([sys.executable, str(ROOT / 'scripts/prepare-previews.py')], check=True)
