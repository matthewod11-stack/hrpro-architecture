from collections.abc import Callable

import streamlit as st


def retry_banner(message: str, on_retry: Callable):
    st.markdown(
        f"<div style='background:#fffbe6;border:1px solid #ffe58f;padding:12px;margin-bottom:8px;'>⚠️ {message}</div>",
        unsafe_allow_html=True,
    )
    if st.button("Retry", key="retry-btn"):
        on_retry()
        st.experimental_rerun()
    st.markdown(
        "<style>button:focus{outline:2px solid #4B5AEF;}</style>",
        unsafe_allow_html=True,
    )
