/* MForce Enhanced Framework — shared site interactions.
   No network requests, no tracking. Progressive enhancement only. */
(() => {
  'use strict';

  // Mobile navigation toggle.
  const menu = document.querySelector('.menu-button');
  const nav = document.querySelector('#navigation');
  if (menu && nav) {
    const close = () => {
      nav.classList.remove('open');
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', 'Open navigation');
    };
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      nav.classList.toggle('open', open);
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });
    nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', close));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    document.addEventListener('click', (e) => {
      if (!menu.contains(e.target) && !nav.contains(e.target)) close();
    });
  }

  // Footer year.
  const year = document.querySelector('#year');
  if (year) year.textContent = String(new Date().getFullYear());

  // Back-to-top button.
  const top = document.querySelector('.back-to-top');
  if (top) {
    let ticking = false;
    const update = () => {
      top.classList.toggle('show', window.scrollY > 640);
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
    top.addEventListener('click', () => {
      const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: reduce ? 'instant' : 'smooth' });
    });
  }

  // Wiki table-of-contents scroll-spy.
  const tocLinks = [...document.querySelectorAll('.wiki-toc a[href^="#"]')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const map = new Map(tocLinks.map((l) => [l.getAttribute('href').slice(1), l]));
    const obs = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          tocLinks.forEach((l) => l.classList.remove('active'));
          const link = map.get(entry.target.id);
          if (link) link.classList.add('active');
        }
      }
    }, { rootMargin: '-20% 0px -70% 0px' });
    document.querySelectorAll('.wiki-content section[id]').forEach((s) => obs.observe(s));
  }

  // Copy buttons for code blocks (data-copy attribute holds the target id).
  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const target = document.getElementById(btn.getAttribute('data-copy'));
      if (!target) return;
      const text = target.innerText;
      try {
        await navigator.clipboard.writeText(text);
        const label = btn.querySelector('span');
        if (label) {
          const prev = label.textContent;
          label.textContent = 'COPIED';
          setTimeout(() => { label.textContent = prev; }, 1600);
        }
      } catch (_) { /* clipboard unavailable; ignore */ }
    });
  });

  // External enhancement libraries (all optional; guarded so the page and the
  // headless smoke tests keep working when a CDN is unavailable).
  if (typeof lucide !== 'undefined' && typeof lucide.createIcons === 'function') {
    lucide.createIcons();
  }
  if (typeof AOS !== 'undefined' && typeof AOS.init === 'function') {
    AOS.init({
      duration: 620,
      easing: 'ease-out-cubic',
      once: true,
      offset: 40,
      disable: matchMedia('(prefers-reduced-motion: reduce)').matches,
    });
  }
  if (typeof hljs !== 'undefined' && typeof hljs.highlightAll === 'function') {
    hljs.highlightAll();
  }

  // ---------- Auth button (always wired, even if auth.js / Firebase fails) ----------
  // The real modal + menu live in auth.js. If auth.js loads, it sets
  // window.auth, window.toggleMenu and window.openAuthModal.
  // If it doesn't (e.g. Firebase CDN unreachable), we still show a visible hint
  // instead of silently doing nothing.
  document.querySelectorAll('[data-auth-toggle]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (window.auth && window.auth.currentUser) {
        window.toggleMenu(btn);
      } else if (typeof window.openAuthModal === 'function') {
        window.openAuthModal();
      } else {
        const overlay = document.querySelector('.auth-overlay');
        if (overlay) {
          overlay.classList.toggle('open');
          document.body.style.overflow = overlay.classList.contains('open') ? 'hidden' : '';
        } else {
          alert('Sign-in module is still loading. Please try again in a moment.');
        }
      }
    });
  });
})();