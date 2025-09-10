.PHONY: api ui dev

api:
	PYTHONPATH=. python -m uvicorn app.api.main:app --reload --port 8000

ui:
	PYTHONPATH=. streamlit run app/ui/main.py --server.port 8501

dev:
	@echo "Starting API and UI"; \
	( PYTHONPATH=. python -m uvicorn app.api.main:app --reload --port 8000 ) & \
	( PYTHONPATH=. streamlit run app/ui/main.py --server.port 8501 )
