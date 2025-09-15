import streamlit as st

from app.services import telemetry


def set_seed_query(text: str):
    st.session_state["seed_query"] = text


def route_to_advisor(text: str | None = None):
    if text:
        st.session_state["seed_query"] = text
        st.query_params["q"] = text
    try:
        st.switch_page("ui/pages/01_Advisor.py")
    except Exception:
        st.rerun()


def get_trace_id() -> str | None:
    return st.session_state.get("trace_id")


def set_trace_id(tid: str):
    st.session_state["trace_id"] = tid


def set_last_answer(ans: dict):
    st.session_state["last_answer"] = ans


def get_state(key, default=None):
    return st.session_state.get(key, default)


def set_state(key, value):
    st.session_state[key] = value


def clear_advisor_state():
    for k in [
        "advisor_buffer",
        "advisor_final",
        "advisor_trace_id",
        "advisor_citations",
        "advisor_error",
    ]:
        if k in st.session_state:
            del st.session_state[k]


def emit_telemetry(name: str, payload: dict) -> None:
    try:
        telemetry.emit(name, payload)
    except Exception as e:
        print(f"[telemetry] Logging failed: {e}")
