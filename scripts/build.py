#!/usr/bin/env python3
"""Render the portfolio into docs/, ready for GitHub Pages. No build dependencies."""
from pathlib import Path
from html import escape as e
from urllib.parse import quote
import json, shutil
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
ASSETS = json.loads((ROOT / 'src/assets.json').read_text())
PROJECTS = json.loads((ROOT / 'src/projects.json').read_text())
WORKS = [p for p in PROJECTS if p['category'] != 'experiments' and not p.get('archived')]
LAB = [p for p in PROJECTS if p['category'] == 'experiments' and not p.get('archived')]
LAB_ORDER = ['pattern-dance','techsugi-panels','quantum-dance','grown','patterned-figures','ribbed-organic-form','chromatic-form','pattern-field','cypher']
LAB.sort(key=lambda p: LAB_ORDER.index(p['slug']) if p['slug'] in LAB_ORDER else len(LAB_ORDER))
CATEGORIES = {'sculpture': 'Sculpture', 'culture': 'Culture & heritage', 'experiments': 'Digital explorations', 'lettering': 'Lettering & form'}
FAN = '<svg class="fan" viewBox="0 0 100 50" aria-hidden="true" fill="none" stroke="currentColor" stroke-width=".65">' + ''.join(f'<path d="M50 47L{x} {y}"/>' for x,y in [(2,44),(5,33),(10,23),(18,14),(28,7),(39,3),(50,1),(61,3),(72,7),(82,14),(90,23),(95,33),(98,44)]) + '<path d="M30 47a20 20 0 0 1 40 0Z" fill="var(--bg)"/></svg>'
THEME = """<script>try{let m=localStorage.getItem('pc-theme');document.documentElement.dataset.theme=m==='light'||m==='dark'?m:matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}catch(e){document.documentElement.dataset.theme=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}</script>"""
def image(i, base='', alt='', large=False, eager=False, cls='', sizes='(max-width: 600px) calc(100vw - 36px), (max-width: 900px) calc(100vw - 48px), (max-width: 1276px) calc(100vw - 96px), 1180px'):
    a=ASSETS[i]
    path=a['display' if large else 'thumb']
    # Small previews never offer the full image, even on high-density screens.
    responsive = f' srcset="{base}{a["thumb"]} {a["thumb_width"]}w, {base}{a["display"]} {a["display_width"]}w" sizes="{sizes}"' if large and a['display_width'] > a['thumb_width'] else ''
    return f'<img class="{cls}" src="{base}{path}"{responsive} width="{a["width"]}" height="{a["height"]}" alt="{e(alt)}" loading="{("eager" if eager else "lazy")}" decoding="async" {("fetchpriority=high" if eager else "")}>'
def header(base, active=""):
    nav = "".join(f'<a href="{base}{route}/index.html"' + (' aria-current="page"' if route == active else '') + f'>{label}</a>' for route,label in [("portfolio","Works"),("lab","Lab"),("about","About"),("contact","Contact")])
    return f'''<a class="skip-link" href="#main">Skip to content</a><header class="site-header container"><a class="wordmark" href="{base}index.html" aria-label="Patrick Cabral home">Patrick Cabral</a><button class="menu-button" id="menu-toggle" aria-controls="site-nav" aria-expanded="false">Menu</button><nav class="site-nav" id="site-nav" aria-label="Main navigation">{nav}</nav><button id="theme-toggle" class="theme-button" aria-label="Color theme: system. Switch to light mode"><span class="sun" aria-hidden="true">☼</span><span id="theme-label">Auto</span></button></header>'''
def footer(base):
    return f'''<footer class="site-footer"><div class="container footer-inner"><a class="wordmark" href="{base}index.html">Patrick Cabral</a><p>© <span class="year">2026</span> Patrick Cabral. All artwork rights reserved.</p><div class="footer-links"><a href="https://www.instagram.com/darkgravity/" target="_blank" rel="noopener noreferrer">Instagram</a><a href="mailto:peacabral@gmail.com">Email</a><a href="#top">Back to top</a></div></div></footer>'''
