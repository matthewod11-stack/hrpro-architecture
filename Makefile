 .PHONY: help demo-theme test-contracts boot stop eval-offline \
         trace-normalize waive-legacy trace-ci trace-force trace-legacy-autopatch \
         ui-canon trace-legacy-report trace-legacy-fix trace-pr2-fail trace-fix trace-pr2 \
         setup-dev format lint hooks demo kb-sync kb-build kb-index kb-validate kb-reindex kb-demo \
         setup serve-ollama pull-model api api-run ui demo-smoke kb-clean retrieve-smoke \
         launcher validate-traceability autopatch-traceability

# Help
help: ## Show available make targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?##"} {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}' | sort

# Demo and testing utilities
demo-theme:
	python ui/demo_theme.py

test-contracts:
	pytest -q -m contract

boot:
	bash scripts/dev_boot.sh

stop:
	bash scripts/dev_stop.sh

eval-offline:
	python -m eval.runner --mode offline --out eval/report.json && \
	python -m eval.report --in eval/report.json --out eval/report.md

# Traceability utilities
trace-normalize:
	@python tools/traceability_normalize_matrix.py || true

waive-legacy:
	@python tools/traceability_waive.py --list tools/legacy_waive_list.txt --trace docs/traceability/Traceability_v4.1_prefilled.xlsx --sheet Matrix && echo "Legacy rows waived."

trace-ci:
	@python tools/validate_traceability_ci.py

trace-force:
	@python tools/traceability_force_patch.py --ambig tools/trace_legacy_autopatch.json --map tools/trace_force_map.json --out tools/trace_force_patch_report.json || true
	@echo "Force-patch report: tools/trace_force_patch_report.json"

trace-legacy-autopatch:
	@python tools/traceability_patch_legacy.py --todo tools/trace_legacy_todo.csv --force --out-report tools/trace_legacy_autopatch.json || true
	@echo "Auto-patch report: tools/trace_legacy_autopatch.json"

ui-canon:
	@mkdir -p docs/UIFramework
	@if [ -f docs/UIFramework/UIFramework_v4.0_unified_numbered.md ]; then \
		echo "UIFramework spec already canonicalized."; \
	else \
		FOUND=$$(find . -type f -name "UIFramework_v4.0_unified_numbered.md" | head -n 1); \
		if [ -n "$$FOUND" ]; then \
			cp "$$FOUND" docs/UIFramework/UIFramework_v4.0_unified_numbered.md && echo "Copied UI spec to canonical path."; \
		else \
			echo "WARNING: Could not find UIFramework_v4.0_unified_numbered.md anywhere in repo."; \
		fi; \
	fi

trace-legacy-report:
	@python tools/traceability_fix_legacy.py --out-report tools/trace_legacy_report.json --out-csv tools/trace_legacy_todo.csv || true
	@echo "Report: tools/trace_legacy_report.json"
	@echo "TODO (ambiguous): tools/trace_legacy_todo.csv"

trace-legacy-fix:
	@python tools/traceability_fix_legacy.py --apply-safe --out-report tools/trace_legacy_report.json --out-csv tools/trace_legacy_todo.csv
	@echo "Applied safe fixes. Remaining ambiguous refs listed in tools/trace_legacy_todo.csv"

trace-pr2-fail:
	@python tools/traceability_extract_pr2_failures.py

trace-fix:
	@python tools/traceability_fix_refs.py --apply && echo "Traceability refs: fix attempted. Re-run make trace-pr2"

trace-pr2:
	@python tools/traceability_update_pr2.py --validate && echo "Traceability PR2 OK"

# Dev setup and linting
setup-dev: ## Install dev tools and pre-commit hooks
	pip install -r requirements-dev.txt
	pre-commit install

format: ## Format code with Black
	black .

lint: ## Lint and fix with Ruff
	ruff check --fix .

hooks: ## Run all pre-commit hooks
	pre-commit run --all-files

# Smoke demo
demo-smoke:
	@python tools/smoke_e2e.py

# Knowledge base workflow
kb-sync: ## Sync knowledge base from external sources
	@echo "Syncing knowledge base..."
	@python tools/sync_repo_kb.py

kb-reindex: kb-sync kb-build kb-index

kb-build: ## Build KB corpus
	@python knowledge_base/build_corpus.py

kb-index: ## Build KB index
	@python knowledge_base/index_corpus.py

kb-validate: ## Validate traceability links
	@python tools/validate_traceability.py

kb-demo: ## Run retrieval demo
	@python tools/retrieve_demo.py --q "Summarize our traceability & validation gates."

kb-clean:
	@rm -f knowledge_base/corpus.jsonl knowledge_base/build_report.md knowledge_base/anchors_index.csv
	@rm -rf versions/index/*
	@mkdir -p versions/index && touch versions/index/.keep

retrieve-smoke:
	@bash tools/retrieval_smoke.sh

# Local run targets
setup: ## Create venv and install requirements
	@echo "Creating .venv and installing requirements..."
	@if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
	@. .venv/bin/activate && pip install --upgrade pip
	@if [ -f "requirements.txt" ]; then . .venv/bin/activate && pip install -r requirements.txt; fi
	@echo "Setup complete."

serve-ollama:
	@echo "Starting Ollama server..."
	@ollama serve

pull-model:
	@echo "Pulling llama3.1:8b model..."
	@ollama pull llama3.1:8b

api: ## Run FastAPI backend (dev)
	@echo "Starting FastAPI backend (uvicorn)..."
	@export PYTHONPATH=. ; \
	uvicorn app.api.main:app --reload --port 8000

api-run:
	@echo "Starting FastAPI backend (uvicorn)..."
	@export PYTHONPATH=. ; \
	uvicorn app.api.main:app --reload --port 8000

ui: ## Run Streamlit UI (dev)
	@echo "Starting Streamlit UI..."
	@(streamlit run app/ui/Home.py --server.port 8501 || \
	  streamlit run app/ui/pages/00_Landing.py --server.port 8501)

# Mac launcher to open separate terminals and browser
launcher: ## Mac: open API & UI in Terminal windows
	@echo "Setting up Python environment..."
	@if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
	@. .venv/bin/activate && pip install --upgrade pip
	@if [ -f "requirements.txt" ]; then . .venv/bin/activate && pip install -r requirements.txt; fi
	@echo "Launching FastAPI backend..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && source .venv/bin/activate && export PYTHONPATH=. && uvicorn app.api.main:app --reload --port 8000"' &
	@sleep 2
	@echo "Launching Streamlit UI..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && source .venv/bin/activate && streamlit run app/ui/Home.py --server.port 8501"' &
	@sleep 2
	@echo "Opening http://localhost:8501 in browser..."
	@open "http://localhost:8501"

# Traceability checks
validate-traceability: ## Validate traceability matrix references
	python tools/validate_traceability_md.py \
		--prd=docs/PRD/PRD_v4.0_unified_numbered.md \
		--arch=docs/Architecture/Architecture_v4.1_unified.md \
		--ui=docs/UI_Framework/UIFramework_v4.0_unified_numbered.md \
		--trace=docs/traceability/Traceability_v4.1_prefilled.xlsx \
		--out=docs/traceability/Traceability_link_check.csv

autopatch-traceability:
	python tools/traceability_add.py --req "$(REQ)" --arch "$(ARCH)" --ui "$(UI)"

 
