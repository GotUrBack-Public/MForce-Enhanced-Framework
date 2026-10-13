(()=>{'use strict';const menu=document.querySelector('.menu-button'),nav=document.querySelector('#navigation');if(menu&&nav){function close(){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label','Open navigation')}menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';nav.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close navigation':'Open navigation')});nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',close));document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});document.addEventListener('click',e=>{if(!menu.contains(e.target)&&!nav.contains(e.target))close()})}const year=document.querySelector('#year');if(year)year.textContent=new Date().getFullYear();const bar=document.querySelector('.page-progress');let ticking=false;function update(){const max=document.documentElement.scrollHeight-innerHeight;if(bar)bar.style.width=(max>0?Math.min(100,scrollY/max*100):0)+'%';ticking=false}addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(update);ticking=true}},{passive:true});update();if('IntersectionObserver'in window){const links=[...document.querySelectorAll('.nav a[href^="#"]')];const ob=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){for(const link of links)link.classList.toggle('active',link.getAttribute('href')==='#'+entry.target.id)}}},{rootMargin:'-18% 0px -68% 0px'});document.querySelectorAll('main section[id]').forEach(s=>ob.observe(s))}})();

/* Quick switcher, keyboard navigation and top-of-page affordance. */
(() => {
  'use strict';
  const dialog = document.getElementById('command-dialog');
  const openButton = document.querySelector('[data-command-open]');
  const closeButton = document.querySelector('[data-command-close]');
  const search = document.getElementById('command-search');
  const results = [...document.querySelectorAll('.command-results a')];
  const emptyMessage = document.getElementById('command-empty');
  let selected = 0;
  let lastFocus = null;
  const available = () => results.filter(link => !link.hidden);
  const setSelected = index => {
    const list = available();
    if (emptyMessage) emptyMessage.hidden = list.length !== 0;
    if (!list.length) {
      selected = 0;
      results.forEach(link => link.classList.remove('highlight'));
      return;
    }
    selected = ((index % list.length) + list.length) % list.length;
    results.forEach(link => link.classList.toggle('highlight', link === list[selected]));
  };
  const open = () => {
    if (!dialog || typeof dialog.showModal !== 'function') return;
    lastFocus = document.activeElement;
    if (search) search.value = '';
    results.forEach(link => link.hidden = false);
    dialog.showModal();
    setSelected(0);
    search?.focus();
  };
  const close = () => { if (dialog?.open) dialog.close(); };
  if (dialog) {
    openButton?.addEventListener('click', open);
    closeButton?.addEventListener('click', close);
    dialog.addEventListener('close', () => { if (lastFocus instanceof HTMLElement) lastFocus.focus(); });
    dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
    results.forEach(link => link.addEventListener('click', close));
    search?.addEventListener('input', () => {
      const term = search.value.toLowerCase().trim();
      results.forEach(link => link.hidden = !(`${link.textContent} ${link.dataset.keywords}`.toLowerCase().includes(term)));
      setSelected(0);
    });
    dialog.addEventListener('keydown', event => {
      if (event.key === 'Escape') { event.preventDefault(); close(); }
      else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        setSelected(selected + (event.key === 'ArrowDown' ? 1 : -1));
      } else if (event.key === 'Enter') {
        if (event.target instanceof HTMLButtonElement) return;
        const link = available()[selected];
        if (link) { event.preventDefault(); link.click(); }
      }
    });
  }
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      if (dialog?.open) close(); else open();
    }
  });
  const topButton = document.querySelector('.back-to-top');
  let scrollTicking = false;
  if (topButton) {
    const update = () => {
      topButton.classList.toggle('show', scrollY > 720);
      scrollTicking = false;
    };
    addEventListener('scroll', () => {
      if (!scrollTicking) { scrollTicking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
    topButton.addEventListener('click', () => {
      scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    });
  }
})();
