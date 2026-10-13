/* MForce website: interactive platform setup, module inspector and motion.
   No external JS dependencies. All previews are illustrative, never live scans. */
(() => {
  'use strict';

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const canAnimate = () => !reduced.matches;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  // Progressive enhancement: no content is hidden without working JavaScript.
  if (canAnimate()) {
    const revealTargets = $$('.section-intro, .module-card, .module-inspector, .architecture-text, .console, .security-grid > div, .cta-layout');
    revealTargets.forEach((el, i) => {
      el.dataset.reveal = '';
      if (el.classList.contains('module-card')) el.style.transitionDelay = ((i % 3) * 110) + 'ms';
    });
    document.documentElement.classList.add('motion-ready');
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -42px 0px' });
      revealTargets.forEach(el => observer.observe(el));
    } else {
      revealTargets.forEach(el => el.classList.add('revealed'));
    }
  }

  // A deliberate counter reveal, not simulated system information.
  const facts = $('.facts');
  const countUp = () => {
    if (facts) facts.classList.add('is-visible');
    if (!canAnimate()) return;
    $$('[data-count]').forEach(el => {
      const value = Number(el.dataset.count);
      const numberNode = el.firstChild;
      if (!numberNode || !Number.isFinite(value)) return;
      const start = performance.now();
      const tick = now => {
        const t = Math.min(1, (now - start) / 1200);
        const eased = 1 - Math.pow(1 - t, 3);
        numberNode.nodeValue = String(Math.round(value * eased)).padStart(2, '0');
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  };
  if (facts) {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting)) { countUp(); observer.disconnect(); }
      }, { threshold: .25 });
      observer.observe(facts);
    } else countUp();
  }

  const install = {
    termux: {
      title: 'termux@device:~',
      note: 'Termux on Android. Root is not required.',
      commands: [
        'pkg update',
        'pkg install git bash jq coreutils ncurses-utils iproute2',
        '',
        'git clone https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git',
        'cd MForce-Enhanced-Framework',
        'bash xrm742.sh'
      ].join('\n')
    },
    linux: {
      title: 'linux@terminal:~',
      note: 'Debian / Ubuntu example. Packages vary by distribution.',
      commands: [
        'sudo apt update',
        'sudo apt install -y git bash jq coreutils ncurses-bin iproute2',
        '',
        'git clone https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git',
        'cd MForce-Enhanced-Framework',
        'bash xrm742.sh'
      ].join('\n')
    }
  };

  let currentPlatform = 'termux';
  const code = $('#install-code');
  const terminalLabel = $('#platform-terminal-label');
  const platformNote = $('#platform-note');
  const platformButtons = $$('[data-platform]');
  const setPlatform = platform => {
    const config = install[platform];
    if (!config) return;
    currentPlatform = platform;
    if (code) code.textContent = config.commands;
    if (terminalLabel) terminalLabel.textContent = config.title;
    if (platformNote) platformNote.textContent = config.note;
    platformButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.platform === platform)));
  };
  platformButtons.forEach(button => button.addEventListener('click', () => setPlatform(button.dataset.platform)));
  $$('[data-platform-link]').forEach(button => button.addEventListener('click', () => {
    setPlatform(button.dataset.platformLink);
    const installSection = $('#install');
    if (installSection) installSection.scrollIntoView({ behavior: canAnimate() ? 'smooth' : 'instant', block: 'center' });
  }));

  // Clipboard works both on secure GitHub Pages and where fallback copying is permitted.
  const copyButton = $('#copy-command');
  if (copyButton) {
    const initialLabel = copyButton.innerHTML;
    let resetTimer;
    copyButton.addEventListener('click', async () => {
      const content = install[currentPlatform].commands;
      let copied = false;
      try {
        if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard API unavailable');
        await navigator.clipboard.writeText(content);
        copied = true;
      } catch {
        const field = document.createElement('textarea');
        field.value = content;
        field.style.cssText = 'position:fixed;opacity:0;left:-9999px;top:0';
        document.body.appendChild(field);
        field.focus();
        field.select();
        try { copied = document.execCommand('copy'); } catch { copied = false; }
        field.remove();
      }
      copyButton.textContent = copied ? 'COPIED ✓' : 'SELECT CODE TO COPY';
      if (!copied && code) {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        if (selection) { selection.removeAllRanges(); selection.addRange(range); }
      }
      clearTimeout(resetTimer);
      resetTimer = setTimeout(() => { copyButton.innerHTML = initialLabel; }, 2400);
    });
  }

  // Module inspector: illustrative samples, NOT collected user/device data.
  const modules = {
    network: {
      title: 'network_information — sample',
      description: 'Inspect local network interfaces, addresses and hostname.',
      output: '$ bash src/functions/lar386.sh --help\n\n' +
        'NETWORK INFORMATION\n' +
        '  • Network interfaces\n' +
        '  • Local IP addresses\n' +
        '  • Device hostname\n\n' +
        '# Availability depends on OS permissions.'
    },
    system: {
      title: 'system_information — sample',
      description: 'Discover host architecture, kernel and available device metadata.',
      output: '$ bash src/functions/vkn193.sh --help\n\n' +
        'SYSTEM INFORMATION\n' +
        '  • CPU architecture\n' +
        '  • Kernel / runtime\n' +
        '  • Android details (on Termux)\n\n' +
        '# Some fields differ on Linux.'
    },
    future: {
      title: 'development_roadmap — status',
      description: 'These modules are planned, not executable yet.',
      output: '# MFORCE ROADMAP\n\n' +
        'CONNECTION TEST     [NOT IMPLEMENTED]\n' +
        'OSINT SEARCH        [NOT IMPLEMENTED]\n\n' +
        'Follow the repository for updates.\n' +
        'No future functionality is represented as active.'
    }
  };
  const moduleTabs = $$('[data-module]');
  const modulePanel = $('#inspector-panel');
  const moduleOutput = $('#inspector-output');
  const moduleTitle = $('#inspector-title');
  const moduleDescription = $('#inspector-description');
  const replay = $('#replay-preview');
  let activeModule = 'network';
  let sequence = 0;
  const showModule = (name, scroll = false) => {
    if (!modules[name]) return;
    activeModule = name;
    moduleTabs.forEach(tab => {
      const selected = tab.dataset.module === name;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && modulePanel) modulePanel.setAttribute('aria-labelledby', tab.id);
    });
    $$('[data-card]').forEach(card => card.dataset.active = String(card.dataset.card === name));
    const data = modules[name];
    if (moduleTitle) moduleTitle.textContent = data.title;
    if (moduleDescription) moduleDescription.textContent = data.description;
    const thisSequence = ++sequence;
    if (moduleOutput) {
      moduleOutput.textContent = '';
      moduleOutput.classList.remove('is-complete');
      if (!canAnimate() || document.hidden) {
        moduleOutput.textContent = data.output;
        moduleOutput.classList.add('is-complete');
      } else {
        const begin = performance.now();
        const animate = now => {
          if (thisSequence !== sequence) return;
          const visible = Math.min(data.output.length, Math.floor((now - begin) / 6));
          moduleOutput.textContent = data.output.slice(0, visible);
          if (visible < data.output.length) requestAnimationFrame(animate);
          else moduleOutput.classList.add('is-complete');
        };
        requestAnimationFrame(animate);
      }
    }
    if (scroll) $('#module-inspector')?.scrollIntoView({ behavior: canAnimate() ? 'smooth' : 'instant', block: 'center' });
  };
  moduleTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => showModule(tab.dataset.module));
    tab.addEventListener('keydown', event => {
      let next = null;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % moduleTabs.length;
      else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index + moduleTabs.length - 1) % moduleTabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = moduleTabs.length - 1;
      if (next !== null) { event.preventDefault(); moduleTabs[next].focus(); showModule(moduleTabs[next].dataset.module); }
    });
  });
  $$('[data-inspect]').forEach(button => button.addEventListener('click', () => showModule(button.dataset.inspect, true)));
  if (replay) replay.addEventListener('click', () => showModule(activeModule));
  if (moduleOutput) moduleOutput.classList.add('is-complete');

  // Pointer interactions are desktop-only. Never run device-motion sensors.
  if (canAnimate() && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    const hero = $('.hero');
    const art = $('.hero-art');
    const frame = $('.hero-art-frame');
    if (hero) hero.addEventListener('pointermove', event => {
      const box = hero.getBoundingClientRect();
      hero.style.setProperty('--px', ((event.clientX - box.left) / box.width * 100).toFixed(1) + '%');
      hero.style.setProperty('--py', ((event.clientY - box.top) / box.height * 100).toFixed(1) + '%');
    }, { passive: true });
    if (art && frame && innerWidth > 1150) {
      art.addEventListener('pointermove', event => {
        const rect = art.getBoundingClientRect();
        const dx = (event.clientX - rect.left) / rect.width - .5;
        const dy = (event.clientY - rect.top) / rect.height - .5;
        frame.style.transform = `perspective(1200px) rotateY(${-dx * 9}deg) rotateX(${dy * 7}deg)`;
      }, { passive: true });
      art.addEventListener('pointerleave', () => { frame.style.transform = ''; });
    }
    $$('[data-card]').forEach(card => card.addEventListener('pointermove', event => {
      const box = card.getBoundingClientRect();
      card.style.setProperty('--mx', (event.clientX - box.left) + 'px');
      card.style.setProperty('--my', (event.clientY - box.top) + 'px');
    }, { passive: true }));
  }

  // Browser back/forward or restored tab: honor current platform choices.
  setPlatform(currentPlatform);
})();
