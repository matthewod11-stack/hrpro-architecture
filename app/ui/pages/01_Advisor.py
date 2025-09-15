import json
import os
import time

import streamlit as st

from app.ui.components.citations import render_citations
from app.ui.components.sse import stream_sse
from app.ui.state import clear_advisor_state, get_state, set_state

st.set_page_config(page_title="Ask your CPO", page_icon="🤖")
st.title("Ask your CPO")

seed_query = st.session_state.get("seed_query", "")
workspace = st.session_state.get("workspace", None)
query_param = st.query_params.get("q") if hasattr(st, "query_params") else None

if query_param and not seed_query:
    seed_query = query_param
    st.session_state["seed_query"] = seed_query

question = st.text_area(
    "Question",
    value=seed_query,
    key="advisor_question",
    help="Type your question for the CPO advisor.",
)
submit = st.button("Ask", key="advisor_submit")

if submit or (query_param and not get_state("advisor_final")):
    clear_advisor_state()
    st.session_state["advisor_buffer"] = ""
    st.session_state["advisor_trace_id"] = None
    st.session_state["advisor_error"] = None
    st.session_state["advisor_citations"] = []
    st.session_state["advisor_final"] = None
    placeholder = st.empty()
    status = st.empty()
    url = os.environ.get("ADVISOR_URL", "http://localhost:8000/v1/advisor/answer")
    body = {"query": question, "persona": "cpo", "top_k": 6, "workspace": workspace}
    start = time.time()
    ttfa_ms = None
    buffer = ""
    trace_id = None
    status.info("Thinking...", icon="⏳")
    for evt in stream_sse(url, body):
        event = evt.get("event")
        data = evt.get("data", {})
        if event == "delta":
            if ttfa_ms is None:
                ttfa_ms = int((time.time() - start) * 1000)
            buffer += data.get("text", "")
            trace_id = data.get("trace_id", trace_id)
            set_state("advisor_buffer", buffer)
            set_state("advisor_trace_id", trace_id)
            placeholder.markdown(buffer)
        elif event == "error":
            status.error(
                f"Error: {data.get('message')} (trace_id: {data.get('trace_id')})"
            )
            set_state("advisor_error", data.get("message"))
            set_state("advisor_trace_id", data.get("trace_id"))
            st.button("Retry", key="advisor_retry")
            break
        elif event == "final":
            status.empty()
            answer = data.get("answer", {})
            set_state("advisor_final", answer)
            set_state("advisor_citations", answer.get("citations", []))
            set_state("advisor_trace_id", data.get("trace_id"))
            placeholder.empty()
            st.markdown(f"### Summary\n{answer.get('summary','')}")
            if answer.get("findings"):
                st.markdown("**Findings:**")
                st.write(answer["findings"])
            if answer.get("actions"):
                st.markdown("**Actions:**")
                st.write(answer["actions"])
            if answer.get("insights"):
                st.markdown("**Insights:**")
                st.write(answer["insights"])
            render_citations(answer.get("citations", []))
            trace_id = data.get("trace_id")
            st.markdown(f"---\nTrace ID: `{trace_id}`")
            st.button(
                "Copy trace ID",
                key="copy_trace_id",
                on_click=lambda t=trace_id: st.session_state.update(
                    {"copied_trace_id": t}
                ),
            )
            total_ms = int((time.time() - start) * 1000)
            telemetry = {
                "ts": int(time.time()),
                "page": "advisor",
                "trace_id": trace_id,
                "ttfa_ms": ttfa_ms,
                "total_ms": total_ms,
                "query_len": len(question),
            }
            try:
                with open("logs/ui.jsonl", "a") as f:
                    f.write(json.dumps(telemetry) + "\n")
            except Exception:
                pass
            break
