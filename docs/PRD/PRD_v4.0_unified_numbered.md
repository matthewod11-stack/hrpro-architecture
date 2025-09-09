# 1 Purpose
Project: HRPro — AI-First HR Consultant in a Box
## 1.1 1. Purpose
HRPro is a local-first AI toolkit that automates HR analysis and documentation for consultants, fractional HR leaders, startup founders, and in-house HR managers (<100 employees).
It is not an ATS/HRIS replacement. Instead, HRPro delivers AI-powered HR workflows that generate branded, client-ready outputs while running securely offline.
Goals:
Replace reliance on ad-hoc spreadsheets/docs with structured workflows.
Empower HR leaders with AI-driven insights, dashboards, and documents.
Provide a consistent, streamlined UI across all modules.
Act as both a consulting accelerator for FoundryHR and a standalone packaged product for clients.
## 1.2 2. Scope
### 1.2.1 In-Scope (v4.0)
UI Framework & Navigation
Shared design system (typography, color palette, component library).
Simplified navigation: Landing → Advisor → Dashboards/Builders → Exports.
Multi-client switcher in the top navigation bar.
Side Panels for contextual actions/filters.
Tabs as sanctioned pattern for subviews.
Modules (Pages)
Landing Page
“Ask your CPO” input.
Five color-coded module tiles:
Dashboard (Red #FF4D4F)
Engagement (Orange #FA8C16)
Performance (Green #52C41A)
PIP Builder (Blue #1890FF)
JD Builder (Purple #722ED1)
No redundant “Get Started” button.
Knowledge Advisor (Chat)
Chat UI with persistent context.
Advisor persona with structured methodology.
Responses always include sources + “Why this looks like this” tags.
Suggested prompts always visible.
Typing indicators + loading skeletons.
Dashboards
Dashboard: KPIs, charts with title, legend, tooltip, and AI Insights section.
Engagement: survey summaries, eNPS visualization, insights.
Performance: review cycle tracking, manager feedback, 9-box visualization.
Empty state: “Upload a CSV to see insights.”
Upload/Export actions top-right.
PIP Builder (Blue)
Stepper flow: Upload → Review Draft → Advisor Feedback → Export.
Rich text draft editor with inline AI suggestions.
Advisor chat panel with quick actions (e.g., Tighten, Measure).
JD Builder (Purple)
Stepper flow: Upload → Review Draft → Advisor Feedback → Export.
Structured sections: Overview, Responsibilities, Requirements, Nice-to-Haves.
Advisor chat panel with quick actions (e.g., Refine, Balance).
### 1.2.2 Out of Scope (v4.0)
Payroll, benefits, compliance.
ATS/HRIS integrations.
Cloud-hosted APIs (OpenAI, Anthropic).
Handling of real employee data.
### 1.2.3 Future Versions
Dark mode + SaaS theming tokens.
v5 (2026+): Preloaded appliance, enterprise telemetry, agent monitoring.
## 1.3 3. Users & Personas
FoundryHR Consultant (Power User): Needs multi-client switching, branded exports, speed.
Startup Founder (No HR yet): Needs plug-and-play templates, automation, and confidence.
Fractional HR Leader: Prioritizes repeatable workflows and sandbox mode.
In-House HR Manager (<100 employees): Needs augmentation, not replacement; prioritizes simplicity.
## 1.4 4. Functional Requirements
### 1.4.4 Navigation
Top Nav Bar: HRPro logo, client switcher, quick access icons.
Breadcrumbs: Used for multi-step flows (e.g., Home › PIP Builder › Review Draft).
Side Panels: Collapsible filters and contextual actions.
Tabs: For subviews inside dashboards/builders.
### 1.4.5 Advisor
Chat history preserved (user right, advisor left).
Responses include sources + explainability tags.
Typing indicators + loading skeletons.
Failure states: Retry banners for advisor errors.
### 1.4.6 Dashboards
Input: CSV upload.
Outputs: Charts with title, legend, tooltip, and AI Insights section.
Empty/error states with suggested prompts.
Exports: PDF/CSV/Excel, fully branded.
### 1.4.7 PIP Builder
Stepper: Upload → Review Draft → Advisor Feedback → Export.
Rich text editor with inline Advisor suggestions.
Advisor chat panel with contextual quick actions.
### 1.4.8 JD Builder
Stepper: Upload → Review Draft → Advisor Feedback → Export.
Structured sections with Advisor quick actions.
## 1.5 5. Non-Functional Requirements
### 1.5.9 Ease of Use
Non-technical users complete workflows unaided.
### 1.5.10 Offline-First
No external API calls; local processing only.
### 1.5.11 Performance
Dashboards render in <10s with 1k rows.
### 1.5.12 Security
Per-company sandbox workspaces.
### 1.5.13 Accessibility (Enforceable)
Contrast ratio ≥4.5:1.
Predictable tab order; Enter=submit, Esc=close.
ARIA roles: nav, main, form, button, alert.
Focus ring: 2px Indigo-300.
### 1.5.14 Scalability
Modular components, reusable layouts.
Hooks for SaaS theming and enterprise telemetry.
## 1.6 6. Design Tokens & Components
### 1.6.15 Typography
Font: Inter (primary), Inter + Source Serif Pro for exports.
Hierarchy: H1 28px Bold, H2 22px Semi-bold, H3 18px Medium, Body 16px, Small 14px, Caption 12px.
### 1.6.16 Color System
Modules: Red (Dashboard), Orange (Engagement), Green (Performance), Blue (PIP), Purple (JD).
Neutrals: Background #F5F5F5, Text Primary #262626, Secondary #595959, Borders #D9D9D9.
Semantic: Success #16A34A, Warning #D97706, Danger #DC2626.
### 1.6.17 Components
Buttons: Primary (solid), Secondary (outlined), Tertiary (text-only).
Inputs: 6px radius, placeholder #8C8C8C, focus with module-color glow.
Cards: 12px radius, shadow, padding 16–24px.
Modals: Max-width 600px, elevation-2 shadow.
Breadcrumbs, tabs, chips/tags, toasts included.
### 1.6.18 Interaction Patterns
Hover elevation + shadow.
Transitions: 200ms ease-in-out.
Inline error handling + toast alerts.
Skeleton loaders, shimmer text, retry banners.
### 1.6.19 Spacing & Grid
12-column grid, 4-pt scale (4–64).
Section padding: 32px; card padding: 16–24px.
## 1.7 7. Architecture & Tech Stack
Language: Python 3.11.
UI: Streamlit (modules).
Advisor: FastAPI + Ollama + Chroma (RAG).
Core Libraries: pandas, matplotlib/plotly, openpyxl, reportlab.
Design System: UI Framework v4.0 enforced.
Enhancements:
Unified insight pipeline (Advisor + Dashboards).
Logging + eval harness for citations, hallucinations, latency.
Performance safeguards (caching, retries).
## 1.8 8. Prompt & Persona Layer
Personas: Product Manager, UX Designer, Staff Engineer, Implementation Engineer, QA Reviewer.
All Advisor outputs must include transparency + sources.
## 1.9 9. Documentation & Ops
Living spec log (docs/spec_log.md).
Module guides (docs/module_guides/).
ADR folder for architectural decisions.
Design kit (typography, color, components).
Install guide: one-click installer + setup docs.
## 1.10 10. Risks & Mitigations
Complex dashboards → Start with high-level KPIs, iterate.
Hallucinations → Require citations + eval harness + fallback responses.
UI drift → Enforce v4.0 framework as single source of truth.
Scope creep → Limit to v4.0 MVP features, backlog future ideas.
## 1.11 11. Success Metrics
≥80% of users complete tasks unaided.
≥70% of users rate Advisor “trust” ≥4/5.
≥95% of Advisor responses include ≥1 cited source.
Dashboards render <10s with 1k rows.
JD/PIP exports meet branding rules (logo, header, footer, watermark).
Hallucination rate <15%.
≥60% of users report UI/navigation “very easy to use.”
## 1.12 12. Roadmap
Phase 1 (Weeks 1–2): Finalize v4.0 design tokens, implement landing + Advisor.
 Phase 2 (Weeks 3–6): Build dashboards (Dashboard, Engagement, Performance).
 Phase 3 (Weeks 7–10): Implement PIP + JD Builders.
 Phase 4 (Weeks 11–12): Usability testing, export polish, branding review.
 Future (2026+): Dark mode, SaaS theming, enterprise telemetry.