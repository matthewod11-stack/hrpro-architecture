# 1 Purpose
## 1.1 1. Purpose
This document establishes the single source of truth for the HRPro UI. It reflects the latest designs exported from Figma (.make file) and incorporates all corrections identified in the QA review. It consolidates design principles, implementation details, accessibility standards, and interaction patterns into a clean, aligned framework.
## 1.2 2. Design Principles
Simplicity First – Clear, uncluttered layouts prioritize usability and reduce cognitive load.
Consistency Across Modules – Shared typography, spacing, and interaction patterns provide a cohesive experience.
Local-First Utility – Designs support offline-first workflows with lightweight UI components.
Scalable Modularity – Each module follows the same structural grid and component hierarchy.
Transparency & Trust – Advisor outputs always include sources, citations, and bias checks (“Why this looks like this” tags).
Accessibility & Inclusivity – WCAG AA standards, ARIA roles, keyboard-first navigation.
Brand Integrity – Consistent visual identity with HRPro logo, watermarks, and professional exports.
## 1.3 3. Layout & Navigation
### 1.3.1 3.1 Global Layout
Top Navigation Bar: Persistent HRPro logo, client switcher, quick access icons.
Primary Content Area: Central workspace for each module.
Side Panel (where applicable): Collapsible filters, contextual actions.
Bottom Notifications: Toasts for success, warning, error.
### 1.3.2 3.2 Navigation
Home / Landing Page: Entry point with AI advisor box ("Ask your CPO") and five color-coded module tiles.
Module Access: Dashboard, Engagement, Performance, PIP Builder, JD Builder.
Breadcrumbs: Present in multi-step flows (e.g., Home › PIP Builder › Review Draft).
Tabs: Used for sub-views within dashboards and builders.
## 1.4 4. Typography
Primary Font: Inter (Sans-serif)
Export Font Pairing: Inter + Source Serif Pro (for professional PDF exports).
Weights: 400, 500, 600, 700
Hierarchy:
H1: 28px Bold – Page/module titles
H2: 22px Semi-bold – Section headers
H3: 18px Medium – Sub-sections
Body: 16px Regular – Standard text
Small: 14px Regular – Secondary info, labels
Caption: 12px – Annotations, tooltips
## 1.5 5. Color System
Module Palette:
Red (#FF4D4F) → Dashboard
Orange (#FA8C16) → Engagement
Green (#52C41A) → Performance
Blue (#1890FF) → PIP Builder
Purple (#722ED1) → JD Builder
Neutrals:
Background: #F5F5F5
Text Primary: #262626
Text Secondary: #595959
Borders: #D9D9D9
Semantic Colors:
Success: #16A34A
Warning: #D97706
Danger: #DC2626
## 1.6 6. Components
### 1.6.3 6.1 Buttons
Primary: Solid, module color background, white text, rounded corners (8px).
Secondary: White background, module color border + text.
Tertiary: Text-only.
### 1.6.4 6.2 Inputs
Rounded (6px)
Placeholder text: #8C8C8C
Focus: Module color border with 2px glow
### 1.6.5 6.3 Cards
Rounded (12px), soft shadow, padding 16–24px
Chart cards include title, legend, tooltip, and AI Insights section.
### 1.6.6 6.4 Modals
Centered, max-width 600px
Elevation-2 shadow
Primary CTA button styled with module color
### 1.6.7 6.5 Additional Components
Breadcrumbs: Icon + label, active state bolded.
Tabs: For switching between module views.
Chips/Tags: Used for filters and AI quick prompts.
Toasts: Temporary bottom notifications for status changes.
## 1.7 7. Module Guidelines
### 1.7.8 7.1 Dashboard
High-level KPIs, charts with legends and AI insights
Upload/Export actions top-right
Empty state: “Upload a CSV to see insights.”
### 1.7.9 7.2 Engagement
Employee survey summaries, eNPS visualization
Actionable insights panel
Suggested prompts appear in empty state
### 1.7.10 7.3 Performance
Review cycle progress, manager feedback forms, 9-box visualization
State handling for loading and error
### 1.7.11 7.4 PIP Builder
Stepper Flow: Upload → Review Draft → Advisor Feedback → Export
Draft editor: Rich text with inline Advisor suggestions
Advisor chat panel: Context-specific quick actions (e.g., Tighten, Measure)
### 1.7.12 7.5 JD Builder
Stepper Flow: Upload → Review Draft → Advisor Feedback → Export
Structured sections: Overview, Responsibilities, Requirements, Nice-to-Haves
Advisor chat panel: Quick actions (e.g., Refine, Balance)
### 1.7.13 7.6 Advisor Page
Chat history preserved (user right, advisor left)
Advisor responses include sources + “Why this looks like this” tags
Suggested prompts always visible
Typing indicators and loading skeletons
## 1.8 8. Interaction Patterns
Hover States: Slight elevation + shadow for clickable items.
Transitions: 200ms ease-in-out.
Error Handling: Inline messages + toast alerts.
Transparency: All Advisor outputs cite sources and reasoning.
Empty States: Suggested prompts, onboarding cues.
Loading States: Skeleton cards, shimmer text, “Advisor is thinking…” dots.
Failure States: Retry banners for uploads/advisor requests.
## 1.9 9. Spacing & Grid
Grid: 12-column responsive grid (desktop ≥1200px, tablet 768–1199px, mobile ≤767px)
Spacing System: 4pt base grid → 4, 8, 12, 16, 24, 32, 48, 64
Standard Padding:
Section: 32px
Card: 16–24px
Element spacing: multiples of 4pt
## 1.10 10. Export & Branding
HRPro logo top-left in-app, watermark on exports
Export headers: HRPro logo left, Client name right
Export footers: “Generated with HRPro • Confidential • Timestamp”
PDF exports use Indigo headers, Gray-800 body text
Module color-coding persists in exports
## 1.11 11. Accessibility Standards
All text/background ≥ 4.5:1 contrast ratio
Keyboard navigation: predictable tab order, Enter = submit, Esc = close
ARIA roles: nav, main, form, button, alert
Focus rings: 2px Indigo-300 for all interactive elements
## 1.12 12. Versioning
v1.0–2.0: Original framework + incremental updates
v3.0: Consolidated framework with simplified modules
v4.0: Fully corrected version aligned with Figma .make + QA review
Next Steps: Dark mode design, SaaS theming tokens
## 1.13 13. Appendix
Reference: Based on HRPro UI Framework v2.0 + v3.0
Updated From: Figma .make export (Sept 2025)
QA Input: Consolidated from Review Report (v3.0 vs .make)