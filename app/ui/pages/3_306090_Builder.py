import time

import streamlit as st

from app.ui.components.retry_banner import retry_banner
from app.ui.components.toast import toast_error, toast_success
from app.ui.session_utils import get_trace_id, set_trace_id
from app.ui.theme import get_palette
from app.ui.tokens import set_mode
from app.services import telemetry

st.title("30/60/90 Builder")
palette = get_palette()
st.set_page_config(page_title="30/60/90 Builder", layout="wide")
st.markdown(
    f"<div style='background:{palette['header']};color:{palette['text']};padding:8px;font-size:1.5em;'>30/60/90 Builder</div>",
    unsafe_allow_html=True,
)
mode = st.sidebar.radio("Theme", ["light", "dark"], index=0)
set_mode(mode)

start_time = time.time()

step_labels = ["Upload", "Draft", "Advisor Feedback", "Export"]
step = st.sidebar.radio("Step", step_labels, index=0)

st.markdown("#### Stepper: 30/60/90 Plan")
st.info("Purple (#722ED1)")

if step == "Upload":
    st.file_uploader("Upload CSV or template", type=["csv"])
    st.warning("No file uploaded. Please upload to continue.")
elif step == "Draft":
    draft_text = st.text_area("Draft Text", "Enter onboarding plan draft here...")
    st.info("AI Insights (coming soon)")
elif step == "Advisor Feedback":
    advisor_resp = {"trace_id": "sim-trace-654321"}
    try:
        set_trace_id(advisor_resp["trace_id"])
        st.text_area(
            "Advisor Suggestions", "Advisor feedback will appear here...", disabled=True
        )
        st.info(f"Trace ID set: {get_trace_id()}")
        toast_success("Advisor succeeded!")
    except Exception as e:
        retry_banner(f"Advisor failed: {e}", lambda: toast_error("Retrying Advisor..."))
elif step == "Export":
    export_kind = st.selectbox("Export Kind", ["pdf", "xlsx", "csv"])
    payload = {
        "content": {"dummy": True},
        "module": "306090",
        "client": "DemoCo",
        "trace_id": get_trace_id(),
    }
    try:
        st.write(f"Payload for export: {payload}")
        st.button("Export Plan")
        st.success("Export available (stub)")
        toast_success("Export succeeded!")
    except Exception as e:
        retry_banner(f"Export failed: {e}", lambda: toast_error("Retrying Export..."))

st.markdown("#### Quick Actions")
actions = [
    "TIGHTEN",
    "MEASURE",
    "REFINE",
    "BALANCE",
    "CLARIFY",
    "PRIORITIZE",
    "STRETCH",
]
cols = st.columns(len(actions))
for i, action in enumerate(actions):
    if cols[i].button(action):
        st.info(f"{action} action triggered (stub)")

render_ms = int((time.time() - start_time) * 1000)
st.caption(f"Render time: {render_ms} ms")

try:
    telemetry.emit(
        "builder",
        {"builder_type": "306090", "ms": render_ms},
    )
except Exception as e:
    print(f"[telemetry] Logging failed: {e}")
