import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from app.api.main import app


@pytest.mark.asyncio
async def test_enps_chart_contract():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            resp = await ac.post("/v1/data/charts", json={"chart": "enps"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("title"), str)
        assert isinstance(data.get("series"), list)
        assert "counts" in data
        # Check series shape
        if data["series"]:
            s = data["series"][0]
            assert "label" in s
            assert isinstance(s["label"], str)
            assert "points" in s
            assert isinstance(s["points"], list)
            if s["points"]:
                pt = s["points"][0]
                assert "x" in pt and "y" in pt


@pytest.mark.asyncio
async def test_nine_box_chart_contract():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            resp = await ac.post("/v1/data/charts", json={"chart": "nine_box"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("title"), str)
        assert "grid" in data
        assert "cells" in data
        assert "legend" in data
        # Check cells shape
        if data["cells"]:
            c = data["cells"][0]
            assert "row" in c and "col" in c and "count" in c
            assert isinstance(c["row"], int)
            assert isinstance(c["col"], int)
            assert isinstance(c["count"], int)
