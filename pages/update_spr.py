import streamlit as st

from core.spr_service import get_spr, update_spr
from ui.spr_editor import render_editor, render_diff
from utils.validators import validate_phone_number


def render(env: str) -> None:
    st.header("Update SPR")
    st.caption("Fetch a user's current SPR, edit fields, review changes, and push the update.")

    # ── Step 1: Fetch ────────────────────────────────────────────────────
    st.subheader("Step 1: Fetch current SPR")
    col1, col2 = st.columns([3, 1])
    with col1:
        phone = st.text_input(
            "Phone number",
            placeholder="e.g. 09006609353",
            help="Enter the phone number of the user whose SPR you want to update.",
            key="update_phone_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_clicked = st.button("Fetch Current SPR", type="primary", use_container_width=True)

    if fetch_clicked and phone.strip():
        err = validate_phone_number(phone.strip())
        if err:
            st.error(err)
            return

        with st.spinner("Fetching current SPR..."):
            _, data = get_spr(env, phone.strip())

        if isinstance(data, str) and data.startswith("Error"):
            st.error(data)
            return
        if not data or not isinstance(data, dict):
            st.warning("No SPR data found for this user.")
            return

        st.session_state["update_original_spr"] = data
        st.session_state["update_phone"] = phone.strip()
        st.session_state["update_confirmed"] = False
        st.success("SPR loaded. Edit fields below.")

    original = st.session_state.get("update_original_spr")
    current_phone = st.session_state.get("update_phone", "")

    if not original:
        return

    # ── Step 2: Edit ─────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 2: Edit fields")
    edited = render_editor(original, key_prefix="update_editor")

    # ── Step 3: Review ───────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 3: Review changes")
    has_changes = render_diff(original, edited)

    # ── Step 4: Confirm & Update ─────────────────────────────────────────
    if has_changes:
        st.divider()
        st.subheader("Step 4: Confirm update")

        if env == "Production":
            st.warning(
                "You are about to update a **Production** SPR. This will affect live data.",
                icon=":material/warning:",
            )

        confirm = st.checkbox(
            f"I confirm I want to update SPR for **{current_phone}** on **{env}**.",
            key="update_confirm_checkbox",
        )

        if st.button("Update SPR", type="primary", disabled=not confirm):
            with st.spinner("Updating SPR..."):
                _, status = update_spr(env, current_phone, edited)

            if status == "Success":
                st.success(f"SPR for {current_phone} updated successfully!")
                st.toast("SPR updated!", icon=":material/check_circle:")
                st.session_state["update_original_spr"] = edited
                st.session_state["update_confirmed"] = True
            else:
                st.error(f"Update failed: {status}")
