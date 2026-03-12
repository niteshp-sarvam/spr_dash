import streamlit as st
import streamlit_authenticator as stauth
import yaml

st.set_page_config(
    page_title="SPR Tool",
    page_icon=":material/database:",
    layout="wide",
    initial_sidebar_state="expanded",
)

CREDENTIALS_PATH = "config/credentials.yaml"

authenticator = stauth.Authenticate(CREDENTIALS_PATH)

authenticator.login()

if not st.session_state.get("authentication_status"):
    if st.session_state.get("authentication_status") is False:
        st.error("Incorrect username or password.")
    st.stop()

from ui.sidebar import render_sidebar
from pages import get_spr, update_spr, bulk_operations

env = render_sidebar(authenticator)

page = st.navigation(
    [
        st.Page(lambda: get_spr.render(env), title="Get SPR", icon=":material/search:", url_path="get"),
        st.Page(lambda: update_spr.render(env), title="Update SPR", icon=":material/edit:", url_path="update"),
        st.Page(lambda: bulk_operations.render(env), title="Bulk Operations", icon=":material/inventory_2:", url_path="bulk"),
    ]
)

page.run()
