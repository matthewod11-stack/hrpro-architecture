# HRPro — Architecture v4.1

> Single source of truth architecture aligned to **PRD v4.0** and **UI Framework v4.0**. Offline‑first, local processing, per‑client workspaces. *This version applies all QA findings and removes prior contradictions.*

---

## 0) Document Control & Versioning
- **Title:** HRPro — Architecture v4.1  
- **Version:** 4.1  
- **Status:** Draft → Review → Final  
- **Owners:** Systems Architect, Staff Engineer  
- **Related Docs:** PRD v4.0, UI Framework v4.0, QA Review (v4.0), Architecture v3.0 (historical)
- **Footer (all pages):** *Architecture v4.1 • HRPro*  

---

## 1) System Overview
**End‑to‑end flow:** **Landing → Advisor → Dashboards/Builders → Export**.  
**Operating model:** Offline‑first; all calls target localhost services; no external APIs.  
**Data isolation:** Per‑client workspaces; namespaced storage and configs.

### 1.1 Conceptual Diagram (updated)
```mermaid
graph TD
  subgraph Experience Layer (UI)
    A[Landing]
    B[Advisor Chat]
    C[Dashboards: Dashboard/Engagement/Performance]
    D[Builders: PIP / JD]
    E[Export UX]
    PR[Prompt Rail (Suggested Prompts)]
  end

  subgraph Intelligence Layer (Advisor Service)
    AS[FastAPI - Advisor API]
    RAG[Retrieval & Chunking]
    LLM[Ollama Local LLM]
    P[Post-process → JSON Contract]
  end

  subgraph Data & Deliverables Layer
    STG[Data Staging]
    TRANS[Transforms & KPIs]
    CHRT[Chart Models (incl. eNPS, 9-box)]
    KB[Local KB / Vector Store]
    EXP[Export Engine (PDF/XLSX/CSV)]
    CFG[Client Configs & Branding]
    EVT[Telemetry & KPIs]
  end

  A --> B
  A --> C
  A --> D
  B <--> AS
  PR --- B
  C -->|"Ask your CPO about this page"| AS
  D <--> AS
  C --> TRANS --> CHRT
  D --> EXP
  STG --> TRANS
  AS --> RAG --> KB
  AS --> LLM --> P
  P --> B
  P --> D
  CHRT --> E
  CFG -.-> EXP
  CFG -.-> UI((Design Tokens))
  UI -.-> EVT
  AS -.-> EVT
  TRANS -.-> EVT
```

---

## 2) Design Tokens (Authoritative Appendix)
> **Source of truth for FE and Export Engine.**

### 2.1 Module Colors (hex)
- **Dashboard:** `#FF4D4F`
- **Engagement:** `#FA8C16`
- **Performance:** `#52C41A`
- **PIP Builder:** `#1890FF`
- **JD Builder:** `#722ED1`

### 2.2 Neutrals & Semantic
- **Background:** `#F5F5F5`
- **Text / Primary:** `#262626`, **Secondary:** `#595959`
- **Borders:** `#D9D9D9`
- **Success:** `#16A34A`  
- **Warning:** `#D97706`  
- **Danger:** `#DC2626`

### 2.3 Focus, Typography, Radii/Spacing
- **Focus Ring:** **2px Indigo‑300** (as defined in UI Framework tokens); applied to all focusable components; visible at 200% zoom.
- **Typography:** UI **Inter**; Exports **Inter + Source Serif Pro** (see §7 for embedding).
- **Radii:** Inputs **6px**, Cards **12px**, Modals **12px** (tokenized: `radius.sm=6`, `radius.md=12`).
- **Spacing:** 4‑pt scale → `4, 8, 12, 16, 24, 32, 48, 64` (tokens `space.xs..xxl`).

**Enforcement:** FE components and Export templates import these tokens; CI includes lint for contrast and token usage.

---

## 3) Frontend Architecture

### 3.1 Accessibility Playbook (enforceable)
- **Keyboard:** `Enter = submit`, `Esc = close/cancel`; predictable **tab order** (top‑to‑bottom, left‑to‑right).  
- **ARIA:** Required roles: `nav`, `main`, `form`, `button`, `tab`, `tabpanel`, `alert`.
- **Focus:** Global focus ring per tokens; no focus trapping except in modals.
- **QA Checklist (CI):** Automated tests verify shortcuts, tab order across primary flows, contrast ≥4.5:1, and ARIA on key components.

