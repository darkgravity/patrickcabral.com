const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const app = fs.readFileSync(path.join(__dirname, '../src/app.js'), 'utf8');

function element(properties = {}) {
  const listeners = {};
  const classes = new Set();
  return Object.assign({
    dataset: {}, textContent: '', value: '', hidden: false, attributes: {},
    classList: {
      add: name => classes.add(name),
      remove: name => classes.delete(name),
      contains: name => classes.has(name),
      toggle(name, force) { if (force) classes.add(name); else classes.delete(name); }
    },
    addEventListener(type, listener) { (listeners[type] ||= []).push(listener); },
    dispatch(type, event = {}) { (listeners[type] || []).forEach(fn => fn({ target: this, preventDefault() {}, ...event })); },
    setAttribute(name, value) { this.attributes[name] = value; },
    getAttribute(name) { return this.attributes[name] ?? null; },
    focus() { this.focused = true; },
    querySelector() { return null; }
  }, properties);
}

function run({ stored, dark = false, blocked = false, selectors = {}, lists = {}, query = '' } = {}) {
  const root = element();
  const body = element();
  const document = element({
    documentElement: root, body,
    querySelector: selector => selectors[selector] || null,
    querySelectorAll: selector => lists[selector] || []
  });
  const media = element({ matches: dark });
  const localStorage = {
    getItem() { if (blocked) throw new Error('Blocked'); return stored; },
    setItem(key, value) { if (blocked) throw new Error('Blocked'); stored = value; }
  };
  vm.runInNewContext(app, { document, localStorage, URLSearchParams, window: { matchMedia: () => media, location: { search: query } } });
  return { root, body, media, document, saved: () => stored };
}

{
  const toggle = element();
  const label = element();
  const env = run({ dark: true, selectors: { '#theme-toggle': toggle, '#theme-label': label } });
  assert.equal(env.root.dataset.theme, 'dark');
  assert.equal(label.textContent, 'Auto');
  toggle.dispatch('click');
  assert.equal(env.root.dataset.theme, 'light');
  assert.equal(env.saved(), 'light');
  env.media.matches = true;
  env.media.dispatch('change');
  assert.equal(env.root.dataset.theme, 'light', 'manual theme ignores OS changes');
  toggle.dispatch('click');
  assert.equal(env.root.dataset.theme, 'dark');
  toggle.dispatch('click');
  assert.equal(env.root.dataset.themeMode, 'system');
  env.media.matches = false;
  env.media.dispatch('change');
  assert.equal(env.root.dataset.theme, 'light', 'auto theme tracks OS changes');
}
{
  const toggle = element();
  const env = run({ blocked: true, dark: true, selectors: { '#theme-toggle': toggle } });
  toggle.dispatch('click');
  assert.equal(env.root.dataset.theme, 'light', 'storage failure does not prevent interaction');
  assert.equal(run({ stored: 'unexpected' }).root.dataset.themeMode, 'system');
}
{
  const all = element({ dataset: { filter: 'all' } });
  const culture = element({ dataset: { filter: 'culture' } });
  const search = element();
  const count = element();
  const noResults = element();
  const cards = [
    element({ textContent: 'Starbucks Reserve', dataset: { category: 'sculpture', search: 'Elephant Tiger' } }),
    element({ textContent: 'Langit at Lupa', dataset: { category: 'culture', search: 'Dinagyang masks' } })
  ];
  run({ selectors: { '#project-search': search, '#results-count': count, '#no-results': noResults }, lists: { '[data-filter]': [all, culture], '[data-category]': cards } });
  assert.equal(count.textContent, '2 projects');
  search.value = ' TIGER ';
  search.dispatch('input');
  assert.deepEqual(cards.map(card => card.hidden), [false, true]);
  culture.dispatch('click');
  assert.equal(noResults.hidden, false, 'category and query must both match');
  search.value = 'masks';
  search.dispatch('input');
  assert.equal(count.textContent, '1 project');
  assert.equal(culture.getAttribute('aria-pressed'), 'true');
}
{
  const menu = element();
  const nav = element();
  const env = run({ selectors: { '#menu-toggle': menu, '#site-nav': nav } });
  menu.dispatch('click');
  assert.equal(menu.getAttribute('aria-expanded'), 'true');
  assert.equal(nav.classList.contains('is-open'), true);
  env.document.dispatch('keydown', { key: 'Escape' });
  assert.equal(menu.getAttribute('aria-expanded'), 'false');
  assert.equal(menu.focused, true);
}
{
  const input = element();
  run({ selectors: { '#contact-project': input }, query: '?project=Starbucks%20Reserve%20%26%20Art' });
  assert.equal(input.value, 'Starbucks Reserve & Art');
}
{
  const dialog = element({ showModal() { this.open = true; }, close() { this.open = false; this.dispatch('close'); } });
  const image = element();
  const caption = element();
  const close = element();
  const previous = element();
  const next = element();
  const launches = ['elephant', 'tiger'].map(name => element({
    dataset: { full: `/assets/${name}.jpg`, caption: name },
    querySelector: () => ({ alt: name })
  }));
  const env = run({ selectors: { '#lightbox': dialog, '#lightbox-image': image, '#lightbox-caption': caption, '#lightbox-close': close, '#lightbox-prev': previous, '#lightbox-next': next }, lists: { '[data-lightbox]': launches } });
  launches[0].dispatch('click');
  assert.equal(dialog.open, true);
  assert.equal(image.src, '/assets/elephant.jpg');
  previous.dispatch('click');
  assert.equal(image.src, '/assets/tiger.jpg', 'gallery wraps within the current page');
  dialog.dispatch('keydown', { key: 'ArrowRight' });
  assert.equal(caption.textContent, 'elephant (1 / 2)');
  close.dispatch('click');
  assert.equal(env.body.classList.contains('modal-open'), false);
  assert.equal(launches[0].focused, true, 'focus returns to the opening image');
  launches[1].dispatch('click');
  const inner = element();
  inner.classList.add('lightbox-inner');
  dialog.dispatch('click', { target: inner });
  assert.equal(dialog.open, false, 'clicking empty inner backdrop closes the lightbox');
}
console.log('Passed: themes, blocked storage, filtering, menu, contact context, lightbox.');
