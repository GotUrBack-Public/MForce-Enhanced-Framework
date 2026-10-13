/* MForce learning experience. Examples only: no commands are executed remotely. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const termuxSetup = 'pkg update\npkg install git bash jq python coreutils ncurses-utils iproute2';
  const linuxSetup = 'sudo apt update\nsudo apt install git bash jq python3 coreutils ncurses-bin iproute2';
  const clone = 'git clone https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git\ncd MForce-Enhanced-Framework';

  const paths = [
    {
      id: 'install', label: 'GETTING STARTED', duration: '~ 5 MIN',
      steps: [
        {
          title: 'Set up your environment',
          description: 'Install the packages MForce needs before cloning the project.',
          code: { termux: termuxSetup, linux: linuxSetup },
          note: { termux: 'Use the official Termux environment. No root access is needed.', linux: 'These commands target Debian or Ubuntu. Other distributions use different package managers.' }
        },
        {
          title: 'Clone the official repository',
          description: 'Download the open-source project into your terminal workspace.',
          code: clone,
          note: 'Check the GitHub repository URL before cloning. Use a Git clone rather than a ZIP if you want to use the updater.'
        },
        {
          title: 'Launch MForce',
          description: 'Start the terminal interface and enter the displayed confirmation code.',
          code: 'bash xrm742.sh',
          note: 'Navigate with the arrow keys or J/K, press Enter to open a module, and use Q to return.'
        }
      ]
    },
    {
      id: 'website', label: 'WEB INTELLIGENCE', duration: '~ 8 MIN',
      steps: [
        {
          title: 'Define your authorized scope',
          description: 'Begin by reading the module help. Replace example targets only with websites you are permitted to assess.',
          code: 'bash src/functions/web311.sh --help',
          note: 'Educational Purpose / Professional Usage. Public availability does not automatically grant permission for an assessment.'
        },
        {
          title: 'Inspect public website signals',
          description: 'Review HTTP status, visible metadata, security headers, forms and public JavaScript references.',
          code: 'bash src/functions/web311.sh https://your-authorized-site.example',
          note: 'The .example address is a placeholder. The inspector does not submit forms or attempt authentication.'
        },
        {
          title: 'Review DOM and rate-limit hints',
          description: 'Look for JavaScript patterns such as innerHTML and inspect advertised rate-limit information.',
          code: 'bash src/functions/jsn314.sh https://your-authorized-site.example\nbash src/functions/rat313.sh https://your-authorized-site.example',
          note: 'A DOM pattern is not proof of XSS. Missing rate-limit headers mean UNKNOWN, not unlimited requests.'
        }
      ]
    },
    {
      id: 'network', label: 'NETWORK INTELLIGENCE', duration: '~ 6 MIN',
      steps: [
        {
          title: 'Inspect DNS records',
          description: 'Start with public DNS data to understand a domain’s published configuration.',
          code: 'bash src/functions/dns211.sh example.org',
          note: 'DNS data can change. Cross-check observations and respect the target’s policies.'
        },
        {
          title: 'Understand the TLS certificate',
          description: 'Inspect certificate metadata and validity information for a domain.',
          code: 'bash src/functions/tls213.sh example.org',
          note: 'Certificate metadata is contextual information, not a complete security assessment.'
        },
        {
          title: 'Inspect IP context',
          description: 'Use a public resolver IP as an example of basic address intelligence.',
          code: 'bash src/functions/ipa212.sh 1.1.1.1',
          note: 'Public IP information can still qualify as personal data in some contexts. Collect and retain only what you need.'
        }
      ]
    },
    {
      id: 'ports', label: 'AUTHORIZED SECURITY', duration: '~ 7 MIN',
      steps: [
        {
          title: 'Understand the scanner limits',
          description: 'Read the TCP scanner options and verify the scope of your permission.',
          code: 'bash src/functions/tcp401.sh --help',
          note: 'Scan only systems you own or have explicit authorization to assess. No stealth, evasion or exploitation.'
        },
        {
          title: 'Check your own localhost',
          description: 'Perform a small TCP connect scan against your local machine.',
          code: 'bash src/functions/tcp401.sh 127.0.0.1 --authorized --ports 22,80,443,8080',
          note: 'The --authorized flag is an explicit confirmation of permission. The scanner is bounded and needs no root access.'
        },
        {
          title: 'Interpret the result carefully',
          description: 'An open port means a TCP connection succeeded. It does not prove a vulnerability.',
          code: 'bash src/functions/tcp401.sh 127.0.0.1 --authorized --ports 22,80,443,8080 --json',
          note: 'CLOSED_OR_FILTERED combines rejection and filtering. Verify findings manually and do not overstate conclusions.'
        }
      ]
    },
    {
      id: 'update', label: 'MAINTENANCE', duration: '~ 4 MIN',
      steps: [
        {
          title: 'Check for updates safely',
          description: 'Ask the official GitHub repository whether a newer main revision is available.',
          code: 'bash src/functions/upd501.sh --check',
          note: 'Requires an official Git clone on main, a clean working tree, Git and Python 3.'
        },
        {
          title: 'Apply the official update',
          description: 'The updater requests confirmation and performs a fast-forward-only update.',
          code: 'bash src/functions/upd501.sh',
          note: 'Local modifications and divergent branches are never discarded automatically. The animated bar shows activity, not a fabricated percentage.'
        },
        {
          title: 'Restart the framework',
          description: 'Restart MForce to load the new files after a successful update.',
          code: 'bash xrm742.sh',
          note: 'If the update was refused, inspect your Git status rather than forcing a reset.'
        }
      ]
    }
  ];

  const choiceButtons = $$('[data-tutorial]');
  const platformButtons = $$('[data-tutorial-platform]');
  const title = $('#tutorial-title');
  const description = $('#tutorial-description');
  const category = $('#tutorial-category');
  const duration = $('#tutorial-duration');
  const pathNumber = $('#tutorial-path-number');
  const stepIndicator = $('#tutorial-step-indicator');
  const terminalTitle = $('#tutorial-terminal-title');
  const code = $('#tutorial-code');
  const note = $('#tutorial-note');
  const platformRow = $('#tutorial-platform-row');
  const progressLabel = $('#tutorial-progress-label');
  const progressFill = $('#tutorial-progress-fill');
  const previous = $('#tutorial-prev');
  const next = $('#tutorial-next');
  const copyButton = $('#tutorial-copy');
  const announce = $('#tutorial-announcement');
  const stage = $('.tutorial-stage');
  let activePath = 0;
  let activeStep = 0;
  let platform = 'termux';
  let copyReset = 0;

  const currentCode = () => {
    const value = paths[activePath].steps[activeStep].code;
    return typeof value === 'string' ? value : value[platform];
  };
  const currentNote = () => {
    const value = paths[activePath].steps[activeStep].note;
    return typeof value === 'string' ? value : value[platform];
  };
  const two = number => String(number).padStart(2, '0');

  const render = (speak = false) => {
    const path = paths[activePath];
    const step = path.steps[activeStep];
    choiceButtons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.tutorial === path.id));
    });
    platformButtons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.tutorialPlatform === platform));
    });
    if (pathNumber) pathNumber.textContent = two(activePath + 1);
    if (category) category.textContent = path.label;
    if (duration) duration.textContent = path.duration;
    if (title) title.textContent = step.title;
    if (description) description.textContent = step.description;
    if (code) code.textContent = currentCode();
    if (note) note.textContent = currentNote();
    if (terminalTitle) terminalTitle.textContent = path.id === 'install' ? platform + ' / setup' : 'mforce / ' + path.id;
    if (platformRow) platformRow.hidden = path.id !== 'install' || activeStep !== 0;
    if (stepIndicator) stepIndicator.textContent = 'STEP ' + two(activeStep + 1) + ' / ' + two(path.steps.length);
    if (progressLabel) progressLabel.textContent = two(activeStep + 1) + ' / ' + two(path.steps.length);
    if (progressFill) progressFill.style.width = (100 * (activeStep + 1) / path.steps.length) + '%';
    if (previous) previous.disabled = activeStep === 0;
    if (next) next.textContent = activeStep === path.steps.length - 1
      ? (activePath === paths.length - 1 ? 'RESTART PATH ↺' : 'NEXT PATH →')
      : 'NEXT STEP →';
    if (copyButton) copyButton.textContent = 'COPY COMMAND ↗';
    if (speak && announce) announce.textContent = path.label + ', step ' + (activeStep + 1) + ': ' + step.title;
  };

  choiceButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
      activePath = paths.findIndex(path => path.id === button.dataset.tutorial);
      if (activePath < 0) { activePath = 0; return; }
      activeStep = 0;
      render(true);
      if (window.matchMedia('(max-width: 850px)').matches) {
        stage?.scrollIntoView({ behavior: reducedMotion() ? 'instant' : 'smooth', block: 'start' });
      }
    });
    button.addEventListener('keydown', event => {
      const nextIndex = event.key === 'ArrowDown' || event.key === 'ArrowRight' ? (index + 1) % choiceButtons.length :
        event.key === 'ArrowUp' || event.key === 'ArrowLeft' ? (index + choiceButtons.length - 1) % choiceButtons.length :
        event.key === 'Home' ? 0 : event.key === 'End' ? choiceButtons.length - 1 : -1;
      if (nextIndex >= 0) {
        event.preventDefault();
        choiceButtons[nextIndex].focus();
        choiceButtons[nextIndex].click();
      }
    });
  });
  platformButtons.forEach(button => button.addEventListener('click', () => {
    platform = button.dataset.tutorialPlatform === 'linux' ? 'linux' : 'termux';
    render(true);
  }));
  previous?.addEventListener('click', () => {
    if (activeStep > 0) { activeStep--; render(true); }
  });
  next?.addEventListener('click', () => {
    if (activeStep < paths[activePath].steps.length - 1) activeStep++;
    else {
      activePath = (activePath + 1) % paths.length;
      activeStep = 0;
    }
    render(true);
  });

  const copyText = async text => {
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard API unavailable');
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const input = document.createElement('textarea');
      input.value = text;
      input.setAttribute('readonly', '');
      input.style.cssText = 'position:fixed;top:0;left:-9999px;opacity:0';
      document.body.appendChild(input);
      input.focus();
      input.select();
      let copied = false;
      try { copied = document.execCommand('copy'); } catch { /* unsupported */ }
      input.remove();
      return copied;
    }
  };
  copyButton?.addEventListener('click', async () => {
    const copied = await copyText(currentCode());
    copyButton.textContent = copied ? 'COPIED ✓' : 'COPY UNAVAILABLE';
    if (announce) announce.textContent = copied ? 'Commands copied to clipboard.' : 'Copy unavailable. Select the commands manually.';
    clearTimeout(copyReset);
    copyReset = window.setTimeout(() => { copyButton.textContent = 'COPY COMMAND ↗'; }, 2400);
  });
  render();

  // Future training roadmap: informative previews, not enrollment or a live course.
  const tracks = {
    foundation: {
      title: 'Terminal Foundations',
      summary: 'An introductory path for the MForce terminal environment.',
      topics: ['Terminal navigation and Bash essentials', 'Termux vs. Linux environments', 'Installing and updating MForce']
    },
    osint: {
      title: 'OSINT Methodology',
      summary: 'A proposed framework for repeatable, low-impact public-data research.',
      topics: ['DNS, IP and website evidence', 'Understanding rate-limit and DOM signals', 'Source verification and uncertainty']
    },
    security: {
      title: 'Authorized Security',
      summary: 'Proposed foundations for scoped, accountable security assessment.',
      topics: ['Authorization and scope definition', 'Bounded TCP port checks and interpretation', 'Safe reporting and responsible disclosure']
    },
    privacy: {
      title: 'Reporting & Privacy',
      summary: 'Planned guidance for responsible handling of technical findings.',
      topics: ['Clear findings and evidence quality', 'Data minimization and retention', 'GDPR / DSGVO principles and legal basis']
    }
  };
  const trackButtons = $$('[data-track]');
  const detailNumber = $('#academy-detail-number');
  const detailTitle = $('#academy-detail-title');
  const detailSummary = $('#academy-detail-summary');
  const topics = $('#academy-topics');
  const chooseTrack = name => {
    const track = tracks[name];
    if (!track) return;
    trackButtons.forEach((button, index) => {
      const selected = button.dataset.track === name;
      button.setAttribute('aria-pressed', String(selected));
      if (selected && detailNumber) detailNumber.textContent = two(index + 1) + ' / FUTURE CURRICULUM';
    });
    if (detailTitle) detailTitle.textContent = track.title;
    if (detailSummary) detailSummary.textContent = track.summary;
    if (topics) {
      topics.replaceChildren(...track.topics.map(topic => {
        const item = document.createElement('li');
        item.textContent = topic;
        return item;
      }));
    }
  };
  trackButtons.forEach((button, index) => {
    button.addEventListener('click', () => chooseTrack(button.dataset.track));
    button.addEventListener('keydown', event => {
      const nextIndex = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? (index + 1) % trackButtons.length :
        event.key === 'ArrowLeft' || event.key === 'ArrowUp' ? (index + trackButtons.length - 1) % trackButtons.length :
        event.key === 'Home' ? 0 : event.key === 'End' ? trackButtons.length - 1 : -1;
      if (nextIndex >= 0) {
        event.preventDefault();
        trackButtons[nextIndex].focus();
        chooseTrack(trackButtons[nextIndex].dataset.track);
      }
    });
  });
  chooseTrack('foundation');

  // Animate only visible elements; never hide content if IntersectionObserver is missing.
  if (!reducedMotion() && 'IntersectionObserver' in window) {
    const targets = $$('.tutorial-shell, .tutorial-below, .academy-top > div, .academy-roadmap, .academy-disclaimer');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.07, rootMargin: '0px 0px -25px 0px' });
    targets.forEach(element => {
      element.dataset.reveal = '';
      observer.observe(element);
    });
  }

  if (!reducedMotion() && window.matchMedia('(hover:hover) and (pointer:fine)').matches && stage) {
    stage.addEventListener('pointermove', event => {
      const rect = stage.getBoundingClientRect();
      stage.style.setProperty('--stage-x', ((event.clientX - rect.left) / rect.width * 100).toFixed(1) + '%');
      stage.style.setProperty('--stage-y', ((event.clientY - rect.top) / rect.height * 100).toFixed(1) + '%');
    }, { passive: true });
    stage.addEventListener('pointerleave', () => {
      stage.style.removeProperty('--stage-x');
      stage.style.removeProperty('--stage-y');
    });
  }
})();
