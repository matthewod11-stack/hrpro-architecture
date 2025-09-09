# ADR-0003: Enforce Traceability via Continuous Integration

## Status
Accepted (2025-09-09)

## Context
We established in ADR-0002 that unified Markdown documents (PRD, Architecture, UI Framework) are the canonical sources of truth. To maintain alignment, every requirement and flow must be traceable across these documents.

Historically, traceability matrices were maintained manually in Excel. This led to frequent drift:
- PRD requirements referenced in the matrix but missing in Architecture.
- Architecture sections referenced but missing in PRD.
- UI Framework mappings incomplete or outdated.

Without automation, drift wasn’t detected until late in development or review.

## Decision
- **Traceability validation is now enforced in CI.**
- The validator script (tools/validate_traceability_md.py) checks that:
  - Every reference in the traceability matrix points to a numbered section in PRD, Architecture, or UI Framework.
  - Status is marked OK when all mappings are valid; otherwise flagged.
- GitHub Action (.github/workflows/traceability-check.yml) runs the validator on every pull request and push to main.
- The workflow fails if any row in the matrix is not OK.
- A validation report (Traceability_link_check.csv) is uploaded as an artifact for review.

## Consequences
- ✅ Prevents drift between PRD, Architecture, UI Framework, and the traceability matrix.
- ✅ Contributors see immediate feedback in their PRs if they break traceability.
- ✅ Stakeholders can download the CSV report for a quick overview.
- ⚠️ Requires contributors to update the matrix whenever they add, change, or remove sections in PRD, Architecture, or UI Framework.

## Related ADRs
- ADR-0001: Advisor Export Trace
- ADR-0002: Unified Markdown Format
