.PHONY: demo-theme
demo-theme:
	python ui/demo_theme.py
.PHONY: test-contracts
test-contracts:
	pytest -q -m contract
.PHONY: boot stop eval-offline
boot:
	bash scripts/dev_boot.sh
stop:
	bash scripts/dev_stop.sh
eval-offline:
	python -m eval.runner --mode offline --out eval/report.json && \
	python -m eval.report --in eval/report.json --out eval/report.md
.PHONY: trace-normalize
trace-normalize:
	@python tools/traceability_normalize_matrix.py || true
.PHONY: waive-legacy trace-ci
waive-legacy:
	@python tools/traceability_waive.py --list tools/legacy_waive_list.txt --trace docs/traceability/Traceability_v4.1_prefilled.xlsx --sheet Matrix && echo "Legacy rows waived."

trace-ci:
	@python tools/validate_traceability_ci.py
.PHONY: trace-force
trace-force:
	@python tools/traceability_force_patch.py --ambig tools/trace_legacy_autopatch.json --map tools/trace_force_map.json --out tools/trace_force_patch_report.json || true
	@echo "Force-patch report: tools/trace_force_patch_report.json"
.PHONY: trace-legacy-autopatch
trace-legacy-autopatch:
	@python tools/traceability_patch_legacy.py --todo tools/trace_legacy_todo.csv --force --out-report tools/trace_legacy_autopatch.json || true
	@echo "Auto-patch report: tools/trace_legacy_autopatch.json"
.PHONY: ui-canon
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
.PHONY: trace-legacy-report trace-legacy-fix
trace-legacy-report:
	@python tools/traceability_fix_legacy.py --out-report tools/trace_legacy_report.json --out-csv tools/trace_legacy_todo.csv || true
	@echo "Report: tools/trace_legacy_report.json"
	@echo "TODO (ambiguous): tools/trace_legacy_todo.csv"

trace-legacy-fix:
	@python tools/traceability_fix_legacy.py --apply-safe --out-report tools/trace_legacy_report.json --out-csv tools/trace_legacy_todo.csv
	@echo "Applied safe fixes. Remaining ambiguous refs listed in tools/trace_legacy_todo.csv"
.PHONY: trace-pr2-fail
trace-pr2-fail:
	@python tools/traceability_extract_pr2_failures.py
.PHONY: trace-fix
trace-fix:
	@python tools/traceability_fix_refs.py --apply && echo "Traceability refs: fix attempted. Re-run make trace-pr2"

.PHONY: trace-pr2
trace-pr2:
	@python tools/traceability_update_pr2.py --validate && echo "Traceability PR2 OK"
.PHONY: setup-dev format lint hooks

setup-dev:
	pip install -r requirements-dev.txt
	pre-commit install

format:
	black .

lint:
	ruff check --fix .

hooks:
	pre-commit run --all-files
.PHONY: demo
demo:
	@python tools/smoke_e2e.py
.PHONY: kb-sync kb-build kb-index kb-validate kb-reindex kb-demo

kb-sync:
	@bash tools/sync_repo_kb.sh

kb-reindex: kb-sync kb-build kb-index

kb-build:
	@python knowledge_base/build_corpus.py

kb-index:
	@python knowledge_base/index_corpus.py

kb-validate:
	@python tools/validate_traceability.py

kb-demo:
	@python tools/retrieval_demo.py --q "Summarize our traceability & validation gates."

.PHONY: ui
ui:
	streamlit run ui/pages/00_Landing.py
.PHONY: setup serve-ollama pull-model api ui demo launcher

setup:
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

api:
	@echo "Starting FastAPI backend (uvicorn)..."
	@export PYTHONPATH=. ; \
	(uvicorn app.main:app --reload --port 8000 || \
	 uvicorn api.main:app --reload --port 8000 || \
	 uvicorn src.app.main:app --reload --port 8000)

api-run:
	@echo "Starting FastAPI backend (uvicorn)..."
	@export PYTHONPATH=. ; \
	uvicorn app.api.main:app --reload --port 8000

ui:
	@echo "Starting Streamlit UI..."
	@(streamlit run Architecture/app/ui/app.py --server.port 8501 || \
	  streamlit run Architecture/app/ui/Home.py --server.port 8501 || \
	  streamlit run Architecture/streamlit_app.py --server.port 8501)

demo:
	@echo "Launching API and UI in new Terminal windows..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && make api"' &
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && make ui"' &
	@echo "Opening http://localhost:8501 in browser..."
	@open "http://localhost:8501"

.PHONY: kb-sync
kb-sync:
	@echo "Syncing knowledge base..."
	@python tools/sync_repo_kb.py
	    source .venv/bin/activate && pip install -r requirements.txt

kb-sync:
	@tools/sync_md.sh "$(HOME)/Desktop/knowledge_base" "knowledge_base/sources"

kb-clean:
	@rm -f knowledge_base/corpus.jsonl knowledge_base/build_report.md knowledge_base/anchors_index.csv
	@rm -rf versions/index/*
	@mkdir -p versions/index && touch versions/index/.keep

retrieve-smoke:
	@bash tools/retrieval_smoke.sh

launcher:
	@echo "Setting up Python environment..."
	@if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
	@. .venv/bin/activate && pip install --upgrade pip
	@if [ -f "requirements.txt" ]; then . .venv/bin/activate && pip install -r requirements.txt; fi
	@echo "Starting Ollama server..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && source .venv/bin/activate && ollama serve"' &
	@sleep 2
	@echo "Pulling llama3.1:8b model..."
	@ollama pull llama3.1:8b
	@echo "Launching FastAPI backend..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && source .venv/bin/activate && export PYTHONPATH=. && (uvicorn app.api.main:app --reload --port 8000 || uvicorn app.advisor.main:app --reload --port 8000)"' &
	@sleep 2
	@echo "Launching Streamlit UI..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && source .venv/bin/activate && (streamlit run app/ui/Home.py --server.port 8501 || streamlit run app/ui/pages/1_Dashboard.py --server.port 8501)"' &
	@sleep 2
	@echo "Opening http://localhost:8501 in browser..."
	@open "http://localhost:8501"