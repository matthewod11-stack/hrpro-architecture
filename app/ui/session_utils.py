import streamlit as st


def set_trace_id(v: str):
    st.session_state["trace_id"] = v


def get_trace_id() -> str:
    return st.session_state.get("trace_id", "")
