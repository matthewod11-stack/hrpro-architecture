import streamlit as st
from app.ui.session_utils import set_trace_id, get_trace_id
from app.ui.components.retry_banner import retry_banner
from app.ui.components.toast import toast_success, toast_error
from app.ui.theme import get_palette
from app.ui.tokens import set_mode

try:
    from app.utils import telemetry
except ImportError:
    telemetry = None

st.title("PIP Builder")
palette = get_palette()
st.set_page_config(page_title="PIP Builder", layout="wide")
st.markdown(
    f"<div style='background:{palette['header']};color:{palette['text']};padding:8px;font-size:1.5em;'>PIP Builder</div>",
    unsafe_allow_html=True,
)
mode = st.sidebar.radio("Theme", ["light", "dark"], index=0)
set_mode(mode)

step_labels = ["Upload", "Draft", "Advisor Feedback", "Export"]
step = st.sidebar.radio("Step", step_labels, index=0)

if step == "Upload":
    st.file_uploader("Upload CSV or template", type=["csv"])
    st.warning("No file uploaded. Please upload to continue.")
elif step == "Draft":
    draft_text = st.text_area("Draft Text", "Enter PIP draft here...")
    st.info("AI Insights (coming soon)")
elif step == "Advisor Feedback":
    # Simulate Advisor response
    advisor_resp = {"trace_id": "sim-trace-123456"}
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
        "module": "pip",
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
