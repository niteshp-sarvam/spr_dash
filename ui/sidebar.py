import streamlit as st

from core.config import ENVIRONMENTS


def render_sidebar() -> str:
    """Render the shared sidebar and return the selected environment name."""
    with st.sidebar:
        st.title("SPR Tool")
        st.divider()

        env = st.radio(
            "Environment",
            options=list(ENVIRONMENTS.keys()),
            index=0,
            help="Select the target environment for all SPR operations.",
        )

        env_cfg = ENVIRONMENTS[env]
        if env == "Production":
            st.warning("You are on **PRODUCTION**. Changes affect live data.")
        else:
            st.info(f"Connected to **{env}**")

        st.caption(f"App ID: `{env_cfg['app_id']}`")

        st.divider()
        st.caption("Sarvam Parse Records Manager")

    return env
