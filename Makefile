.PHONY: validate-traceability autopatch-traceability

# Run traceability validator with autodiscovered spec paths
validate-traceability:
	python tools/validate_traceability_md.py

# Auto patch legacy rows in the traceability matrix
autopatch-traceability:
	python tools/traceability_autopatch.py
