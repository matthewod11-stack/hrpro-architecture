from fastapi import FastAPI

from app.api.routers import (
    charts,
    export,
)  # add other routers (e.g., advisor) as they exist

app = FastAPI(title="HRPro API")

# mount routers
app.include_router(charts.router)
app.include_router(export.router)