def document(title, description, content, base='', social=8, active=''):
    return f'''<!doctype html><html lang="en" id="top"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="color-scheme" content="light dark"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:image" content="{base}{ASSETS[social]['full']}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{THEME}<link rel="stylesheet" href="{base}assets/styles.css"><script defer src="{base}assets/app.js"></script></head><body>{header(base, active)}{content}{footer(base)}</body></html>'''
def card(p, base=''):
    series = p.get('series', CATEGORIES[p['category']])
    search = ' '.join([p['description'], p.get('context',''), p['medium'], series])
    return f'''<article class="work-card" data-category="{p['category']}" data-search="{e(search)}"><a href="{base}projects/{p['slug']}/index.html"><div class="work-image">{image(p['cover'],base,p['alt'])}</div><div class="work-caption"><div><h3>{e(p['title'])}</h3><p>{e(series)}</p></div><span class="project-link-label" aria-hidden="true"><svg viewBox="0 0 28 16" fill="none" focusable="false"><path d="M1 8h24M19 2l6 6-6 6" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg></span></div></a></article>'''
def write(path, text):
    path=OUT/path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
def home():
    selected=[PROJECTS[0]] + [next(p for p in PROJECTS if p['slug']==s) for s in ['manaoag','langit-at-lupa','roosters-in-colour','parol','madonna-and-child','crowned-lion','owl']]
    lab_selected=[next(p for p in LAB if p['slug']==slug) for slug in ['pattern-dance','techsugi-panels','quantum-dance','chromatic-form']]
    content=f'''<main id="main"><section class="hero" aria-labelledby="hero-title"><img class="ornament left" src="assets/ornament.png" alt="" width="950" height="869"><img class="ornament right" src="assets/ornament.png" alt="" width="950" height="869"><div class="hero-content">{FAN}<h1 id="hero-title">Patrick Cabral</h1><p class="hero-tagline">Paper sculpture. Digital experiments.</p><p class="eyebrow">Artist & technologist · Philippines</p><div class="hero-links"><a class="text-link" href="portfolio/index.html">Explore the sculptures</a><a class="text-link" href="lab/index.html">Explore the Lab</a></div><a class="hero-art" href="projects/starbucks-reserve/index.html" aria-label="Explore the Starbucks Reserve project">{image(8,alt='Elephant, tiger and quetzal sculptures installed at Starbucks Reserve, SM North Towers',large=True,eager=True,sizes='(min-width: 1600px) 900px, (max-width: 600px) calc(100vw - 50px), (max-width: 900px) calc(100vw - 122px), 850px')}</a><p class="eyebrow feature-label">Featured collaboration · Starbucks</p><h2><a href="projects/starbucks-reserve/index.html">Stories of origin, layer by layer.</a></h2><p class="hero-description">Three coffee-growing regions. Three extraordinary animals.<br>A sculptural collection for Starbucks Reserve.</p><a class="text-link" href="projects/starbucks-reserve/index.html">Discover the collaboration</a></div></section>
<section class="section container" id="selected-work"><div class="section-heading"><h2>Selected sculptures</h2></div><p class="section-intro">Paper sculpture and layered commissions, shaped by nature, cultural memory, and an attention to detail.</p><div class="selected-grid">{''.join(card(p) for p in selected)}</div><div class="center archive-link"><a class="text-link" href="portfolio/index.html">Explore all {len(WORKS)} works</a></div></section>
<section class="section container" id="lab" aria-labelledby="lab-title"><div class="section-heading"><h2 id="lab-title">Technology & possibility</h2></div><p class="section-intro">Custom algorithms exploring craft, culture, and organic form. Weaving, basketry, and textiles become code-driven visual experiments.</p><div class="selected-grid">{''.join(card(p) for p in lab_selected)}</div><div class="center archive-link"><a class="text-link" href="lab/index.html">Explore the Lab</a></div></section>
<section class="section about" id="about"><div class="container about-inner"><div class="about-photo">{image(74,alt='Patrick Cabral seated in front of his Starbucks Reserve sculptures',large=True,sizes='(max-width: 600px) calc(100vw - 62px), 500px')}</div><div class="about-text"><p class="eyebrow">The artist</p><h2>A fascination<br>with the <em>smallest<br>of details.</em></h2><p>Patrick Cabral is a Filipino artist and technologist working across intricate paper sculpture, generative tools, and digital experimentation.</p><p>His work brings the natural world into conversation with Filipino culture. Delicate patterns become dimensional forms; familiar animals and cultural symbols become an invitation to look closer.</p><p>From hand-cut paper to computational studies, each medium offers another way to explore form, rhythm, and possibility.</p><a class="text-link" href="about/index.html">More about the artist</a></div></div></section>
<section class="section container craft-strip"><div>{image(84,alt='Close-up of the intricately layered Starbucks tiger sculpture',large=True,sizes='(max-width: 600px) calc(100vw - 36px), 650px')}</div><div><p class="eyebrow">A closer look</p><h2>There is a world<br><em>within the detail.</em></h2><p>A line becomes a pattern. A pattern becomes a layer. Together, they become something you can almost feel before you touch it.</p><a class="text-link" href="projects/starbucks-reserve/index.html">Explore the details</a></div></section>
<section class="section contact" id="contact"><div class="container contact-inner"><div class="contact-copy"><p class="eyebrow">Commissions · Collaborations · Inquiries</p><h2 class="contact-heading">Let’s make<br>something<br><em>extraordinary.</em></h2><p>For artwork inquiries, commissions, exhibitions, or a conversation about an idea, leave a note.</p><a class="contact-email" href="mailto:peacabral@gmail.com">peacabral@gmail.com</a></div><form class="contact-form" action="https://formsubmit.co/peacabral@gmail.com" method="POST"><input type="hidden" name="_subject" value="New inquiry · Patrick Cabral website"><input type="hidden" name="_template" value="table"><div class="honeypot" aria-hidden="true"><label>Leave this empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div><div class="field"><label for="contact-name">Your name *</label><input id="contact-name" name="name" autocomplete="name" required maxlength="120" placeholder="Full name"></div><div class="field"><label for="contact-email">Email address *</label><input id="contact-email" name="email" autocomplete="email" type="email" required maxlength="200" placeholder="you@example.com"></div><div class="field full"><label for="contact-project">Project or subject</label><input id="contact-project" name="project" maxlength="160" placeholder="What do you have in mind?"></div><div class="field full"><label for="contact-message">Your message *</label><textarea id="contact-message" name="message" required maxlength="6000" rows="4" placeholder="Tell me a little about your idea…"></textarea></div><div class="field full"><button class="submit-button" type="submit">Send inquiry</button><p class="form-note">Your name, email, and message are sent securely through <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">FormSubmit</a> to Patrick’s inbox. You’ll complete a spam check on the next page.</p></div></form></div></section></main>'''
    write(Path('index.html'),document('Patrick Cabral | Paper Sculpture & Technology','Paper sculpture and technology by Filipino artist Patrick Cabral. Explore intricate layered works alongside generative surfaces, procedural motion, and digital experiments.',content))
