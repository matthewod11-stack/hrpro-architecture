.PHONY: launcher validate-traceability autopatch-traceability

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

validate-traceability:
	python tools/validate_traceability_md.py \
		--prd=docs/PRD/PRD_v4.0_unified_numbered.md \
		--arch=docs/Architecture/Architecture_v4.1_unified.md \
		--ui=docs/UI_Framework/UIFramework_v4.0_unified_numbered.md \
		--trace=docs/traceability/Traceability_v4.1_prefilled.xlsx \
		--out=docs/traceability/Traceability_link_check.csv

autopatch-traceability:
	python tools/traceability_add.py --req "$(REQ)" --arch "$(ARCH)" --ui "$(UI)"
