# ADR-0001: Link Advisor Trace to Export & Enforce Branding Compliance
Date: 2025-09-09
Status: Accepted
Context
- PRD requires transparent Advisor outputs with sources and explainability tags, plus branded exports.
- Architecture defines Advisor response contract with `citations[]`, `explainability_tag`, and `trace_id`, and an Export Engine with branding rules and offline font embedding.
Decision
- UI/BE MUST pass `trace_id` from Advisor responses through Builder flows to Export Engine.
- Export Engine MUST emit `export_branding_compliance` (boolean) and `export_manifest_hash`, logged with `trace_id`.
- CI MUST block release if branding compliance is false for any golden export snapshots.
Consequences
- Enables end-to-end auditability from prompt → answer → exported document.
- Provides measurable gating for branding and reduces regressions.
Implementation Notes
- UI: Store `trace_id` in builder state; include in `/v1/export/{pdf|xlsx|csv}` payloads.
- BE: Add manifest hashing; assert header/logo/footer/watermark presence; embed Inter + Source Serif subsets.
- QA: Golden snapshot exports; schema check for `citations[]` non-empty when Success Metrics require it.
