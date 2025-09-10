# ADR-0004: Collaboration & Prompting Protocol (LLM Assistant)

## Status
Accepted (2025-09-10)

## Context
We now maintain PRD, Architecture, and UI Framework as **canonical Markdown** with a CI-enforced traceability matrix.
Progress consistently accelerates when instructions to the assistant are **specific, scoped, and stepwise**.
This ADR captures a repeatable **collaboration playbook** so future sessions (and contributors) can work quickly and predictably.

## Decision
Adopt the following **working protocol** when collaborating with the assistant:
- **Role framing:** Begin each session by stating the role (e.g., repo maintainer, QA analyst, DevOps engineer).
- **One step at a time:** Ask for a single, concrete step; confirm results before continuing.
- **Explicit file flow:** Always say where files live and where new artifacts should be written.
- **Canonical paths:** Use the repo as the anchor: `~/Desktop/HRPro/architecture` with the standard `docs/*` and `tools/*` layout.
- **Traceability first:** Prefer numbered headings and `§X[.Y]` references. Keep the matrix current.
- **No background work:** Results must be produced in the response (download links for generated files); do not “wait” for future work.
- **CI as gate:** Run the validator locally, then push and check GitHub Actions before declaring a task done.

## Operating Guidelines (Expanded)
1) **Be Specific and One‑Step‑at‑a‑Time**  
   **Good:** “Here is the current PRD unified doc. Please add numbering to all headings based on the canonical outline.”  
   **Bad:** “Fix the PRD, Architecture, UI, and validator.” (too broad)

2) **Always Provide Context**  
   - Upload the file or reference the exact repo path.  
   - State the expected output (e.g., “return a .md file”, “create a .yml workflow”, “shell commands”).

3) **Use Explicit Task Framing**  
   Start prompts like:  
   - “You are acting as a **product QA analyst**.”  
   - “You are acting as a **repo maintainer**.”  
   - “You are acting as a **DevOps engineer**.”

4) **Keep File Flow Clear**  
   - Tell me precisely where files should go (e.g., `docs/PRD/PRD_v4.0_unified_numbered.md`).  
   - I’ll assume those locations are canonical and structure outputs accordingly.

5) **Confirm Before We Move**  
   - After I give you a step (e.g., “run this in terminal”), execute it and reply **“done.”**  
   - This keeps us in lockstep and avoids rework.

6) **Break Down Multi‑Step Processes**  
   - For flows like *update doc → validate → commit → push → CI check*, we will do steps one by one.  
   - Tell me “**ok, step 2 now**” or “**pause, let’s review output**.”

7) **Use the Repo as Anchor**  
   - Keep everything under `~/Desktop/HRPro/architecture`.  
   - If adding a new doc, specify the subfolder: `docs/PRD`, `docs/Architecture`, `docs/UI_Framework`, `docs/traceability`, `docs/adr`, `docs/versions`.

## New‑Chat Bootstrap Template
Paste this at the start of a new session (attach ADRs if relevant):

```
You are acting as my repo maintainer and product QA analyst.

Repo: ~/Desktop/HRPro/architecture

ADRs (canonical process): 
- ADR-0001: Advisor Export Trace
- ADR-0002: Unified Markdown Format
- ADR-0003: Traceability CI Enforcement
- ADR-0004: Collaboration & Prompting Protocol (this document)

Your job:
- Maintain alignment between PRD, Architecture, and UI Framework.
- Keep the traceability matrix valid; run the validator and summarize mismatches.
- Provide outputs as files with download links when applicable.
- Work step by step (wait for me to say “done” before continuing).

First task: <insert the one concrete step you want>
```

## Prompt Templates
**Repo Maintainer:**  
“Act as a repo maintainer. Open `{path}` and {action}. Write back the updated file and tell me where to place it.”

**QA Analyst (Traceability):**  
“Act as a QA analyst. Validate `docs/traceability/Traceability_v4.1_prefilled.xlsx` against the unified docs and produce `Traceability_link_check.csv` with a short summary.”

**DevOps (CI):**  
“Act as a DevOps engineer. Generate a GitHub Actions workflow at `.github/workflows/<name>.yml` that runs `{command}` and fails on non‑zero. Provide the file.”

## Definition of Done (DoD) Checklists
**Docs change DoD**
- [ ] Headings are numbered (`# 1`, `## 1.1`, …).
- [ ] Inline references use `§X[.Y]` and resolve to real sections.
- [ ] Saved under the correct `docs/*` path.
- [ ] If numbering changed, update the traceability matrix.

**Traceability change DoD**
- [ ] Matrix updated (PRD, Arch, UI columns).
- [ ] `tools/validate_traceability_md.py` passes locally.
- [ ] CI workflow run is green (or issues explained and tracked).

## CI & Validator Usage (Quick Reference)
Local:
```bash
cd ~/Desktop/HRPro/architecture
python tools/validate_traceability_md.py   --prd=docs/PRD/PRD_v4.0_unified_numbered.md   --arch=docs/Architecture/Architecture_v4.1.md   --ui=docs/UI_Framework/UIFramework_v4.0_unified_numbered.md   --trace=docs/traceability/Traceability_v4.1_prefilled.xlsx   --out=docs/traceability/Traceability_link_check.csv
```

CI:
- Workflow: `.github/workflows/traceability-check.yml`
- Fails if any row is not `OK`
- Artifact: `Traceability_link_check.csv`

## Maintenance
- Store this ADR at `docs/adr/ADR-0004-collaboration-protocol.md`.
- Update when roles, prompts, or repo layout evolve.
- Reference this ADR in new chats to keep process consistent.

## Related ADRs
- ADR-0001: Advisor Export Trace
- ADR-0002: Unified Markdown Format
- ADR-0003: Traceability CI Enforcement