def archive(route, projects):
    base='../'
    is_lab = route == 'lab'
    label = 'Lab' if is_lab else 'Works'
    heading = 'Algorithms for craft and culture.' if is_lab else 'A world of detail.'
    intro = ('Visual experiments exploring organic forms, traditional crafts, and Philippine culture through computation. Patrick creates algorithms that translate weaving, basketry, tattooing, and beadwork into new digital forms.<br><br>These are code-driven works, not AI-generated visuals.' if is_lab else 'Paper sculptures and layered commissions, shaped by nature, pattern, and cultural memory.<br>Explore each work, from the full composition to its smallest details.')
    categories = {k:v for k,v in CATEGORIES.items() if any(p['category']==k for p in projects)}
    all_label = 'All experiments' if is_lab else 'All work'
    filters = ''.join(f'<button class="filter" data-filter="{k}" aria-pressed="{str(k=="all").lower()}">{v}</button>' for k,v in {'all':all_label,**(categories if len(categories)>1 else {})}.items())
    other_route, other_label = ('portfolio', 'Explore the works') if is_lab else ('lab', 'Explore the Lab')
    content=f'''<main class="container" id="main"><section class="page-title">{FAN}<p class="eyebrow">{label} · {('Technology & digital experiments' if is_lab else 'Paper & layered sculpture')}</p><h1>{heading}</h1><p>{intro}</p><a class="text-link" href="{base}{other_route}/index.html">{other_label}</a></section><div class="archive-controls"><div class="filters" role="group" aria-label="Filter projects">{filters}</div><label><span class="eyebrow">Search </span><input class="search" id="project-search" type="search" placeholder="{('Find an experiment…' if is_lab else 'Find a work…')}" aria-label="Search {label.lower()}"></label></div><p class="archive-count" id="results-count" role="status" aria-live="polite">{len(projects)} projects</p><p class="no-results" id="no-results" hidden>No projects match that search. Try another word or choose {all_label}.</p><div class="archive-grid">{''.join(card(p,base) for p in projects)}</div></main>'''
    description = 'Explore Patrick Cabral’s code-driven experiments in Philippine weaving, basketry, tattoo patterns, beadwork, and procedural textiles.' if is_lab else 'Explore Patrick Cabral’s paper sculptures, layered commissions, and cultural works.'
    write(Path(f'{route}/index.html'),document(f'{label} | Patrick Cabral',description,content,base,social=projects[0]['cover'],active=route))
