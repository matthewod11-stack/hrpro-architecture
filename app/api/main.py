from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.routers import advisor, charts, export

app = FastAPI(title="HRPro API")
app.include_router(charts.router)
app.include_router(advisor.router)
app.include_router(export.router)


@app.get("/healthz", response_class=PlainTextResponse, tags=["ops"])  # liveness
def healthz() -> str:
    return "ok"


@app.get("/readyz", response_class=JSONResponse, tags=["ops"])  # readiness
def readyz() -> dict:
    # Lightweight readiness; can be extended to check external deps
    return {"status": "ready"}
