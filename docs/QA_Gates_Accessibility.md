# Accessibility QA Gates (Enforceable)
## Success Criteria
- Contrast ratio >= 4.5:1
- Keyboard: Enter=submit, Esc=close, predictable tab order
- ARIA roles present: nav, main, form, button, alert
- Focus ring: 2px Indigo-300 visible at 200% zoom

## Tooling
- Lint: eslint-plugin-jsx-a11y
- Automated: axe-core/pa11y run on key pages
- E2E: Playwright tests for Enter/Esc and tab order across Landing, Advisor, Dashboard, PIP, JD
- Visual: Golden screenshot diffs for focus/hover states

## CI Policy
- Block merge on any a11y error
- Generate junit + HTML reports and store artifacts
