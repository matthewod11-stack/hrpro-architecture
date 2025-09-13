import streamlit as st

from ui.state import route_to_advisor


def render_tiles():
    st.write("### Modules")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Advisor", use_container_width=True):
            route_to_advisor(None)
        st.caption("Ask your CPO. Streaming answers with citations.")
    with c2:
        st.button("Dashboards (coming soon)", disabled=True, use_container_width=True)
        st.caption("eNPS & Attrition.")
    with c1:
        st.button("Builders (coming soon)", disabled=True, use_container_width=True)
        st.caption("30/60/90, PIP.")
    with c2:
        st.button("Exports (coming soon)", disabled=True, use_container_width=True)
    st.caption("Branded PDFs/CSVs.")


from app.ui.tokens import BG_CARD, BORDER_MID, FG_MUTED, RADIUS_MD, SPACE_MD, SPACE_SM


def render_tiles():
    tiles = [
        {
            "title": "Advisor",
            "desc": "Ask your CPO. Streaming answers with citations.",
            "action": lambda: st.session_state.update({"seed_query": ""})
            or st.switch_page("ui/pages/01_Advisor.py"),
            "enabled": True,
        },
        {
            "title": "Dashboards",
            "desc": "View HR dashboards (coming soon).",
            "action": lambda: st.info("Dashboards not ready."),
            "enabled": False,
        },
        {
            "title": "Builders",
            "desc": "Create onboarding plans, PIPs, and more (coming soon).",
            "action": lambda: st.info("Builders not ready."),
            "enabled": False,
        },
        {
            "title": "Exports",
            "desc": "Export data with branding compliance (coming soon).",
            "action": lambda: st.info("Exports not ready."),
            "enabled": False,
        },
    ]
    cols = st.columns(2)
    for i, tile in enumerate(tiles):
        with cols[i % 2]:
            style = f"background:{BG_CARD};border-radius:{RADIUS_MD}px;border:1px solid {BORDER_MID};padding:{SPACE_MD}px;margin-bottom:{SPACE_SM}px;"
            st.markdown(
                f"<div style='{style}'>"
                f"<b>{tile['title']}</b><br>"
                f"<span style='color:{FG_MUTED};font-size:0.95em'>{tile['desc']}</span><br>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if tile["enabled"]:
                if st.button(f"Go to {tile['title']}", key=f"tile_{tile['title']}"):
                    tile["action"]()
            else:
                st.button(
                    f"Go to {tile['title']}", key=f"tile_{tile['title']}", disabled=True
                )
