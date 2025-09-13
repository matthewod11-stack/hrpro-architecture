import streamlit as st

from app.ui.state import route_to_advisor
from app.ui.tokens import BG_CARD, BORDER_MID, FG_MUTED, RADIUS_MD, SPACE_MD, SPACE_SM


def render_tiles():
    tiles = [
        {
            "title": "Advisor",
            "desc": "Ask your CPO. Streaming answers with citations.",
            "action": lambda: route_to_advisor(None),
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
            style = (
                f"background:{BG_CARD};border-radius:{RADIUS_MD}px;border:1px solid {BORDER_MID};"
                f"padding:{SPACE_MD}px;margin-bottom:{SPACE_SM}px;"
            )
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
