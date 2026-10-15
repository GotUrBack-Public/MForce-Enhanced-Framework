/* Dependency-free Academy search/filter/mobile navigation smoke test. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class Element {
  constructor(dataset = {}) {
    this.dataset = dataset;
    this.listeners = {};
    this.attrs = {};
    this.hidden = false;
    this.value = '';
    this.textContent = '';
    const classes = new Set();
    this.classList = {
      add: name => classes.add(name),
      remove: name => classes.delete(name),
      contains: name => classes.has(name),
      toggle: (name, force) => {
        if (force === undefined ? !classes.has(name) : force) classes.add(name);
        else classes.delete(name);
      }
    };
  }
  addEventListener(name, fn) { (this.listeners[name] ??= []).push(fn); }
  fire(name, event = {}) { for (const fn of this.listeners[name] || []) fn(event); }
  click() { this.fire('click'); }
  setAttribute(name, value) { this.attrs[name] = value; }
  removeAttribute(name) { delete this.attrs[name]; }
  getAttribute(name) { return this.attrs[name]; }
  querySelector() { return { textContent: this.textContent }; }
  focus() { this.focused = true; }
}

const chips = ['all', 'foundation', 'osint', 'security', 'reporting']
  .map(name => new Element({ areaFilter: name }));
const cards = ['foundation', 'osint', 'security', 'reporting']
  .map(name => {
    const card = new Element({ area: name, search: name });
    card.textContent = name;
    return card;
  });
const search = new Element();
const status = new Element();
const empty = new Element();
const reset = new Element();
const sidebar = new Element();
const toggle = new Element();
const links = [new Element(), new Element()];
const ids = new Map([
  ['area-search', search], ['area-results', status], ['area-empty', empty],
  ['reset-filters', reset], ['academy-sidebar', sidebar], ['sidebar-toggle', toggle]
]);
const document = {
  getElementById(id) { return ids.get(id); },
  querySelectorAll(selector) {
    return selector === '[data-area-filter]' ? chips :
      selector === '[data-area]' ? cards :
      selector === '.side-nav a[href^="#"]' ? links : [];
  },
  addEventListener(name, fn) { (this.listeners ??= {})[name] = fn; }
};
const code = fs.readFileSync(path.join(__dirname, '../academy/assets/js/academy.js'), 'utf8');
vm.runInNewContext(code, { document }, { filename: 'academy.js', timeout: 3000 });

assert.equal(status.textContent, '4 geplante Lernbereiche');
assert.equal(cards.filter(card => !card.hidden).length, 4);
chips[2].click();
assert.equal(status.textContent, '1 geplanter Lernbereich');
assert.equal(cards.filter(card => !card.hidden)[0].dataset.area, 'osint');
assert.equal(chips[2].getAttribute('aria-pressed'), 'true');
search.value = 'missing-area';
search.fire('input');
assert.equal(empty.hidden, false);
assert.equal(status.textContent, '0 geplante Lernbereiche');
reset.click();
assert.equal(empty.hidden, true);
assert.equal(search.value, '');
assert.equal(cards.filter(card => !card.hidden).length, 4);
toggle.click();
assert.equal(sidebar.classList.contains('is-open'), true);
assert.equal(toggle.getAttribute('aria-expanded'), 'true');
links[1].click();
assert.equal(sidebar.classList.contains('is-open'), false);
assert.equal(links[1].getAttribute('aria-current'), 'page');
toggle.click();
document.listeners.keydown({ key: 'Escape' });
assert.equal(toggle.getAttribute('aria-expanded'), 'false');
console.log('Academy overview interaction smoke tests: PASS');
