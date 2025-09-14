"""Home page for the HRPro UI."""

import json
import time

import requests
import streamlit as st

from app.config import API_BASE_URL
from app.ui.state import emit_telemetry

# ----- Page setup -----
st.set_page_config(page_title="HRPro", layout="wide")

# ----- Design tokens (module colors) -----
MODULES = [
    ("Dashboard", "pages/1_Dashboard.py", "#FF4D4F"),
    ("Engagement", "pages/2_Engagement.py", "#FA8C16"),
    ("Performance", "pages/3_Performance.py", "#52C41A"),
    ("PIP Builder", "pages/4_PIP_Builder.py", "#1890FF"),
    ("JD Builder", "pages/5_JD_Builder.py", "#722ED1"),
]
ADVISOR_URL = f"{API_BASE_URL}/v1/advisor/answer"


# ----- SSE client (no external deps) -----
def call_advisor_sse(prompt: str):
    """
    Yields ({'delta': '...'}, None) for tokens and (None, final_json) once finished.
    Expects server to send 'data: {...}\\n\\n' lines and a terminal 'data: [DONE]'.
    """
    with requests.post(
        ADVISOR_URL, json={"prompt": prompt, "stream": True}, stream=True, timeout=60
    ) as resp:
        resp.raise_for_status()
        final = None
        for raw in resp.iter_lines(decode_unicode=True):
            if not raw:
                continue
            if raw == "data: [DONE]":
                break
            if raw.startswith("data: "):
                payload = json.loads(raw[6:])
                if "delta" in payload:
                    yield payload, None
                if "final" in payload:
                    final = payload["final"]
        yield None, final


# ----- UI: Title -----
st.markdown("<h1 style='text-align:center;'>HR PRO</h1>", unsafe_allow_html=True)

# ----- Ask box (Enter-to-submit via form) -----
with st.form(key="advisor_form", clear_on_submit=False):
    q = st.text_input(
        "Ask your CPO",
        placeholder="e.g., What are our top performance risks this cycle?",
    )
    go = st.form_submit_button("Ask")

# ----- Tiles row (with navigation via st.switch_page) -----
cols = st.columns(len(MODULES))
for i, (name, page, color) in enumerate(MODULES):
    with cols[i]:
        # nice-looking colored tile as a button
        if st.button(
            name, key=f"tile_{i}", help=f"Open {name}", use_container_width=True
        ):
            st.session_state["_jump_to_page"] = page
        # style it to look like our tile
        st.markdown(
            f"""
            <style>
            div.stButton > button[kind="secondary"] {{
                background:{color} !important;
                color:white !important;
                border-radius:16px !important;
                padding:16px 0 !important;
                border:0 !important;
                font-weight:700 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

# perform the navigation after buttons render
if st.session_state.get("_jump_to_page"):
    target = st.session_state.pop("_jump_to_page")
    try:
        st.switch_page(target)  # e.g., "pages/1_Dashboard.py"
    except Exception:
        # Fallback: show a hint if switch_page isn't available
        st.warning(
            f"Could not navigate automatically. Use the sidebar to open: {target}"
        )


# ----- Advisor streaming block -----
def advisor_block(prompt: str):
    banner = st.empty()
    stream_box = st.empty()
    summary = st.empty()
    meta = st.empty()

    try:
        stream_box.write("…streaming…")
        start = time.perf_counter()
        first_token_emitted = False
        final = None
        pending_trace = "pending"

        for payload, final_so_far in call_advisor_sse(prompt):
            if payload and "delta" in payload:
                # First token → log TTFA with pending trace id
                if not first_token_emitted:
                    ttfa_ms = int((time.perf_counter() - start) * 1000)
                    first_token_emitted = True
                    emit_telemetry(
                        "time_to_first_answer_ms",
                        {"trace_id": pending_trace, "ms": ttfa_ms},
                    )
                # Append streamed text
                stream_box.markdown(payload["delta"])

            if final_so_far is not None:
                final = final_so_far

        stream_box.empty()

        if final:
            # Patch telemetry with real trace_id (log again w/ final id for simplicity)
            trace_id = final.get("trace_id", "n/a")
            if first_token_emitted:
                ttfa_ms2 = int((time.perf_counter() - start) * 1000)
                emit_telemetry(
                    "time_to_first_answer_ms", {"trace_id": trace_id, "ms": ttfa_ms2}
                )

            has_cite = bool(final.get("citations"))
            emit_telemetry(
                "advisor_response_has_citation",
                {"trace_id": trace_id, "has_citation": has_cite},
            )

            summary.write(f"**Summary:** {final.get('summary','')}")
            meta.caption(
                "Citations: "
                + ", ".join(final.get("citations", []))
                + f" • trace_id: {trace_id}"
            )
        else:
            banner.error("Advisor stream ended unexpectedly. Click retry to try again.")
            if st.button("Retry"):
                advisor_block(prompt)
    except Exception as e:
        banner.error(f"Network hiccup: {e}")
        if st.button("Retry"):
            advisor_block(prompt)


# ----- Submit handler -----
if go and q:
    advisor_block(q)