def lightbox():
    return '''<dialog class="lightbox" id="lightbox" aria-label="Artwork image viewer"><button class="lightbox-close" id="lightbox-close" aria-label="Close image viewer">×</button><div class="lightbox-inner"><img id="lightbox-image" alt=""><p id="lightbox-caption" aria-live="polite"></p></div><button class="lightbox-prev" id="lightbox-prev" aria-label="Previous image">‹</button><button class="lightbox-next" id="lightbox-next" aria-label="Next image">›</button></dialog>'''
def photo(p,i,n,base,main=False,total=None,eager=False):
    caption=p.get('captions',{}).get(str(i),p['title'] + (' · full composition' if n==0 else f' · view {n+1}'))
    count=len(p['images']) if total is None else total
    return f'''<figure{(' class="project-main-figure"' if main else '')}><button class="zoom-image {('project-main' if main else '')}" data-lightbox data-full="{base}{ASSETS[i]['full']}" data-caption="{e(caption)}" aria-label="Enlarge {e(caption)}">{image(i,base,caption,large=main,eager=eager)}</button><figcaption class="image-caption"><span>{e(caption)}</span><span>{n+1:02d} / {count:02d}</span></figcaption></figure>'''
def films(p, base):
    if not p.get('videos'):
        return ''
    posters = {a['full']: a['thumb'] for a in ASSETS}
    items = ''.join(f'''<figure><video controls preload="none" playsinline poster="{base}{e(posters.get(v['poster'], v['poster']))}" aria-label="{e(v['title'])}"><source src="{base}{e(v['src'])}" type="video/mp4">Your browser does not support embedded video. <a href="{base}{e(v['src'])}">Open the film</a>.</video><figcaption class="image-caption"><span>{e(v['title'])}</span><a href="{base}{e(v['src'])}">Open film</a></figcaption></figure>''' for v in p['videos'])
    return f'<section class="project-films" aria-labelledby="films-title"><h2 id="films-title">Studies in motion</h2>{items}</section>'
