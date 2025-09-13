import streamlit as st

from ui.components.tiles import render_tiles
from ui.state import route_to_advisor, set_seed_query
from ui.tokens import SPACE_MD

st.title("HRPro")
st.caption("Ask your CPO. Local-first, traceable answers.")


# Debounce logic
if "_last_ask_time" not in st.session_state:
    st.session_state["_last_ask_time"] = 0.0
import time


def can_submit():
    now = time.time()
    if now - st.session_state["_last_ask_time"] < 0.5:
        return False
    st.session_state["_last_ask_time"] = now
    return True


q = st.text_input(
    "Ask your CPO",
    value=st.session_state.get("seed_query", ""),
    placeholder="e.g., How do we enforce citations in advisor answers?",
    on_change=lambda: None,
)


def submit_query():
    if can_submit():
        route_to_advisor(q)


if st.button("Ask"):
    submit_query()

# Enter-to-submit
import streamlit.components.v1 as components

components.html(
    """
<script>
document.querySelector('input[type="text"]')?.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') {
    window.parent.postMessage({streamlitSubmit:true}, '*');
  }
});
</script>
""",
    height=0,
)

import streamlit as st


def handle_streamlit_submit():
    submit_query()


st.experimental_get_query_params()

if st.session_state.get("streamlitSubmit"):
    handle_streamlit_submit()
    st.session_state["streamlitSubmit"] = False

SUGGESTED = [
    "How do we enforce citations in advisor answers?",
    "Draft a 30/60/90 onboarding plan for a new PM.",
    "What dashboards should we show for eNPS and attrition?",
    "Summarize our traceability & validation gates.",
    "Outline the export pipeline with branding compliance.",
    "How do we raise retrieval coverage above 60%?",
]
st.write("")
st.write("**Try a suggested prompt**")
cols = st.columns(3)
for i, s in enumerate(SUGGESTED):
    with cols[i % 3]:
        if st.button(s, key=f"sugg_{i}"):
            if can_submit():
                route_to_advisor(s)

st.divider()
render_tiles()
from app.ui.components.tiles import render_tiles
from app.ui.state import route_to_advisor, set_seed_query
from app.ui.tokens import BG_SURFACE, FG_MUTED, RADIUS_MD, SPACE_MD

SUGGESTED = [
    "How do we enforce citations in advisor answers?",
    "Draft a 30/60/90 onboarding plan for a new PM.",
    "What dashboards should we show for eNPS and attrition?",
    "Summarize our traceability & validation gates.",
    "Outline the export pipeline with branding compliance.",
    "How do we raise retrieval coverage above 60%?",
]

st.set_page_config(page_title="HRPro Landing", page_icon="🏢")

st.markdown(
    f"<div style='background:{BG_SURFACE};padding:{SPACE_MD}px;border-radius:{RADIUS_MD}px;'>"
    "<h1>HRPro</h1>"
    "<span style='color:{};font-size:1.1em'>Unified HR architecture. Ask your CPO, explore dashboards, and more.</span>"
    "</div>".format(FG_MUTED),
    unsafe_allow_html=True,
)

q = st.text_input(
    "Ask your CPO",
    value=st.session_state.get("seed_query", ""),
    placeholder="e.g., How do we enforce citations in advisor answers?",
    key="landing_input",
)

ask_clicked = st.button("Ask", key="landing_ask")

if ask_clicked and q:
    set_seed_query(q)
    route_to_advisor(q)
    # Telemetry
    import json

    telemetry = {
        "ts": int(time.time()),
        "page": "landing",
        "action": "route_to_advisor",
        "query_len": len(q),
    }
    try:
        with open("logs/ui.jsonl", "a") as f:
            f.write(json.dumps(telemetry) + "\n")
    except Exception:
        pass

st.markdown("#### Suggested prompts")
chip_cols = st.columns(len(SUGGESTED))
for i, prompt in enumerate(SUGGESTED):
    with chip_cols[i]:
        if st.button(prompt, key=f"suggested_{i}"):
            set_seed_query(prompt)
            route_to_advisor(prompt)
            # Telemetry
            import json

            telemetry = {
                "ts": int(time.time()),
                "page": "landing",
                "action": "route_to_advisor",
                "query_len": len(prompt),
            }
            try:
                with open("logs/ui.jsonl", "a") as f:
                    f.write(json.dumps(telemetry) + "\n")
            except Exception:
                pass

st.divider()
render_tiles()

st.markdown(
    f"<div style='margin-top:{SPACE_MD}px;color:{FG_MUTED};font-size:0.9em'>"
    "Version: 4.1 | Workspace: "
    + str(st.session_state.get("workspace", "default"))
    + "</div>",
    unsafe_allow_html=True,
)
