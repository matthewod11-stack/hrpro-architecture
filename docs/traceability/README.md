# Traceability Matrix & Runtime Probe

## Trace Probe

To verify runtime contract compliance (ADR-0001, §12), run:

    make trace-probe

This command runs a synthetic export request with a generated trace_id and checks that the API response echoes the trace_id, returns a valid 64-character manifest hash, and passes branding compliance.

**Expected output:**

    {'trace_id': 'probe-...', 'export_branding_compliance': True, 'export_manifest_hash': '...'}

Exit code 0 means pass; nonzero means contract violation.

See also: `tools/probe_trace_flow.py`, `tests/test_trace_flow.py` for integration tests.