### 3.2 Interaction Contracts
- **Load & Error:** Skeleton loaders, shimmer text, inline errors with toasts, **retry banners** on API failure.
- **Typing Indicators:** Implemented via **streaming** (SSE) from Advisor; FE renders token stream + animated indicator.
- **Toasts:** Success, warning, error; auto‑dismiss with manual close.

### 3.3 App Shell & Sanctioned Patterns
- **Prompt Rail (persistent):** Always‑visible suggested prompts on Advisor and module pages.
- **Side Panels:** Contextual filters/actions; collapsible; keyboard accessible.
- **Tabs:** For subviews; arrow‑key navigation; `aria-selected` state.
- **Empty State (dashboards):** Copy: **“Upload a CSV to see insights.”** with primary action → Upload.

---

## 4) Advisor Service (FastAPI)

### 4.1 Response Contract
Structured JSON: `{ summary, findings[], actions[], insights[], citations[], explainability_tag, trace_id }`.

### 4.2 Streaming & UX Hooks
- **SSE:** Advisor always streams tokens for typing indicator; FE aggregates to final JSON.

### 4.3 Personas & Quick Actions
- **Persona Hook:** `persona?: string` (e.g., `"cpo"`, `"pm"`).
- **Quick Actions:** `quick_action?: "TIGHTEN"|"MEASURE"|"REFINE"|"BALANCE"` for Builder‑context prompts.

### 4.4 Guardrails & Redaction
Prompt‑injection filters; PII redaction at ingest; response length caps; trace IDs.

**Endpoint:** `POST /v1/advisor/answer`  
**Request (example):**
```json
{
  "prompt": "Summarize performance trends and suggest a plan.",
  "module": "dashboard",
  "persona": "cpo",
  "quick_action": "MEASURE",
  "page_stats": {"kpis": [{"name":"Attrition","value":12.3,"period":"L12M"}]}
}
```
**Final Response (shape):** *Advisor contract above.*

---

## 5) Dashboards Service

### 5.1 Chart Models & Data Contracts
**eNPS**  
- **Scale:** −100..100; **Formula:** `%Promoters (9–10) − %Detractors (0–6)`; Passives ignored.  
- **Payload (request):**
```json
{
  "chart_type": "enps",
  "k": "<upload_fingerprint>",
  "bins": {"promoter_min": 9, "detractor_max": 6}
}
```
- **Response (example):**
```json
{
  "title": "eNPS (Last Cycle)",
  "value": 34,
  "counts": {"promoters": 120, "passives": 58, "detractors": 47},
  "series": [{"label":"Score","points":[{"x":"2024-Q4","y":28},{"x":"2025-Q1","y":34}]}]
}
```

**9‑box**  
- **Axes:** **Performance** × **Potential**; 3×3 grid (Low/Med/High).  
- **Bins:** default thresholds `{low: 0–0.33, med: 0.34–0.66, high: 0.67–1.0}` (overridable).  
- **Payload (request):**
```json
{
  "chart_type": "nine_box",
  "k": "<upload_fingerprint>",
  "thresholds": {"low": 0.33, "high": 0.67}
}
```
- **Response (example):**
```json
{
  "title": "9-box Distribution",
  "grid": {"rows": ["High","Medium","Low"], "cols": ["Low","Medium","High"]},
  "cells": [
    {"row":"High","col":"High","count":12},
    {"row":"High","col":"Medium","count":8}
  ],
  "legend": [{"label":"Employees","value":120}]
}
```

### 5.2 Endpoint Variants
- `POST /v1/data/charts` → `{ chart_type: "enps"|"nine_box"|..., k, ... }` returns chart‑ready JSON.

---

## 6) Builders (PIP/JD) — State Machines
**Flow:** Upload → Draft → Advisor Feedback → Export.  
**FE Responsibilities:** stepper UI, validation, inline AI suggestions, audit trail of edits.  
**BE Responsibilities:** `generate-draft`, apply quick actions, persist intermediate drafts in client namespace.  
**Audit Logs:** timestamp, user action, quick_action, diff summary.

---

## 7) Export Engine
**Branding Rules:**  
- **Header:** HRPro logo (left), **Client Name** (right).  
- **Footer:** “**Generated with HRPro • Confidential • {timestamp}**”.  
- **Watermark:** “Sandbox” when in non‑production datasets.  
- **Module Color Persistence:** Section accents use current module color token.

