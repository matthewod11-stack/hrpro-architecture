# ADR-0002: Adopt Unified Markdown Format as Canonical Documentation

## Status
Accepted (2025-09-09)

## Context
Prior versions of the Product Requirements Document (PRD), Architecture Specification, and UI Framework were stored as PDFs or Word docs. This created several issues:

- Headings were inconsistent or lost numbering during format conversion.
- Traceability validator scripts could not reliably parse references (§X.Y).
- Mismatches between PRD, Architecture, and UI Framework created confusion.
- CI/CD automation could not enforce document compliance.

The Architecture document was already in Markdown and cleanly structured with numbered headings. To align, we converted PRD and UI Framework from Word → Markdown, applied canonical numbering, and synced all three to a common outline.

## Decision
- Markdown (.md) is now the **canonical source of truth** for PRD, Architecture, and UI Framework documents.
- All top-level headings use numeric prefixes:
  - # 1 …
  - ## 1.1 …
  - ### 1.1.1 …
- Inline references must use §X[.Y] format.
- A validator script (tools/validate_traceability_md.py) enforces consistency between the documents and the traceability matrix.
- GitHub Action (.github/workflows/traceability-check.yml) runs the validator on every PR. Any mismatches fail the build.
- PDFs and Word versions may be exported for distribution, but **Markdown is canonical**.

## Consequences
- ✅ Traceability matrix can now map UI flows → PRD requirements → Architecture → UI Framework with reliable anchors.
- ✅ CI/CD automation ensures drift is caught immediately.
- ✅ Contributors can open and edit docs with any text editor.
- ⚠️ Requires discipline: all edits must preserve numbering format and §X.Y references.

## Related ADRs
- ADR-0001: Advisor Export Trace
- ADR-0003: Traceability CI Enforcement
