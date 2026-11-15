"""Check the complete static portfolio without third-party dependencies."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
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
        self.videos = []
        self.images = []
        self.image_sources = []
        self.links = []
        self.stack = []
        markup = path.read_text()
        for private_host in ('mail.google.com', 'mail-attachment.googleusercontent.com'):
            assert private_host not in unquote(markup).lower(), f'Private mail URL rendered in {path}'
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            assert attrs['id'] not in self.ids, f'Duplicate id in {self.path}: {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ('href', 'src', 'poster', 'data-full'):
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
        if tag == 'video':
            assert 'controls' in attrs, f'Video needs playback controls: {self.path}'
            assert attrs.get('preload') in ('none', 'metadata'), f'Video must avoid full preload: {self.path}'
            assert 'autoplay' not in attrs, f'Video must not autoplay: {self.path}'
            self.videos.append(attrs)
        if tag == 'img':
            self.images.append({'attrs': attrs, 'parents': self.stack[:]})
            if attrs.get('src') and 'hidden' not in attrs and all('hidden' not in parent for _, parent in self.stack):
                self.image_sources.append(attrs['src'])
        if tag == 'a':
            self.links.append({'attrs': attrs, 'parents': self.stack[:], 'text': '', 'svgs': []})
        if tag == 'svg' and self.links and any(parent == 'a' for parent, _ in self.stack):
            self.links[-1]['svgs'].append({'attrs': attrs, 'decorative': attrs.get('aria-hidden') == 'true' or any(parent.get('aria-hidden') == 'true' for _, parent in self.stack)})
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.links and any(tag == 'a' for tag, _ in self.stack):
            self.links[-1]['text'] += data

    def links_within(self, *, element_id=None, css_class=None):
        return [link for link in self.links if any(
            (element_id and attrs.get('id') == element_id)
            or (css_class and css_class in attrs.get('class', '').split())
            for _, attrs in link['parents'])]


projects = json.loads((ROOT / 'src/projects.json').read_text())
assets = json.loads((ROOT / 'src/assets.json').read_text())
slugs = [project['slug'] for project in projects]
assert len(slugs) >= 74, f'Expected at least 74 project pages, found {len(slugs)}'
assert len(set(slugs)) == len(slugs), 'Project slugs must be unique'
used = Counter(image for project in projects for image in project['images'])
original_ids = set(range(100))
expected_originals = original_ids - {20}
assert set(used) & original_ids == expected_originals, f'Original image coverage mismatch: missing {expected_originals - set(used)}, unexpected {(set(used) & original_ids) - expected_originals}'
assert all(count == 1 for count in used.values()), f'Images must belong to one project: {[i for i, count in used.items() if count != 1]}'
manifest_ids = [asset['id'] for asset in assets]
assert len(manifest_ids) == len(set(manifest_ids)), 'Duplicate asset IDs'
assert original_ids <= set(manifest_ids), 'Asset manifest must preserve all 100 originals, including excluded blank image 20'
assert manifest_ids == list(range(len(assets))), 'Asset IDs must match their list positions; append new assets without shifting original IDs'
expected = set(manifest_ids) - {20}
assert set(used) == expected, f'Image coverage mismatch: missing {expected - set(used)}, unexpected {set(used) - expected}'
assert len(used) >= 126, 'Existing artwork, Techsugi, and artist-supplied images must remain preserved'
for asset in assets:
    for version in ('thumb', 'display', 'full'):
        image_path = (DOCS / asset[version]).resolve()
        assert image_path.is_relative_to(DOCS.resolve()), f'Optimized image escapes deployed directory: {asset[version]}'
        assert image_path.is_file(), f'Missing optimized image: {asset[version]}'
        if version != 'full':
            assert image_path.suffix.lower() in ('.jpg', '.jpeg'), f'Preview must use lightweight JPEG: {image_path}'
            with image_path.open('rb') as stream: assert stream.read(2) == b'\xff\xd8', f'Invalid JPEG: {image_path}'
    assert 0 < asset['display_width'] <= min(1400, asset['width']), f'Invalid display width: {asset["id"]}'
    assert 0 < asset['display_height'] <= min(1400, asset['height']), f'Invalid display height: {asset["id"]}'
    if Path(asset['source']).suffix.lower() in ('.tif', '.tiff'):
        png = DOCS / asset['full']
        assert png.suffix == '.png', f'TIFF full-size copy is not PNG: {png}'
        with png.open('rb') as stream: assert stream.read(8) == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {png}'
    if asset['id'] >= 100:
        if asset.get('source_type') == 'techsugi':
            source = Path(asset['source'])
            assert not source.is_absolute() and '..' not in source.parts and len(source.parts) > 1 and source.parts[0] == 'techsugi', f'Invalid Techsugi source path: {asset["source"]}'
        elif asset.get('source_type') == 'user-supplied':
            source = Path(asset['source'])
            allowed_folder = len(source.parts) > 1 and (source.parts[0] == 'Galleon' or (len(source.parts) == 3 and source.parts[:2] == ('art', 'Manaoag')))
            assert not source.is_absolute() and '..' not in source.parts and allowed_folder and source.suffix.lower() in ('.png', '.jpg', '.jpeg'), f'Invalid artist-supplied image path: {asset["source"]}'
        else:
            source = urlsplit(asset['source'])
            assert source.scheme == 'https' and source.hostname in ('instagram.com', 'www.instagram.com'), f'Additional image needs an Instagram, Techsugi, or artist-supplied source: {asset["id"]}'
            assert '/p/' in source.path or '/reel/' in source.path, f'Additional image source must identify a post: {asset["id"]}'
    # Original TIFFs are deliberately excluded from the deployment and CI checkout.
    elif (ROOT / 'art').is_dir():
        assert (ROOT / asset['source']).is_file(), f'Missing original: {asset["source"]}'
for project in projects:
    assert project['cover'] in project['images'], f'Cover not part of project: {project["slug"]}'
    assert (DOCS / 'projects' / project['slug'] / 'index.html').is_file(), f'Missing project route: {project["slug"]}'

pages = {path.resolve(): Page(path) for path in DOCS.rglob('*.html')}
full_paths = {(DOCS / asset['full']).resolve() for asset in assets}
thumb_paths = {(DOCS / asset['thumb']).resolve() for asset in assets}
preview_paths = thumb_paths | {(DOCS / asset['display']).resolve() for asset in assets}
poster_thumbs = {asset['full']: asset['thumb'] for asset in assets}
for page in pages.values():
    eager_images = []
    for image in page.images:
        attrs, parents = image['attrs'], image['parents']
        candidates = ([attrs['src']] if attrs.get('src') else []) + [item.strip().split()[0] for item in attrs.get('srcset', '').split(',') if item.strip()]
        requested = {(page.path.parent / urlsplit(candidate).path).resolve() for candidate in candidates}
        assert not requested & full_paths, f'Full-size artwork loads before zoom: {page.path}'
        if attrs.get('id') == 'lightbox-image':
            assert not candidates, f'Lightbox must not request an image before opening: {page.path}'
        if not requested & preview_paths:
            continue
        classes = {name for _, parent in parents for name in parent.get('class', '').split()}
        if 'work-card' in classes or ('project-gallery' in classes and 'project-main' not in classes):
            assert requested <= thumb_paths, f'Card or gallery offers a larger image than its thumbnail: {page.path}'
            assert attrs.get('loading') == 'lazy', f'Thumbnail must load lazily: {page.path}'
        assert attrs.get('loading') in ('lazy', 'eager'), f'Artwork needs an explicit loading policy: {page.path}'
        if attrs['loading'] == 'eager':
            eager_images.append(image)
    assert len(eager_images) <= 1, f'Only one primary image may load eagerly: {page.path}'
    for video in page.videos:
        poster = (page.path.parent / urlsplit(video.get('poster', '')).path).resolve()
        assert poster in thumb_paths, f'Video poster must use a thumbnail: {page.path}'
for project in projects:
    page = pages[(DOCS / 'projects' / project['slug'] / 'index.html').resolve()]
    videos = project.get('videos', [])
    assert len(page.videos) == len(videos), f'Video count mismatch: {project["slug"]}'
    referenced = {(page.path.parent / urlsplit(reference).path).resolve() for reference in page.references if not urlsplit(reference).scheme and not urlsplit(reference).netloc}
    for video, rendered in zip(videos, page.videos):
        for key in ('src', 'poster'):
            media = Path(video[key])
            assert not media.is_absolute() and '..' not in media.parts, f'Video media path must be relative to docs: {media}'
            target = (DOCS / media).resolve()
            assert target.is_relative_to(DOCS.resolve()) and target.is_file(), f'Missing video media: {media}'
            if key == 'poster':
                expected_poster = (DOCS / poster_thumbs[video['poster']]).resolve()
                actual_poster = (page.path.parent / urlsplit(rendered['poster']).path).resolve()
                assert actual_poster == expected_poster, f'Wrong video thumbnail for {project["slug"]}'
            else:
                assert target in referenced, f'Video media not rendered for {project["slug"]}: {media}'
    displayed_images = {(page.path.parent / urlsplit(source).path).resolve() for source in page.image_sources}
    for study in project.get('study_sections', []):
        image = study['image']
        assert image in project['images'], f'Study image must belong to project: {project["slug"]}'
        assert any((DOCS / assets[image][version]).resolve() in displayed_images for version in ('display', 'thumb')), f'Study image not rendered for {project["slug"]}: {image}'
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

for route in ['portfolio', 'lab', 'about', 'contact']:
    assert (DOCS / route / 'index.html').resolve() in pages, f'Missing inner page: {route}'
for path, page in pages.items():
    for reference in page.references:
        url = urlsplit(reference)
        if not url.scheme and not url.netloc and url.path:
            assert not url.path.endswith('/'), f'Use explicit index.html for offline navigation: {reference}'

home = pages[(DOCS / 'index.html').resolve()]
collections = {
    'portfolio': {p['slug'] for p in projects if p['category'] != 'experiments' and not p.get('archived')},
    'lab': {p['slug'] for p in projects if p['category'] == 'experiments' and not p.get('archived')},
}
archived = {p['slug'] for p in projects if p.get('archived')}
assert archived == {'lettering-in-relief', 'white-lettering', 'calligraphic-monogram'}, 'Keep the three older lettering projects archived'
assert len(collections['portfolio']) >= 49 and len(collections['lab']) >= 22


def destination(page, link):
    return (page.path.parent / urlsplit(link['attrs']['href']).path).resolve()


archived_paths = {(DOCS / 'projects' / slug / 'index.html').resolve() for slug in archived}
for path, page in pages.items():
    if path in archived_paths:
        assert not page.links_within(css_class='project-nav'), f'Archived projects should not have adjacent-project navigation: {path}'
        continue
    for link in page.links:
        url = urlsplit(link['attrs']['href'])
        if not url.scheme and not url.netloc:
            assert destination(page, link) not in archived_paths, f'Archived lettering promoted on {path}: {link["attrs"]["href"]}'


for page in pages.values():
    if 'site-nav' not in page.ids:
        assert page.path == DOCS / 'work/index.html', f'Missing main navigation: {page.path}'
        continue
    nav = page.links_within(element_id='site-nav')
    for label, route in [('Works', 'portfolio'), ('Lab', 'lab')]:
        matching = [link for link in nav if link['text'] == label]
        assert len(matching) == 1, f'Missing or duplicate {label} navigation on {page.path}'
        assert destination(page, matching[0]) == (DOCS / route / 'index.html').resolve()
    for card in page.links_within(css_class='work-card'):
        project = next(p for p in projects if p['slug'] == destination(page, card).parent.name)
        accessible_name = card['attrs'].get('aria-label', card['text'])
        assert project['title'] in accessible_name, f'Card link must retain its project name: {project["slug"]}'
        assert 'view project' not in card['text'].lower(), f'Old card action text remains: {project["slug"]}'
        assert not re.search(r'\b\d+\s+(?:views?|films?)\b', card['text'], re.I), f'Card media count remains: {project["slug"]}'
        assert len(card['svgs']) == 1 and card['svgs'][0]['decorative'], f'Card arrow must be a decorative SVG: {project["slug"]}'

for route, members in collections.items():
    page = pages[(DOCS / route / 'index.html').resolve()]
    cards = page.links_within(css_class='work-card')
    assert len(cards) == len(members), f'Incorrect card count on {route}'
    assert {destination(page, link).parent.name for link in cards} == members, f'Incorrect projects on {route}'
    for slug in members:
        project_page = pages[(DOCS / 'projects' / slug / 'index.html').resolve()]
        breadcrumb = project_page.links_within(css_class='breadcrumb')
        assert len(breadcrumb) == 1 and destination(project_page, breadcrumb[0]) == page.path.resolve(), f'Wrong collection breadcrumb: {slug}'
        current = [link for link in project_page.links_within(element_id='site-nav') if link['attrs'].get('aria-current') == 'page']
        assert len(current) == 1 and destination(project_page, current[0]) == page.path.resolve(), f'Wrong active collection: {slug}'
        adjacent = project_page.links_within(css_class='project-nav')
        assert len(adjacent) == 2 and all(destination(project_page, link).parent.name in members for link in adjacent), f'Adjacent projects cross collections: {slug}'

selected = home.links_within(element_id='selected-work')
selected_projects = [destination(home, link).parent.name for link in selected if '/projects/' in str(destination(home, link))]
assert selected_projects and set(selected_projects) <= collections['portfolio'], 'Selected works must contain sculptures only'
assert 'manaoag' in selected_projects[:2], 'Our Lady of Manaoag must appear in the first row of selected sculptures'
lab_teaser = home.links_within(element_id='lab')
assert any(destination(home, link) == (DOCS / 'lab/index.html').resolve() for link in lab_teaser), 'Homepage needs a separate Lab link'
featured_lab = {destination(home, link).parent.name for link in lab_teaser if destination(home, link).parent.name in collections['lab']}
assert {'pattern-dance', 'techsugi-panels', 'quantum-dance', 'chromatic-form'} <= featured_lab, 'Homepage must highlight the selected technology studies'

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
