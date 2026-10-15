/* No external dependencies: simulated DOM smoke tests for MForce website controls. */
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
  showModal() { this.open = true; }
  close() { this.open = false; }
  replaceChildren(...children) { this.children = children; }
  getBoundingClientRect() { return { left: 0, top: 0, width: 500, height: 500 }; }
}

const create = (names, key) => names.map(name => {
  const element = new Element({ [key]: name });
  element.id = key + '-' + name;
  return element;
});

function environment() {
  const ids = new Map();
  const at = id => {
    if (!ids.has(id)) ids.set(id, new Element());
    return ids.get(id);
  };
  const groups = {
    '[data-audit]': create(['rate', 'dom', 'headers'], 'audit'),
    '[data-module]': create(['network', 'system', 'future', 'scanner', 'updater'], 'module'),
    '[data-platform]': create(['termux', 'linux'], 'platform'),
    '[data-card]': create(['network', 'system', 'future', 'scanner', 'updater'], 'card'),
    '[data-tutorial]': create(['install', 'website', 'network', 'ports', 'update'], 'tutorial'),
    '[data-tutorial-platform]': create(['termux', 'linux'], 'tutorialPlatform'),
    '[data-track]': create(['foundation', 'osint', 'security', 'privacy'], 'track'),
    '[data-inspect]': [],
    '[data-platform-link]': [],
    '[data-count]': []
  };
  const emptySelectors = new Set(['.facts', '.hero', '.hero-art', '.hero-art-frame', '.back-to-top', '.menu-button', '#navigation', '#year', '.page-progress']);
  const document = {
    documentElement: { classList: { add() {}, remove() {} }, scrollHeight: 3000 },
    activeElement: new Element(),
    hidden: false,
    querySelector(selector) {
      if (emptySelectors.has(selector)) return null;
      if (selector === '.tutorial-stage') return at('tutorial-stage');
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
    isSecureContext: false
  };
  const context = {
    document, window, navigator: {},
    performance: { now: () => 0 },
    requestAnimationFrame() {},
    addEventListener() {},
    innerWidth: 1440, innerHeight: 900, scrollY: 0,
    scrollTo() {}, HTMLElement: Element, HTMLButtonElement: Element,
    setTimeout() { return 1; }, clearTimeout() {},
    console
  };
  window.setTimeout = context.setTimeout;
  return { at, groups, document, context };
}

function runScript(name, env) {
  const script = fs.readFileSync(path.join(web, name), 'utf8');
  vm.runInNewContext(script, env.context, { filename: name, timeout: 3000 });
}

function testModuleAndAuditTabs() {
  const env = environment();
  runScript('main.js', env);
  env.groups['[data-audit]'][1].click();
  assert.match(env.at('audit-output').textContent, /innerHTML/);
  env.groups['[data-audit]'][2].click();
  assert.match(env.at('audit-output').textContent, /SECURITY HEADERS/);
  env.groups['[data-module]'][4].click();
  assert.match(env.at('inspector-output').textContent, /UPDATE CENTER/);
  env.groups['[data-platform]'][1].click();
  assert.match(env.at('install-code').textContent, /sudo apt/);
}

function testTutorialAndAcademy() {
  const env = environment();
  runScript('learn.js', env);
  assert.match(env.at('tutorial-code').textContent, /pkg install/);
  env.groups['[data-tutorial-platform]'][1].click();
  assert.match(env.at('tutorial-code').textContent, /sudo apt/);
  env.at('tutorial-next').click();
  assert.match(env.at('tutorial-code').textContent, /git clone/);
  env.groups['[data-tutorial]'][3].click();
  assert.match(env.at('tutorial-code').textContent, /tcp401/);
}

function testPaletteEmptyState() {
  const env = environment();
  const dialog = env.at('command-dialog');
  const open = env.at('open-button');
  const close = env.at('close-button');
  const search = env.at('command-search');
  const empty = env.at('command-empty');
  const results = ['Platform overview', 'Interactive tutorials', 'Schulung roadmap'].map(title => {
    const item = new Element();
    item.textContent = title;
    item.dataset.keywords = title.toLowerCase();
    return item;
  });
  env.document.querySelector = selector => {
    if (selector === '[data-command-open]') return open;
    if (selector === '[data-command-close]') return close;
    return null;
  };
  env.document.querySelectorAll = selector => selector === '.command-results a' ? results : [];
  runScript('global.js', env);
  open.click();
  assert.equal(dialog.open, true);
  search.value = 'nothing-matches-this';
  search.fire('input');
  assert.equal(empty.hidden, false);
  assert.equal(results.every(link => link.hidden), true);
  search.value = 'Schulung';
  search.fire('input');
  assert.equal(empty.hidden, true);
  assert.equal(results.filter(link => !link.hidden).length, 1);
}

testModuleAndAuditTabs();
testTutorialAndAcademy();
testPaletteEmptyState();
console.log('MForce website interaction smoke tests: PASS');
