import streamlit as st

from ui.tokens import FG_MUTED


def render_citations(citations: list[dict]):
    if not citations:
        st.caption("No citations.")
        return
    st.write("**Citations**")
    import streamlit.components.v1 as components

    cols = st.columns(min(4, len(citations)))
    # Track last focused chip
    if "_last_cit_chip" not in st.session_state:
        st.session_state["_last_cit_chip"] = None
    for i, c in enumerate(citations):
        anchor = c.get("anchor", "§")
        chip_key = f"cit_{i}"
        # Use HTML button for a11y, aria-label
        chip_html = f'<button tabindex="0" aria-label="Citation {anchor}" style="margin:2px;padding:6px 12px;border-radius:8px;background:{FG_MUTED};color:white;border:none;cursor:pointer;" id="{chip_key}">{anchor}</button>'
        components.html(chip_html, height=32)
        # Streamlit button for click
        if st.button(anchor, key=chip_key):
            st.session_state["_last_cit_chip"] = chip_key
            with st.sidebar:
                st.subheader(anchor)
                st.caption(c.get("source", ""))
                st.code(c.get("snippet", ""), language=None)
                p = c.get("path", "")
                if p:
                    st.markdown(
                        f"<span style='color:{FG_MUTED}'>Path:</span> `{p}`",
                        unsafe_allow_html=True,
                    )
                # Close button
                if st.button("Close", key=f"close_{chip_key}"):
                    st.session_state["_last_cit_chip"] = None
                    # Focus returns to last chip (handled by browser)


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
