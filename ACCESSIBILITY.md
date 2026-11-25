# Accessibility

MForce Enhanced Framework is a terminal (Termux/Linux) security toolkit with a
companion static website and a standalone Academy page. Accessibility matters
because security and learning tools should be usable by people who rely on
keyboards, screen readers, high-contrast modes or reduced-motion settings,
regardless of experience or ability.

This document describes our accessibility commitments, what contributors should
verify, and how to report a barrier.

## Priorities

- **Keyboard first.** The terminal UI is fully operable with the keyboard
  (arrow keys, J/K, Home/End, Enter, Q) without a mouse.
- **Readable output.** The interface remains usable on narrow terminals and
  when color is disabled; status is never conveyed by color alone.
- **Reduced motion.** The website and Academy respect `prefers-reduced-motion`.
- **Semantic, labeled content.** The website and Academy use semantic HTML,
  accessible labels, visible focus and sufficient color contrast.
- **Plain language.** Documentation aims to describe real user experience
  rather than relying on jargon.

Any accessibility target (for example a WCAG level) is an **aspirational
goal**, not a verified conformance claim. Conformance is only claimed after a
formal evaluation with a defined scope, date, method and evaluator.

## Contributor expectations

- Keep all interactive flows keyboard-accessible and verify a logical focus
  order for user-facing changes.
- Preserve and test `prefers-reduced-motion` behavior and responsive layouts.
- Maintain sufficient contrast and never rely on color alone for meaning.
- Use semantic HTML, accessible names/labels and status announcements
  (`aria-live`) where the UI already does.
- The website must stay static and must not silently execute security scans.
- Include a short note in the pull request describing the accessibility checks
  you ran (keyboard, mobile, reduced motion).

## Reporting accessibility issues

Open a **non-sensitive** GitHub issue describing the barrier. Helpful context:

- The affected task, page or terminal flow.
- What you expected and what happened instead.
- Browser, operating system and assistive technology used.
- Terminal type and width, if the issue is in the CLI.

Screenshots or recordings are optional. Do **not** include credentials,
personal data or private target information, and do not require disability
disclosure to report a barrier.

### Severity

Maintainers may triage issues by how strongly a barrier blocks a task:

- **Blocking** — a task cannot be completed at all with assistive means.
- **Major** — a task is possible only with significant difficulty or a
  workaround.
- **Minor** — a task is completed but with avoidable friction.

Reporters do not need to assign severity; maintainers confirm it during triage.

### How we respond

Maintainers will acknowledge the report, ask for clarification if needed,
provide a workaround when one exists, and track the fix in Git history. No
fixed response deadline is promised for this early-stage, best-effort project.

## Ownership and maintenance

Accessibility is maintained by the project maintainers as part of the regular
review process (see [docs/MAINTAINERS.md](docs/MAINTAINERS.md)). Review happens
on a best-effort basis alongside other contributions; ownership transfers with
project maintainership.

## Supported environments

- **Termux** on Android (ARM) and **Linux** distributions (x86_64), including
  Debian, Ubuntu and Kali Linux, via the terminal UI.
- Modern desktop and mobile browsers for the static website and Academy.

Specific versions and assistive-technology combinations are not exhaustively
evaluated; partial support is possible.

## Known limitations

- The interactive CLI has not been evaluated with every screen reader; terminal
  output is text-based but not formally audited.
- No automated accessibility test suite or third-party audit has been run.
- The Academy is a preview with no published courses yet.

## Feedback and improvements

Suggest improvements through a non-sensitive GitHub issue using the
documentation/feedback template. Direct active accessibility barriers to the
reporting process above. See [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation guidelines.