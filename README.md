## Waiving legacy rows

To suppress legacy traceability failures in CI:

- Add legacy feature names (one per line, case-insensitive) to `tools/legacy_waive_list.txt`.
- Run `make waive-legacy` to tag those rows in the traceability matrix with `legacy-waived`.
- CI uses `make trace-ci` to enforce PR-2 and future rows strictly, ignoring legacy-waived failures.
## Traceability

Canonical spec paths:

- PRD: `docs/PRD/PRD_v4.0_unified_numbered.md`
- Arch: `docs/Architecture/Architecture_v4.1_unified.md`
- UI: `docs/UIFramework/UIFramework_v4.0_unified_numbered.md`

If the UI file moves, run `make ui-canon` to restore the canonical path, or rely on auto-discovery in `trace-legacy-*`/`trace-fix` workflows.
## ⚡ Quickstart: 3-minute demo
1) API: `uvicorn app.api.main:app --reload --port 8000`
### Troubleshooting
- **API not running**: If you see 502/timeout, ensure `uvicorn` API is started and reachable at `localhost:8000`.
- **No citations**: Expected if the knowledge base is empty. See the Telemetry page for recent events.
- **Export path not found**: Check write permissions under `artifacts/`.

### UI shortcut
You can run the UI with:
```bash
make ui
## 📌 Overview
This repo contains the **canonical documentation** and **quality gates** for the HRPro project.  
It aligns the **PRD**, **Architecture**, and **UI Framework** into unified Markdown, and enforces end-to-end traceability via CI.
Core components:
- **Unified Markdown docs** in `docs/PRD/`, `docs/Architecture/`, `docs/UI_Framework/`
- **Traceability matrix** in `docs/traceability/`
- **CI workflow** in `.github/workflows/traceability-check.yml`
- **Architecture Decision Records (ADRs)** in `docs/adr/`

---

## 📂 Repo Structure
```
.
├── docs/
│   ├── PRD/                  # Product Requirements Document
│   ├── adr/                  # Architecture Decision Records (ADR-0001..0004)
│   └── versions/             # Changelogs & release notes
├── tools/
│   └── validate_traceability_md.py
└── .github/
    └── workflows/traceability-check.yml
- **ADR-0002:** Unified Markdown Format  

- **ADR-0003:** Traceability CI Enforcement  

- **ADR-0005:** Traceability & Validation Expansion

All major repo conventions are documented here. **Read ADR-0004** before starting work — it defines the collaboration process and prompt templates.
|-----|-------|----------------|
| ADR-0001 | Advisor Export Trace | Establishes export branding, footer rules, and traceable sources in artifacts. |
| ADR-0002 | Unified Markdown Format | Single format + numbered headings for PRD/Arch/UI to enable §-style traceability. |

| ADR-0003 | Traceability CI Enforcement | Fails CI when matrix links don’t resolve to real § sections. |

| ADR-0004 | Collaboration & Prompting Protocol | Roles, prompts, and step-by-step workflow for contributions. |
## 🔄 Workflow



### 2. Traceability

  - Column D → PRD Reference

- Keep references formatted like:

  ```
  PRD v4.0 §4.2 (Advisor) (docs/PRD/PRD_v4.0_unified_numbered.md)

  Arch v4.1 §4.2 (Streaming & UX Hooks) (docs/Architecture/Architecture_v4.1.md)


```bash

python tools/validate_traceability_md.py   --prd=docs/PRD/PRD_v4.0_unified_numbered.md   --arch=docs/Architecture/Architecture_v4.1.md   --ui=docs/UI_Framework/UIFramework_v4.0_unified_numbered.md   --trace=docs/traceability/Traceability_v4.1_prefilled.xlsx   --out=docs/traceability/Traceability_link_check.csv

## 🛠️ Developer Guide


### Environment Setup


git clone https://github.com/matthewod11-stack/hrpro-architecture.git

cd hrpro-architecture

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt   # if provided
```


### Git Hygiene

- Do **not** commit `.venv/`, caches, or generated artifacts.


---



## 🤝 Collaboration Protocol


- Labels are auto-synced from `.github/labels.yml` via CI or script.
4. Keep everything inside `~/Desktop/HRPro/architecture`.
5. Update traceability and run the validator before every push.


### Where to Start (2-minute bootstrap)


3. Run local validator:

python tools/validate_traceability_md.py \
--prd=docs/PRD/PRD_v4.0_unified_numbered.md \

--ui=docs/UI_Framework/UIFramework_v4.0_unified_numbered.md \
--trace=docs/traceability/Traceability_v4.1_prefilled.xlsx \
--out=docs/traceability/Traceability_link_check.csv


4. Open the CSV to fix any broken § references, then commit.




```bash

