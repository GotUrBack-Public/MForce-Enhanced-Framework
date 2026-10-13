/* MForce v7 / calm motion layer.
   Progressive enhancement only; no external libraries, tracking or requests. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const canMove = () => !motionQuery.matches && finePointer.matches;
  const sections = ['modules', 'osint', 'tutorials', 'schulung', 'install'];
  const railLinks = $$('.explore-rail a[href^="#"]');
  const targets = sections.map(id => document.getElementById(id)).filter(Boolean);
  const setCurrent = id => {
    railLinks.forEach(link => {
      if (link.getAttribute('href') === '#' + id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };

  // Section progress is an actual viewport observation, never a fabricated state.
  if ('IntersectionObserver' in window && targets.length) {
    const visible = new Map();
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) visible.set(entry.target.id, entry.boundingClientRect.top);
        else visible.delete(entry.target.id);
      });
      if (!visible.size) return;
      const closest = [...visible].sort((a, b) => Math.abs(a[1] - 130) - Math.abs(b[1] - 130))[0];
      if (closest) setCurrent(closest[0]);
    }, { rootMargin: '-12% 0px -45% 0px', threshold: 0 });
    targets.forEach(target => observer.observe(target));
  }
  railLinks.forEach(link => link.addEventListener('click', () => setCurrent(link.hash.slice(1))));

  // One-shot entrance accents. Content stays visible if the observer is unsupported.
  if ('IntersectionObserver' in window && !motionQuery.matches) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('glass-visible');
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.16, rootMargin: '0px 0px -20px 0px' });
    $$('.facts-inner, .explore-rail-inner, .academy-roadmap-header, .tutorial-below, .hero-art-frame').forEach(el => observer.observe(el));
  }

  // Decorative pointer parallax; one rAF at a time and no sensors.
  const hero = $('.hero');
  const orbit = $('.hero-orbit');
  let pointerFrame = 0;
  let px = 0, py = 0;
  const renderPointer = () => {
    pointerFrame = 0;
    if (!hero || !orbit || !canMove()) return;
    hero.style.setProperty('--glass-move-x', px.toFixed(1) + 'px');
    hero.style.setProperty('--glass-move-y', py.toFixed(1) + 'px');
  };
  if (hero && orbit) {
    hero.addEventListener('pointermove', event => {
      if (!canMove()) return;
      const bounds = hero.getBoundingClientRect();
      if (!bounds.width || !bounds.height) return;
      px = ((event.clientX - bounds.left) / bounds.width - .5) * 25;
      py = ((event.clientY - bounds.top) / bounds.height - .5) * 20;
      if (!pointerFrame) pointerFrame = requestAnimationFrame(renderPointer);
    }, { passive: true });
    hero.addEventListener('pointerleave', () => {
      if (pointerFrame) cancelAnimationFrame(pointerFrame);
      pointerFrame = 0; px = 0; py = 0;
      hero.style.removeProperty('--glass-move-x');
      hero.style.removeProperty('--glass-move-y');
    });
  }

  // Animate real tutorial/academy state changes; no DOM replacements or innerHTML.
  const animateChange = (selector) => {
    if (motionQuery.matches || document.hidden) return;
    const panel = $(selector);
    if (!panel || typeof panel.animate !== 'function') return;
    panel.getAnimations().forEach(animation => {
      if (animation.id === 'mforce-glass-switch') animation.cancel();
    });
    const animation = panel.animate(
      [{ opacity: .66, transform: 'translateY(9px)' }, { opacity: 1, transform: 'translateY(0)' }],
      { duration: 340, easing: 'cubic-bezier(.2,.75,.22,1)' }
    );
    animation.id = 'mforce-glass-switch';
  };
  $$('.tutorial-choice, .tutorial-controls button').forEach(button => {
    button.addEventListener('click', () => animateChange('.tutorial-stage-main'));
  });
  $$('.academy-track').forEach(button => {
    button.addEventListener('click', () => animateChange('.academy-detail'));
  });

  // Subtle glints appear on actual user interaction only.
  $$('.module-card, .osint-tool, .academy-track').forEach(card => {
    card.classList.add('glass-shine');
  });

  // Reduced-motion changes during the session take effect immediately.
  const stopMotion = () => {
    if (!motionQuery.matches) return;
    if (pointerFrame) cancelAnimationFrame(pointerFrame);
    pointerFrame = 0;
    hero?.style.removeProperty('--glass-move-x');
    hero?.style.removeProperty('--glass-move-y');
    $$('.tutorial-stage-main, .academy-detail').forEach(panel => panel.getAnimations?.().forEach(animation => {
      if (animation.id === 'mforce-glass-switch') animation.cancel();
    }));
  };
  if (typeof motionQuery.addEventListener === 'function') motionQuery.addEventListener('change', stopMotion);
  else if (typeof motionQuery.addListener === 'function') motionQuery.addListener(stopMotion);
})();