def project(p):
    base='../../'
    photos=p['images']
    is_lab = p['category'] == 'experiments'
    collection = LAB if is_lab else WORKS
    route, label = ('lab', 'Lab') if is_lab else ('portfolio', 'Works')
    navigation = ''
    if not p.get('archived'):
        idx = collection.index(p)
        prev=collection[(idx-1)%len(collection)]; nxt=collection[(idx+1)%len(collection)]
        navigation = f'<nav class="project-nav" aria-label="Adjacent projects"><a href="../{prev["slug"]}/index.html">Previous project<strong>{e(prev["title"])}</strong></a><a href="../{nxt["slug"]}/index.html">Next project<strong>{e(nxt["title"])}</strong></a></nav>'
    sources=''
    if p.get('sources'):
        sources='<details class="project-sources"><summary>Project reading & context</summary>' + ''.join(f'<p><a href="{e(s[1])}" target="_blank" rel="noopener noreferrer">{e(s[0])}</a></p>' for s in p['sources']) + '</details>'
    metadata = ''.join(f'<div><span>{label}</span>{e(str(p[key]))}</div>' for key,label in [('commission','Commission'),('year','Year'),('dimensions','Dimensions'),('series','Series')] if p.get(key))
    section_images = {section['image'] for section in p.get('study_sections', [])}
    studies = ''.join(f'<section class="project-study"><h2>{e(section["title"])}</h2><p>{e(section["description"])}</p>{photo(p,section["image"],0,base,main=True,total=1)}</section>' for section in p.get('study_sections', []))
    if p.get('videos'):
        primary_media = films(p,base)
        posters = {v['poster'] for v in p['videos']}
        stills = [i for i in photos if ASSETS[i]['full'] not in posters and i not in section_images]
        gallery = ''.join(photo(p,i,n,base,total=len(stills)) for n,i in enumerate(stills))
    else:
        primary_media = photo(p,photos[0],0,base,main=True,eager=True)
        gallery = ''.join(photo(p,i,n,base) for n,i in enumerate(photos) if n>0)
    content=f'''<main id="main" class="container"><p class="breadcrumb"><a href="{base}{route}/index.html">{label}</a> / {e(p['title'])}</p><section class="project-intro"><div><p class="eyebrow">{("Archive · " if p.get("archived") else "")}{e(CATEGORIES[p['category']])}</p><h1>{e(p['title'])}</h1><div class="project-meta"><div><span>Practice</span>{e(p['medium'])}</div><div><span>Artist</span>Patrick Cabral</div>{metadata}</div></div><div class="project-description"><p>{e(p['description'])}</p>{('<p>'+e(p['context'])+'</p>' if p.get('context') else '')}<a class="text-link" href="{base}contact/index.html?project={quote(p['title'])}">Inquire about this work</a></div></section>{primary_media}<div class="project-gallery">{gallery}</div>{studies}{sources}<div class="project-bottom"><p class="eyebrow">{('New tools. New ways of seeing.' if is_lab else 'Look closer. Every layer has a story.')}</p><a class="text-link" href="https://www.instagram.com/darkgravity/" target="_blank" rel="noopener noreferrer">More from the studio on Instagram</a></div>{navigation}</main>{lightbox()}'''
    write(Path(f'projects/{p["slug"]}/index.html'),document(f'{p["title"]} | Patrick Cabral',p['description'],content,base,p['cover'],active=route))
def main():
    for filename in ['styles.css','app.js']:
        shutil.copy2(ROOT/'src'/filename,OUT/'assets'/filename)
    (OUT/'.nojekyll').touch()
    write(Path('assets/favicon.svg'),'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#392e25"/><text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-size="35" fill="#f5f0e7">P</text></svg>')
    current = {p['slug'] for p in PROJECTS}
    for old in (OUT/'projects').iterdir() if (OUT/'projects').exists() else []:
        if old.is_dir() and old.name not in current: shutil.rmtree(old)
    home(); archive('portfolio', WORKS); archive('lab', LAB)
    write(Path('work/index.html'), '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../portfolio/index.html"><title>Works | Patrick Cabral</title></head><body><a href="../portfolio/index.html">Explore the works</a></body></html>')
    for name,title,description in [('about','About Patrick Cabral','Meet Filipino artist Patrick Cabral and explore his approach to layered sculpture, nature, culture, and technology.'),('contact','Contact Patrick Cabral','Contact Patrick Cabral for artwork inquiries, commissions, collaborations, exhibitions, and press.')]:
        content = (ROOT/'src'/f'{name}.html').read_text().replace('{{BASE}}','../')
        if name == 'about':
            content = content.replace('{{ARTIST_IMAGE}}', image(74,'../','Patrick Cabral seated in front of his sculptures at Starbucks Reserve',large=True,eager=True,sizes='(max-width: 600px) calc(100vw - 62px), 500px'))
            content = content.replace('{{DETAIL_IMAGE}}', image(84,'../','Close view of the patterned layers surrounding the eye of the Starbucks Reserve tiger',large=True,sizes='(max-width: 600px) calc(100vw - 36px), 650px'))
        write(Path(f'{name}/index.html'),document(title,description,content,'../',active=name))
    for p in PROJECTS: project(p)
    print(f'Built Home, Works, Lab, About, Contact, and {len(PROJECTS)} project pages.')
if __name__=='__main__': main()
