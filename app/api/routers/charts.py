# app/api/routers/charts.py
from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/data", tags=["charts"])


class ChartRequest(BaseModel):
    chart: Literal["enps", "nine_box"]
    params: dict = Field(default_factory=dict)


class SeriesPoint(BaseModel):
    x: float | int | str
    y: float | int
    meta: dict | None = None


class ChartSeries(BaseModel):
    name: str
    points: List[SeriesPoint]


class ChartResponse(BaseModel):
    chart: str
    title: str
    series: List[ChartSeries]
    legend: List[str]
    bins: dict | None = None
    insights_placeholder: bool = True


@router.post("/charts", response_model=ChartResponse)
def charts(req: ChartRequest):
    if req.chart == "enps":
        return {
            "chart": "enps",
            "title": "eNPS (last 6 mo)",
            "series": [
                {
                    "name": "eNPS",
                    "points": [
                        {"x": "2025-04", "y": 18},
                        {"x": "2025-05", "y": 22},
                        {"x": "2025-06", "y": 15},
                        {"x": "2025-07", "y": 28},
                        {"x": "2025-08", "y": 31},
                        {"x": "2025-09", "y": 27},
                    ],
                }
            ],
            "legend": ["eNPS"],
            "bins": None,
            "insights_placeholder": True,
        }
    # nine_box stub
    return {
        "chart": "nine_box",
        "title": "9-Box Distribution",
        "series": [
            {
                "name": "count",
                "points": [
                    {"x": "L-P", "y": 6},
                    {"x": "L-M", "y": 10},
                    {"x": "L-H", "y": 4},
                    {"x": "M-P", "y": 12},
                    {"x": "M-M", "y": 18},
                    {"x": "M-H", "y": 8},
                    {"x": "H-P", "y": 5},
                    {"x": "H-M", "y": 9},
                    {"x": "H-H", "y": 3},
                ],
            }
        ],
        "legend": ["Employees"],
        "bins": {"total": 75},
        "insights_placeholder": True,
    }
