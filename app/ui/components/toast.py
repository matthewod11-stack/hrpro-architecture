import streamlit as st


def toast_success(msg):
    st.toast(msg, icon="✅")


def toast_info(msg):
    st.toast(msg, icon="ℹ️")


def toast_warn(msg):
    st.toast(msg, icon="⚠️")


def toast_error(msg):
    st.toast(msg, icon="❌")
