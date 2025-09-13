import streamlit as st

from app.ui.tokens import FG_MUTED


def render_citations(citations):
    if not citations:
        st.write("No citations.")
        return
    st.write("Citations:")
    for idx, c in enumerate(citations):
        anchor = c.get("anchor", "§?")
        source = c.get("source", "Unknown source")
        snippet = c.get("snippet", "")
        chip_key = f"citation_chip_{idx}"
        if st.button(
            anchor, key=chip_key, help=f"Source: {source}", use_container_width=False
        ):
            with st.sidebar:
                st.markdown(f"### Citation {anchor}")
                st.write(f"**Source:** {source}")
                if snippet:
                    st.write(f"**Excerpt:** {snippet}")
                else:
                    st.write("Open in sources.")
                st.write("---")
