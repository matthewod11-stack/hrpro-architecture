from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.routers import advisor, charts
from app.retrieval import adapter, ollama_client

app = FastAPI(title="HRPro API")
app.include_router(charts.router)
app.include_router(advisor.router)


@app.get("/healthz", response_class=PlainTextResponse, tags=["ops"])  # liveness
def healthz() -> str:
    return "ok"


@app.get("/readyz", response_class=JSONResponse, tags=["ops"])  # readiness
def readyz() -> JSONResponse:
    """Check external dependencies for readiness."""
    errors: list[str] = []

    if not ollama_client.health_ok():
        errors.append("ollama_client not healthy")

    required = [
        adapter.META_PATH,
        adapter.MATRIX_PATH,
        adapter.VEC_PATH,
        adapter.NN_PATH,
    ]
    missing = [p.name for p in required if not p.exists()]
    if missing:
        errors.append(f"missing index files: {', '.join(sorted(missing))}")

    if errors:
        return JSONResponse(
            status_code=503, content={"status": "not ready", "errors": errors}
        )

    return JSONResponse(content={"status": "ready"})
