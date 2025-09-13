# HRPro Architecture & Traceability

## 📌 Overview
This repo contains the **canonical documentation** and **quality gates** for the HRPro project.  
It aligns the **PRD**, **Architecture**, and **UI Framework** into unified Markdown, and enforces end-to-end traceability via CI.

Core components:
- **Unified Markdown docs** in `docs/PRD/`, `docs/Architecture/`, `docs/UI_Framework/`
- **Traceability matrix** in `docs/traceability/`
- **Validator script** in `tools/validate_traceability_md.py`
- **CI workflow** in `.github/workflows/traceability-check.yml`
- **Architecture Decision Records (ADRs)** in `docs/adr/`

---

## 📂 Repo Structure
```
.
├── docs/
│   ├── PRD/                  # Product Requirements Document
│   ├── Architecture/         # System Architecture
│   ├── UI_Framework/         # Design System & Components
│   ├── traceability/         # Traceability matrix + reports
│   ├── adr/                  # Architecture Decision Records (ADR-0001..0004)
│   └── versions/             # Changelogs & release notes
├── tools/
│   └── validate_traceability_md.py
└── .github/
    └── workflows/traceability-check.yml
```

---

## ✅ Architecture Decision Records
- **ADR-0001:** Advisor Export Trace  
- **ADR-0002:** Unified Markdown Format  
- **ADR-0003:** Traceability CI Enforcement  
- **ADR-0004:** Collaboration & Prompting Protocol  

All major repo conventions are documented here. **Read ADR-0004** before starting work — it defines the collaboration process and prompt templates.

---

## 🔄 Workflow

### 1. Documentation
- Author/edit PRD, Architecture, UI Framework only in Markdown.  
- Use numbered headings (`# 1`, `## 1.1`, …).  
- Use `§X.Y` references for traceability.

### 2. Traceability
- Update `docs/traceability/Traceability_v4.1_prefilled.xlsx` with:
  - Column D → PRD Reference
  - Column E → Architecture Mapping
  - Column F → UI Framework Mapping
- Keep references formatted like:
  ```
  PRD v4.0 §4.2 (Advisor) (docs/PRD/PRD_v4.0_unified_numbered.md)
  Arch v4.1 §4.2 (Streaming & UX Hooks) (docs/Architecture/Architecture_v4.1.md)
  UI v4.0 §6.3 (Components: Buttons) (docs/UI_Framework/UIFramework_v4.0_unified_numbered.md)
  ```

### 3. Local Validation
Run:
```bash
make autopatch-traceability   # fuzzy-fix legacy rows (skips PR-2)
make validate-traceability   # generate Traceability_link_check.csv
```

Both scripts autodiscover the latest PRD, Architecture and UI spec files.
Check `Traceability_link_check.csv` for remaining mismatches.

### 4. Continuous Integration
- Every PR triggers `.github/workflows/traceability-check.yml`.
- CI fails if any row in the matrix is not `OK`.
- The validator report is uploaded as a build artifact.

---

## 🛠️ Developer Guide

### Environment Setup
```bash
git clone https://github.com/matthewod11-stack/hrpro-architecture.git
cd hrpro-architecture
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # if provided
```

### Git Hygiene
- Do **not** commit `.venv/`, caches, or generated artifacts.
- `.gitignore` already excludes common cases.
- Commit with clear prefixes (`docs:`, `ci:`, `chore:`, …).

---

## 🤝 Collaboration Protocol
Defined in **ADR-0004**. Key points:
1. One step at a time — confirm each before moving on.
2. Explicit role framing (“You are acting as a repo maintainer”).
3. Always specify file paths.
4. Keep everything inside `~/Desktop/HRPro/architecture`.
5. Update traceability and run the validator before every push.

### New Chat Bootstrap Template
```
You are acting as my repo maintainer and product QA analyst.

Repo: ~/Desktop/HRPro/architecture

ADRs:
- ADR-0001: Advisor Export Trace
- ADR-0002: Unified Markdown Format
- ADR-0003: Traceability CI Enforcement
- ADR-0004: Collaboration & Prompting Protocol

Your job:
- Maintain alignment between PRD, Architecture, and UI Framework.
- Keep the traceability matrix valid.
- Provide outputs as files with download links when applicable.
- Work step by step (wait for me to say “done” before continuing).

First task: <insert here>
```

---

## 📊 Definition of Done

### Docs
- Headings numbered.
- References use `§X.Y` and resolve to real sections.
- Saved in correct folder.

### Traceability
- Matrix updated with PRD, Arch, UI refs.
- Validator passes locally.
- CI green on GitHub.

---

## 🧩 Next Steps
- Resolve current mismatches in `Traceability_v4.1_prefilled.xlsx`.
- Add ADR-0005+ as new architectural/process decisions are made.
- Polish Executive Overview exports for leadership.
