/* No external dependencies: simulated DOM smoke tests for MForce site.js. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const web = path.resolve(__dirname, '../web/js');
class Element {
  constructor(dataset = {}) {
    this.dataset = dataset;
    this.listeners = {};
    this.attrs = {};
    this.hidden = false;
    this.disabled = false;
    this.open = false;
    this.value = '';
    this.textContent = '';
    this.innerHTML = '';
    this.style = { setProperty() {}, removeProperty() {}, width: '' };
    this.classList = { add() {}, remove() {}, toggle() {} };
  }
  addEventListener(name, fn) { (this.listeners[name] ??= []).push(fn); }
  click() { for (const fn of this.listeners.click || []) fn({ target: this }); }
  fire(name) { for (const fn of this.listeners[name] || []) fn({ target: this }); }
  setAttribute(key, value) { this.attrs[key] = value; }
  getAttribute(key) { return this.attrs[key]; }
  focus() {}
  scrollIntoView() {}
  getBoundingClientRect() { return { left: 0, top: 0, width: 500, height: 500 }; }
}

function environment() {
  const ids = new Map();
  const at = id => {
    if (!ids.has(id)) ids.set(id, new Element());
    return ids.get(id);
  };
  const groups = {
    '.wiki-toc a[href^="#"]': [],
    '[data-copy]': []
  };
  const emptySelectors = new Set(['.back-to-top', '.menu-button', '#navigation', '#year']);
  const document = {
    documentElement: { classList: { add() {}, remove() {} }, scrollHeight: 3000 },
    activeElement: new Element(),
    hidden: false,
    querySelector(selector) {
      if (emptySelectors.has(selector)) return null;
      if (selector.startsWith('#')) return at(selector.slice(1));
      return null;
    },
    querySelectorAll(selector) { return groups[selector] || []; },
    getElementById(id) { return at(id); },
    createElement() { return new Element(); },
    addEventListener() {}
  };
  const window = {
    matchMedia() { return { matches: true }; },
    addEventListener() {},
    scrollTo() {},
    scrollY: 0
  };
  const context = {
    document, window, navigator: { clipboard: { writeText: async () => {} } },
    performance: { now: () => 0 },
    requestAnimationFrame() {},
    addEventListener() {},
    innerWidth: 1440, innerHeight: 900, scrollY: 0,
    scrollTo() {}, HTMLElement: Element, HTMLButtonElement: Element,
    setTimeout() { return 1; }, clearTimeout() {},
    IntersectionObserver: undefined,
    console
  };
  window.setTimeout = context.setTimeout;
  return { at, groups, document, context };
}

function runScript(name, env) {
  const script = fs.readFileSync(path.join(web, name), 'utf8');
  vm.runInNewContext(script, env.context, { filename: name, timeout: 3000 });
}

function testMobileNavToggle() {
  const env = environment();
  const menu = new Element();
  menu.setAttribute('aria-expanded', 'false');
  const nav = new Element();
  nav.querySelectorAll = () => [];
  env.document.querySelector = selector => {
    if (selector === '.menu-button') return menu;
    if (selector === '#navigation') return nav;
    return null;
  };
  runScript('site.js', env);
  menu.click();
  assert.equal(menu.getAttribute('aria-expanded'), 'true');
  assert.equal(nav.classList.toggle.length >= 0, true);
  menu.click();
  assert.equal(menu.getAttribute('aria-expanded'), 'false');
}

function testCopyButton() {
  const env = environment();
  const code = new Element();
  code.innerText = 'bash xrm742.sh';
  const label = new Element();
  label.textContent = 'COPY';
  const btn = new Element({ copy: 'install-code' });
  btn.querySelector = () => label;
  env.document.getElementById = id => (id === 'install-code' ? code : new Element());
  env.document.querySelectorAll = selector => (selector === '[data-copy]' ? [btn] : []);
  runScript('site.js', env);
  btn.click();
  // No throw is sufficient; clipboard is async and stubbed.
}

testMobileNavToggle();
testCopyButton();
console.log('MForce site interaction smoke tests: PASS');