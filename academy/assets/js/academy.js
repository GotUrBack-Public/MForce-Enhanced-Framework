/* Isolated Academy overview: filters describe planned areas, never fabricate courses. */
(() => {
  'use strict';
  const search = document.getElementById('area-search');
  const chips = [...document.querySelectorAll('[data-area-filter]')];
  const cards = [...document.querySelectorAll('[data-area]')];
  const status = document.getElementById('area-results');
  const empty = document.getElementById('area-empty');
  const reset = document.getElementById('reset-filters');
  const sidebar = document.getElementById('academy-sidebar');
  const toggle = document.getElementById('sidebar-toggle');
  const links = [...document.querySelectorAll('.side-nav a[href^="#"]')];
  let active = 'all';

  function update() {
    const query = (search?.value || '').trim().toLocaleLowerCase('de');
    let visible = 0;
    for (const card of cards) {
      const matchesCategory = active === 'all' || card.dataset.area === active;
      const matchesText = !query || (card.dataset.search || '').toLocaleLowerCase('de').includes(query)
        || card.querySelector('h3').textContent.toLocaleLowerCase('de').includes(query);
      card.hidden = !(matchesCategory && matchesText);
      if (!card.hidden) visible++;
    }
    for (const chip of chips) chip.setAttribute('aria-pressed', String(chip.dataset.areaFilter === active));
    if (status) status.textContent = visible === 1 ? '1 geplanter Lernbereich' : visible + ' geplante Lernbereiche';
    if (empty) empty.hidden = visible !== 0;
  }

  chips.forEach(chip => chip.addEventListener('click', () => {
    active = chip.dataset.areaFilter;
    update();
  }));
  search?.addEventListener('input', update);
  reset?.addEventListener('click', () => {
    active = 'all';
    if (search) search.value = '';
    update();
    search?.focus();
  });

  function closeMenu() {
    sidebar?.classList.remove('is-open');
    toggle?.setAttribute('aria-expanded', 'false');
    toggle?.setAttribute('aria-label', 'Menü öffnen');
  }
  toggle?.addEventListener('click', () => {
    const open = !sidebar?.classList.contains('is-open');
    sidebar?.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
  });
  links.forEach(link => link.addEventListener('click', () => {
    for (const item of links) item.removeAttribute('aria-current');
    link.setAttribute('aria-current', 'page');
    closeMenu();
  }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeMenu();
  });
  update();
})();
