import time

import pandas as pd
import requests
import streamlit as st

from app.ui.components.retry_banner import retry_banner
from app.ui.components.toast import toast_success
from app.ui.theme import get_palette
from app.ui.tokens import set_mode
from app.services import telemetry

API_URL = "http://127.0.0.1:8000/v1/data/charts"

st.title("Dashboard")
palette = get_palette()
st.set_page_config(page_title="Dashboard", layout="wide")
st.markdown(
    f"<div style='background:{palette['header']};color:{palette['text']};padding:8px;font-size:1.5em;'>Dashboard</div>",
    unsafe_allow_html=True,
)
mode = st.sidebar.radio("Theme", ["light", "dark"], index=0)
set_mode(mode)

start_time = time.time()


# Helper to fetch chart data
def fetch_chart(chart_name):
    try:
        resp = requests.post(API_URL, json={"chart": chart_name}, timeout=5)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)


# Fetch eNPS and 9-box
with st.spinner("Loading charts..."):
    enps_data, enps_err = fetch_chart("enps")
    nine_box_data, nine_box_err = fetch_chart("nine_box")

col1, col2 = st.columns(2)

# eNPS Chart
with col1:
    st.subheader("eNPS Line Chart")
    if enps_err:

        def retry_enps():
            toast_success("Retrying eNPS...")

        retry_banner(f"Could not load eNPS chart: {enps_err}", retry_enps)
    elif not enps_data or not enps_data.get("series", {}).get("points"):
        st.warning("Upload a CSV to see insights.")
    else:
        points = enps_data["series"]["points"]
        df = pd.DataFrame(points)
        st.line_chart(df)
        st.info("AI Insights (coming soon)")

# 9-box Table
with col2:
    st.subheader("9-Box Table")
    if nine_box_err:

        def retry_nine_box():
            toast_success("Retrying 9-box...")

        retry_banner(f"Could not load 9-box chart: {nine_box_err}", retry_nine_box)
    elif not nine_box_data or (
        not nine_box_data.get("cells")
        and not nine_box_data.get("series", {}).get("points")
    ):
        st.warning("Upload a CSV to see insights.")
    else:
        if nine_box_data.get("cells"):
            df = pd.DataFrame(nine_box_data["cells"])
        else:
            df = pd.DataFrame(nine_box_data["series"]["points"])
        st.dataframe(df)
        st.info("AI Insights (coming soon)")

render_time = int((time.time() - start_time) * 1000)
st.caption(f"Render time: {render_time} ms")

# Telemetry logging
try:
    # Try to get employee count from either chart
    employee_count = 0
    if enps_data and enps_data.get("series", {}).get("points"):
        employee_count = len(enps_data["series"]["points"])
    elif nine_box_data and nine_box_data.get("cells"):
        employee_count = len(nine_box_data["cells"])
    elif nine_box_data and nine_box_data.get("series", {}).get("points"):
        employee_count = len(nine_box_data["series"]["points"])
    telemetry.emit(
        "dashboard",
        {"ms": render_time, "employee_count": employee_count},
    )
except Exception as e:
    print(f"[telemetry] Logging failed: {e}")