**Fonts (offline embedding):**  
- UI exports use **Inter**; long‑form documents may mix **Inter + Source Serif Pro**.  
- Bundle font files locally; document licensing; provide fallbacks; pre‑embed subsets for PDF.

**APIs:** `POST /v1/export/pdf`, `/xlsx`, `/csv` (inputs: content, branding config, assets; outputs: file path + hash manifest).

---

## 8) Data Layer & Security
- **Namespaces:** `/data/{client}/...` and `/config/{client}/...` with strict file permissions.  
- **Redaction:** On ingest; drop/obfuscate obvious PII columns.  
- **Retention:** Auto‑clean staging; immutable exports with manifest.  
- **No External Calls:** All processing local; model health checked at startup.

---

## 9) Telemetry & KPIs
**Event Schema (selected):**
- `advisor_response_has_citation: {trace_id, has_citation: bool}`  
- `time_to_first_answer_ms: {trace_id, ms}`  
- `dashboard_render_ms: {fingerprint, ms}`

**Rollups & Thresholds:**  
- **Trust:** ≥95% Advisor responses include ≥1 citation.  
- **Performance:** TTFA p95 budget; dashboards render <10s for ~1k rows.  
- **Exports:** branding compliance checks logged.

**Surfacing:** Minimal local dashboard; logs ship to file; future hook for enterprise telemetry.

---

## 10) Risks & Mitigations
- **Visual spec drift (eNPS/9‑box):** Enforce chart contracts via §5; CI schema checks.
- **A11y regressions:** CI tests for Enter/Esc, tab order, ARIA presence, contrast.
- **Trust KPI not measurable:** Require citation telemetry event; fail CI if missing.
- **Export brand inconsistency:** Font‑embedding precheck; watermark enforcement in sandbox.

---

## 11) API Updates (v4.1)

### 11.1 `POST /v1/advisor/answer`
**Params:** `persona?: string`, `quick_action?: "TIGHTEN"|"MEASURE"|"REFINE"|"BALANCE"`
**Request:** *(see §4.4 example)*
**Streamed Tokens:** SSE channel emits JSON frames (`start`, `delta`, `final`, `ping`). FE aggregates `delta` events and reads the `final` payload for the complete answer.

### 11.2 `POST /v1/data/charts`
**Body:** `{ chart_type: "enps"|"nine_box"|..., k: string, ... }`  
**Examples:** *(see §5.1)*

---

## 12) Acceptance Criteria (Do not mark v4.1 complete unless all pass)
- **Tokens:** exact hexes, focus ring, typefaces, spacing/radii **present and referenced** by FE & Export.  
- **A11y:** Enter/Esc shortcuts, tab‑order policy, ARIA examples, CI test notes **documented**.  
- **Advisor UX:** **typing indicators via streaming**; Prompt Rail mandated.  
- **Dashboards:** **eNPS & 9‑box contracts** with example payloads.  
- **Exports:** font‑embedding strategy & branding layout rules **documented**.  
- **Telemetry:** events & rollups compute PRD KPIs.  
- **Naming/versioning:** header, footer, anchors show **Architecture v4.1** consistently.

---

## 13) Appendices
**A. Design Tokens Table** — full palette, typography scale, radii, spacing.  
**B. Accessibility Playbook** — shortcuts, tab order, ARIA examples, CI checklist.  
**C. Chart Specs** — eNPS (formula/thresholds), 9‑box (axes/bins/labels).  
**D. Font Embedding** — bundling, licensing, PDF subset embedding, fallbacks.  
**E. Telemetry Schema** — event fields, sampling, local dashboard.

---

## 14) Diff Summary (v4.1 vs previous)
- **Naming fixed:** All titles/footers/anchors updated to **v4.1**.
- **Token specificity added:** Exact module hexes, neutrals/semantic, focus ring, typography, radii/spacing.
- **A11y codified:** Shortcuts, tab order policy, ARIA examples, CI QA checklist.
- **Advisor UX upgraded:** SSE streaming + typing indicators; Prompt Rail mandated.
- **Dashboards formalized:** eNPS and 9‑box contracts with endpoint variants and examples.
- **Exports tightened:** Branding layout and **Inter + Source Serif Pro** embedding offline.
- **Telemetry defined:** Events + thresholds to compute PRD KPIs.
- **Risks/mitigations updated** and **acceptance criteria** added to gate release.

