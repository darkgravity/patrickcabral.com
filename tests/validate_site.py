"""Check the complete static portfolio without third-party dependencies."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.references = []
        self.ids = set()
        self.labels = set()
        self.fields = {}
        self.forms = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            assert attrs['id'] not in self.ids, f'Duplicate id in {self.path}: {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ('href', 'src', 'data-full'):
            if attrs.get(key):
                self.references.append(attrs[key])
        if attrs.get('srcset'):
            self.references.extend(item.strip().split()[0] for item in attrs['srcset'].split(',') if item.strip())
        if tag == 'label' and attrs.get('for'):
            self.labels.add(attrs['for'])
        if tag in ('input', 'textarea', 'select') and attrs.get('id'):
            self.fields[attrs['id']] = attrs
        if tag == 'form':
            self.forms.append(attrs)


projects = json.loads((ROOT / 'src/projects.json').read_text())
assets = json.loads((ROOT / 'src/assets.json').read_text())
slugs = [project['slug'] for project in projects]
assert len(slugs) == 64, f'Expected 64 project pages, found {len(slugs)}'
assert len(set(slugs)) == len(slugs), 'Project slugs must be unique'
used = Counter(image for project in projects for image in project['images'])
expected = set(range(100)) - {20}
assert set(used) == expected, f'Image coverage mismatch: missing {expected - set(used)}, unexpected {set(used) - expected}'
assert all(count == 1 for count in used.values()), f'Images must belong to one project: {[i for i, count in used.items() if count != 1]}'
manifest_ids = [asset['id'] for asset in assets]
assert len(manifest_ids) == len(set(manifest_ids)), 'Duplicate asset IDs'
assert set(manifest_ids) == set(range(100)), 'Asset manifest must account for all 100 originals, including excluded blank image 20'
for asset in assets:
    for version in ('thumb', 'full'):
        assert (DOCS / asset[version]).is_file(), f'Missing optimized image: {asset[version]}'
    if Path(asset['source']).suffix.lower() in ('.tif', '.tiff'):
        for version in ('thumb','full'):
            png = DOCS / asset[version]
            assert png.suffix == '.png', f'TIFF web copy is not PNG: {png}'
            with png.open('rb') as stream: assert stream.read(8) == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {png}'
    # Original TIFFs are deliberately excluded from the deployment and CI checkout.
    if (ROOT / 'art').is_dir():
        assert (ROOT / asset['source']).is_file(), f'Missing original: {asset["source"]}'
for project in projects:
    assert project['cover'] in project['images'], f'Cover not part of project: {project["slug"]}'
    assert (DOCS / 'projects' / project['slug'] / 'index.html').is_file(), f'Missing project route: {project["slug"]}'

pages = {path.resolve(): Page(path) for path in DOCS.rglob('*.html')}
reference_count = 0
for path, page in pages.items():
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        decoded = unquote(url.path)
        assert Path(decoded).suffix.lower() not in ('.tif', '.tiff'), f'Original TIFF referenced by {path}: {reference}'
        target = ((DOCS / decoded.lstrip('/')) if decoded.startswith('/') else (path.parent / decoded)).resolve() if decoded else path
        assert target.is_relative_to(DOCS.resolve()), f'Reference escapes deployed directory: {reference}'
        if target.is_dir():
            target /= 'index.html'
        assert target.is_file(), f'Broken reference in {path.relative_to(DOCS)}: {reference}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'Broken fragment in {path.relative_to(DOCS)}: {reference}'
        reference_count += 1

for route in ['portfolio', 'about', 'contact']:
    assert (DOCS / route / 'index.html').resolve() in pages, f'Missing inner page: {route}'
for path, page in pages.items():
    for reference in page.references:
        url = urlsplit(reference)
        if not url.scheme and not url.netloc and url.path:
            assert not url.path.endswith('/'), f'Use explicit index.html for offline navigation: {reference}'

home = pages[(DOCS / 'index.html').resolve()]
assert any(form.get('action') == 'https://formsubmit.co/peacabral@gmail.com' and form.get('method', '').lower() == 'post' for form in home.forms), 'Native contact form endpoint missing'
for field_id in ('contact-name', 'contact-email', 'contact-message'):
    assert field_id in home.labels, f'Missing contact label: {field_id}'
    assert field_id in home.fields and 'required' in home.fields[field_id], f'Required contact field missing: {field_id}'
assert home.fields['contact-email'].get('type') == 'email', 'Contact email needs native email validation'
assert 'contact-project' in home.labels, 'Missing project inquiry label'
contact = pages[(DOCS/'contact/index.html').resolve()]
assert any(form.get('action') == 'https://formsubmit.co/peacabral@gmail.com' for form in contact.forms), 'Contact page form missing'
for field_id in ('contact-name','contact-email','contact-message'):
    assert field_id in contact.labels and 'required' in contact.fields[field_id]
print(f'Passed: {len(projects)} projects, {len(used)} uniquely assigned images, {len(pages)} pages, {reference_count} local references, and native contact form.')
