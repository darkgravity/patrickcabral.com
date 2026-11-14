(() => {
  'use strict';

  const root = document.documentElement;
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
  const modes = ['system', 'light', 'dark'];
  let mode = 'system';
  try {
    const stored = localStorage.getItem('pc-theme');
    if (modes.includes(stored)) mode = stored;
  } catch (_) { /* Private browsing can make storage unavailable. */ }

  const themeButton = document.querySelector('#theme-toggle');
  const themeLabel = document.querySelector('#theme-label');
  function applyTheme() {
    root.dataset.theme = mode === 'system' ? (systemTheme.matches ? 'dark' : 'light') : mode;
    root.dataset.themeMode = mode;
    const next = modes[(modes.indexOf(mode) + 1) % modes.length];
    if (themeLabel) themeLabel.textContent = mode === 'system' ? 'Auto' : mode[0].toUpperCase() + mode.slice(1);
    if (themeButton) {
      const label = `Color theme: ${mode}. Switch to ${next} mode`;
      themeButton.setAttribute('aria-label', label);
      themeButton.title = label;
    }
  }
  applyTheme();
  themeButton?.addEventListener('click', () => {
    mode = modes[(modes.indexOf(mode) + 1) % modes.length];
    try { localStorage.setItem('pc-theme', mode); } catch (_) { /* Keep the current tab usable. */ }
    applyTheme();
  });
  systemTheme.addEventListener('change', () => {
    if (mode === 'system') applyTheme();
  });

  const menuButton = document.querySelector('#menu-toggle');
  const navigation = document.querySelector('#site-nav');
  function setMenu(open) {
    menuButton?.setAttribute('aria-expanded', String(open));
    navigation?.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);
  }
  menuButton?.addEventListener('click', () => {
    setMenu(menuButton.getAttribute('aria-expanded') !== 'true');
  });
  navigation?.addEventListener('click', event => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      menuButton.focus();
    }
  });

  const filters = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('[data-category]')];
  const search = document.querySelector('#project-search');
  const count = document.querySelector('#results-count');
  const noResults = document.querySelector('#no-results');
  let category = 'all';
  function filterProjects() {
    const query = (search?.value || '').trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      const words = `${card.textContent} ${card.dataset.search || ''}`.toLocaleLowerCase();
      card.hidden = !((category === 'all' || card.dataset.category === category) && words.includes(query));
      if (!card.hidden) visible++;
    }
    if (count) count.textContent = `${visible} ${visible === 1 ? 'project' : 'projects'}`;
    if (noResults) noResults.hidden = visible !== 0;
    for (const button of filters) {
      const selected = button.dataset.filter === category;
      button.setAttribute('aria-pressed', String(selected));
      button.classList.toggle('is-active', selected);
    }
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filterProjects();
  }));
  search?.addEventListener('input', filterProjects);
  if (cards.length) filterProjects();

  const dialog = document.querySelector('#lightbox');
  const fullImage = document.querySelector('#lightbox-image');
  const caption = document.querySelector('#lightbox-caption');
  const close = document.querySelector('#lightbox-close');
  const previous = document.querySelector('#lightbox-prev');
  const next = document.querySelector('#lightbox-next');
  const images = [...document.querySelectorAll('[data-lightbox]')];
  if (dialog && fullImage && images.length) {
    let index = 0;
    let trigger = null;
    function showImage(position) {
      index = (position + images.length) % images.length;
      const source = images[index];
      const thumbnail = source.querySelector('img');
      fullImage.src = source.dataset.full || source.dataset.src || thumbnail?.currentSrc || thumbnail?.src || '';
      fullImage.alt = thumbnail?.alt || source.dataset.caption || '';
      if (caption) caption.textContent = `${source.dataset.caption || fullImage.alt} (${index + 1} / ${images.length})`;
    }
    if (previous) previous.hidden = images.length < 2;
    if (next) next.hidden = images.length < 2;
    images.forEach((button, position) => button.addEventListener('click', event => {
      event.preventDefault();
      trigger = button;
      showImage(position);
      dialog.showModal();
      document.body.classList.add('modal-open');
      close?.focus();
    }));
    close?.addEventListener('click', () => dialog.close());
    previous?.addEventListener('click', () => showImage(index - 1));
    next?.addEventListener('click', () => showImage(index + 1));
    dialog.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        showImage(index + (event.key === 'ArrowLeft' ? -1 : 1));
      }
    });
    dialog.addEventListener('click', event => {
      if (event.target === dialog || event.target.classList?.contains('lightbox-inner')) dialog.close();
    });
    dialog.addEventListener('close', () => {
      document.body.classList.remove('modal-open');
      trigger?.focus();
    });
  }

  const projectInput = document.querySelector('#contact-project');
  const projectName = new URLSearchParams(window.location.search).get('project');
  if (projectInput && projectName) projectInput.value = projectName.slice(0, 160);
  document.querySelectorAll('.year').forEach(element => {
    element.textContent = String(new Date().getFullYear());
  });
})();
