import json
import time

import requests
import streamlit as st

from ui.components.citations import render_citations
from ui.components.sse import stream_sse
from ui.state import get_trace_id, set_last_answer, set_trace_id

API = "http://localhost:8000"

st.title("Ask your CPO")
seed = st.session_state.get("seed_query") or st.query_params.get("q", "")
question = st.text_area("Question", value=seed, height=120)
submit = st.button("Ask") or (seed and "auto_ran" not in st.session_state)

# Empty-question guard
if submit and not question.strip():
    st.warning("Please enter a question to ask your CPO.")
elif submit:
    st.session_state["auto_ran"] = True
    out = st.empty()
    typing = st.status("Thinking...", expanded=False)
    buf = []
    final = None
    error_msg = None
    try:
        for evt in stream_sse(
            f"{API}/v1/advisor/answer",
            {"query": question, "persona": "cpo", "top_k": 6},
        ):
            ev = evt.get("event")
            data = evt.get("data", {})
            if ev == "start":
                set_trace_id(data.get("trace_id"))
            elif ev == "delta":
                buf.append(data.get("text", ""))
                out.markdown("".join(buf))
            elif ev == "error":
                error_msg = data.get("message", "Unknown error")
                typing.update(label=f"Error: {error_msg}", state="error")
                break
            elif ev == "final":
                final = data.get("answer", {})
                set_last_answer(final)
                typing.update(label="Done", state="complete")
    except Exception as e:
        error_msg = str(e)
        typing.update(label=f"Error: {error_msg}", state="error")
    if error_msg:
        st.error(f"{error_msg}", icon="🚨")
    if final:
        st.subheader("Summary")
        st.write(final.get("summary", ""))
        cols = st.columns(3)
        with cols[0]:
            st.subheader("Findings")
            for x in final.get("findings", []):
                st.markdown(f"- {x}")
        with cols[1]:
            st.subheader("Actions")
            for x in final.get("actions", []):
                st.markdown(f"- {x}")
        with cols[2]:
            st.subheader("Insights")
            for x in final.get("insights", []):
                st.markdown(f"- {x}")
        tag = final.get("explainability_tag", "")
        st.caption(f"Explainability: `{tag}`")
        # No-citation UX
        if tag == "no_citation_context":
            st.info("Answer provided without retrieved context.", icon="ℹ️")
        render_citations(final.get("citations", []))

        # Export button
        if st.button("Export Summary (PDF)"):
            trace = get_trace_id() or "adv_demo"
            payload = {
                "trace_id": trace,
                "client": "demo",
                "module": "advisor",
                "title": "Advisor Summary",
                "content": final.get("summary", ""),
                "branding": {"client_name": "DEMO", "watermark": "Sandbox"},
            }
            r = requests.post(f"{API}/v1/export/pdf", json=payload, timeout=30)
            if r.ok:
                resp = r.json()
                st.success(
                    f"Exported to {resp.get('path')} • branding_ok={resp.get('export_branding_compliance')}"
                )
            else:
                st.error(f"Export failed: {r.text}")
import requests

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
    url = "http://localhost:8000/v1/advisor/answer"
    body = {"query": question, "persona": "cpo", "top_k": 6, "workspace": workspace}
    start = time.time()
    ttfa_ms = None
    buffer = ""
    trace_id = None
    status.info("Thinking...", icon="⏳")
    for evt in stream_sse(url, body):
        if evt.get("event") == "delta":
            if ttfa_ms is None:
                ttfa_ms = int((time.time() - start) * 1000)
            buffer += evt.get("text", "")
            trace_id = evt.get("trace_id", trace_id)
            set_state("advisor_buffer", buffer)
            set_state("advisor_trace_id", trace_id)
            placeholder.markdown(buffer)
        elif evt.get("event") == "error":
            status.error(
                f"Error: {evt.get('message')} (trace_id: {evt.get('trace_id')})"
            )
            set_state("advisor_error", evt.get("message"))
            set_state("advisor_trace_id", evt.get("trace_id"))
            st.button("Retry", key="advisor_retry")
            break
        elif evt.get("event") == "final":
            status.empty()
            answer = evt.get("answer", {})
            set_state("advisor_final", answer)
            set_state("advisor_citations", answer.get("citations", []))
            set_state("advisor_trace_id", answer.get("trace_id"))
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
            trace_id = answer.get("trace_id")
            st.markdown(f"---\nTrace ID: `{trace_id}`")
            st.button(
                "Copy trace ID",
                key="copy_trace_id",
                on_click=lambda: st.session_state.update({"copied_trace_id": trace_id}),
            )
            # Telemetry
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
