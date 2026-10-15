# Standalone Academy portal

The MForce Academy is a **separate static site** under `academy/`, served
at `/MForce-Enhanced-Framework/academy/` on GitHub Pages.

## Design goals

- Enterprise-style navigation, restrained visual hierarchy and responsive UI.
- No Academy content embedded in `web/html/main.html`; only navigation links.
- Independent HTML, CSS and JavaScript under `academy/`; no imports from
  `web/css/`, `web/js/` or the framework's interactive runtime.
- Four **planned subject areas**, with searchable/filterable cards.
- **Zero published courses**. No invented lessons, enrollment, progress,
  certificates, user accounts or launch dates.
- Explicit empty state and links to the separate, already-existing tutorials.
- Accessible keyboard controls, status announcements and reduced-motion support.
- No external fonts, scripts, tracking, backend requests or network scans.

## Files

- `academy/index.html`: semantic overview, planned areas, empty catalog and FAQ.
- `academy/assets/css/academy.css`: standalone visual design and responsive layout.
- `academy/assets/js/academy.js`: search, category filters, mobile navigation.
- `academy/data/courses.json`: an empty array reserved for **future** courses.

The courses JSON file is not fetched or displayed yet. It remains empty until
actual, reviewed courses are built and released. Future work should add a
versioned schema, safe rendering, per-course pages, content validation and tests
before populating it.

## Website refresh

The existing main site now loads `web/css/enterprise.css` as a last-loaded
override. This preserves legacy interactive features while reducing visual
noise, decorative effects, overly strong glassmorphism and inconsistent surfaces.
The previous inline Academy roadmap was removed from the homepage, along with
its obsolete JavaScript. No changes were made to MForce bot logic or README.

## Verification

```bash
python3 -m unittest tests.test_website tests.test_academy_portal -v
node tests/academy_interactions.js
```

Links and static assets are relative so both the root and project-subpath
GitHub Pages deployments work. The Academy is intentionally separate from
the existing five interactive tutorials.
