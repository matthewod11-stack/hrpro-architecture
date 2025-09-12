anchors-normalize:
	python tools/normalize_anchors.py
# Ollama endpoint/model check
ollama-check:
	python tools/ollama_check.py
eval-retrieval:
	python tools/eval_retrieval.py
advisor-demo:
	curl -X POST http://localhost:8000/v1/advisor/answer \
	  -H "Content-Type: application/json" \
	  -d '{"prompt":"acceptance criteria","module":"dashboard"}' | jq
.PHONY: kb-build kb-index kb-retrieve
kb-build:
	python tools/build_corpus.py

kb-index:
	python tools/index_corpus.py

kb-retrieve:
	python tools/retrieve_demo.py --topic "tokens focus ring" --top_k 5
.PHONY: api ui dev test deps trace-probe
trace-probe:
	python tools/probe_trace_flow.py --module pip --client DemoCo --export pdf

api:
	PYTHONPATH=. python -m uvicorn app.api.main:app --reload --port 8000

ui:
	PYTHONPATH=. streamlit run app/ui/pages/3_306090_Builder.py --server.port 8501

dev:
    @echo "Starting API and UI"; \
		( PYTHONPATH=. python -m uvicorn app.api.main:app --reload --port 8000 ) & \
		( PYTHONPATH=. streamlit run app/ui/pages/3_306090_Builder.py --server.port 8501 )

test:
		PYTHONPATH=. pytest -q

deps:
		python -m venv .venv || true
	    source .venv/bin/activate && pip install -r requirements.txt

kb-sync:
	@tools/sync_md.sh "$(HOME)/Desktop/knowledge_base" "knowledge_base/sources"

kb-clean:
	@rm -f knowledge_base/corpus.jsonl knowledge_base/build_report.md knowledge_base/anchors_index.csv
	@rm -rf versions/index/*
	@mkdir -p versions/index && touch versions/index/.keep

retrieve-smoke:
	@bash tools/retrieval_smoke.sh