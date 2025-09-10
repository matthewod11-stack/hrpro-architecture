import streamlit as st
import pandas as pd
import requests
import time
from app.utils import telemetry

API_URL = "http://127.0.0.1:8000/v1/data/charts"

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard")

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
        st.error(f"Could not load eNPS chart: {enps_err}")
        if enps_err:
            if st.button("Retry eNPS"):
                st.rerun()
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
        st.error(f"Could not load 9-box chart: {nine_box_err}")
        if nine_box_err:
            if st.button("Retry 9-box"):
                st.rerun()
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
    telemetry.log(
        {
            "event": "dashboard_render",
            "ms": render_time,
            "employee_count": employee_count,
        }
    )
except Exception as e:
    print(f"[telemetry] Logging failed: {e}")