python tools/traceability_fix_refs.py --in docs/traceability/Traceability_v4.1_prefilled.xlsx --out docs/traceability/Traceability_v4.1_fixed.xlsx


- **Status:** Implements ADR-0005 (Traceability & Validation Expansion).
- **Notes:** Safe import, test-covered, and validated by `pytest -k traceability_fix_refs`.


### 🛠️ Traceability Fix Tool

For legacy or malformed § references in the traceability matrix, use the fixer script:

```bash
python tools/traceability_fix_refs.py --in docs/traceability/Traceability_v4.1_prefilled.xlsx --out docs/traceability/Traceability_v4.1_fixed.xlsx
```

- **Purpose:** Normalize §X.Y references so they map cleanly to PRD/Arch/UI docs.
- **Status:** Implements ADR-0005 (Traceability & Validation Expansion).
- **Notes:** Safe import, test-covered, and validated by `pytest -k traceability_fix_refs`.


### 🛠️ Traceability Fix Tool
For legacy or malformed § references in the traceability matrix, use the fixer script:

```bash
python tools/traceability_fix_refs.py --in docs/traceability/Traceability_v4.1_prefilled.xlsx --out docs/traceability/Traceability_v4.1_fixed.xlsx
```

- **Purpose:** Normalize §X.Y references so they map cleanly to PRD/Arch/UI docs.
- **Status:** Implements ADR-0005 (Traceability & Validation Expansion).
- **Notes:** Safe import, test-covered, and validated by `pytest -k traceability_fix_refs`.

New Chat Bootstrap Template
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

## ⚡ Quickstart: 3-minute demo
1) Start services (two terminals):
   - API: `uvicorn app.api.main:app --reload --port 8000`
   - UI:  `streamlit run ui/Home.py`  (or your entrypoint)
2) Run the end-to-end smoke:
   ```bash
   make demo
   ```

You should see: E2E OK • trace=adv_... • citations=N • export=artifacts/demo/...
3) Open the UI → ask a question → see streaming + citations → click Export Summary.
4) Telemetry page: ui/pages/99_Telemetry.py shows Advisor & Export events.

---

## 🧩 Next Steps
- Resolve current mismatches in `Traceability_v4.1_prefilled.xlsx`.
- Add ADR-0005+ as new architectural/process decisions are made. (✅ ADR-0005 added)
- Polish Executive Overview exports for leadership.

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

### 🔧 Dev Setup (format/lint)
```bash
pip install -r requirements-dev.txt
pre-commit install           # one-time
make format && make lint     # or: pre-commit run --all-files
```

Formatting is by Black (88 cols). Lint + import sorting by Ruff. CI runs pre-commit on every PR/push.

---

#### Loop-busting checklist

- Same **line-length** (88) in both Black and Ruff.
- Only **one** formatter (Black). Do **not** enable `ruff-format`.
- Ruff fixes imports (`I`) and safe lints only (`--fix`); no style that conflicts with Black.
- Exclude generated/output dirs to avoid needless churn.

---

## 📥 Data Ingestion & Corpus
This repo includes a local-first CSV loader and a reproducible corpus builder.

**CSV ingestion (perf-guarded)**
- Loader: `app/core/csv_loader.py` (streaming `load_iter`, batch `load_batch`)
- Settings: `CSV_CHUNK_ROWS`, `CSV_MAX_ROWS` in `app/core/settings.py`
- Perf tests: `tests/test_csv_perf.py` (1k/5k rows under generous thresholds)
- Generate fake HR CSVs for testing:
  ```bash
  python tools/generate_fake_hr_csv.py tmp/hr.csv 5000
  ```

**Corpus builder CLI**
- Script: `tools/build_corpus.py`
- Usage (Markdown):
  ```bash
  python tools/build_corpus.py --in ./samples --out ./corpus_md --format md
  # writes INDEX.md and one .md per input file
  ```
- Usage (JSONL):
  ```bash
  python tools/build_corpus.py --in ./samples --out ./corpus_jsonl --format jsonl
  # writes corpus.jsonl (one JSON object per line)
  ```

## 🔒 Privacy & PII Redaction
PII redaction is **local**, regex-based, and enabled by default.
- Flag: `REDACT_PII=true|false` (default **true**) in `app/core/settings.py`
- Applies to **streamed deltas**, **final answers**, and **exports**
- Patterns masked: emails (`***@***.***`), phones (`***-***-****`), SSN (`***-**-****`)
- Telemetry includes `pii_redactions` count per trace

## 📈 Telemetry
Use the unified telemetry service in `app/services/telemetry.py`.

```python
from app.services import telemetry

telemetry.emit("advisor", {"event": "start", "trace_id": "t1"})
rows = telemetry.tail("advisor", 100)
```

Events are stored as JSONL files under `telemetry/<name>.jsonl`. The module also
provides `tail` to read recent events and `rotate` to archive large logs.
