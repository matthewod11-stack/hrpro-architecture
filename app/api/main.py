from fastapi import FastAPI

from app.api.routers import advisor, charts, export

app = FastAPI(title="HRPro API")
app.include_router(charts.router)
app.include_router(advisor.router)
app.include_router(export.router)
