import json
import time

import streamlit as st

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
