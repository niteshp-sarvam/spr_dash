import streamlit as st
import pandas as pd


SPR_SECTIONS = [
    ("Agent Variables", "agent_variables"),
    ("Internal Variables", "internal_variables"),
    ("User Information", "user_information"),
    ("Authoring Config", "authoring_config"),
    ("Custom App Config", "custom_app_config"),
]


def _render_key_value_table(data: dict) -> None:
    """Display a dict as a two-column table."""
    if not data:
        st.caption("No data in this section.")
        return
    df = pd.DataFrame(
        [{"Field": k, "Value": str(v) if v is not None else ""} for k, v in data.items()]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_spr(spr_data: dict, key_prefix: str = "") -> None:
    """
    Render a single SPR record in organized tabs.
    key_prefix avoids Streamlit widget key collisions when rendering multiple SPRs.
    """
    if isinstance(spr_data, str) and spr_data.startswith("Error"):
        st.error(spr_data)
        return

    if not spr_data or not isinstance(spr_data, dict):
        st.warning("No SPR data found for this user.")
        return

    tab_names = [name for name, _ in SPR_SECTIONS] + ["Raw JSON"]
    tabs = st.tabs(tab_names)

    for i, (section_name, section_key) in enumerate(SPR_SECTIONS):
        with tabs[i]:
            section_data = spr_data.get(section_key, {})
            if isinstance(section_data, dict):
                _render_key_value_table(section_data)
            else:
                st.json(section_data)

    with tabs[-1]:
        st.json(spr_data)
