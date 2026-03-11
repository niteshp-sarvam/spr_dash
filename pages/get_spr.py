import json

import streamlit as st

from core.spr_service import get_spr, get_multiple_sprs
from ui.spr_viewer import render_spr
from utils.validators import parse_phone_numbers, validate_phone_number
from utils.export import to_json_download


def render(env: str) -> None:
    st.header("Get SPR")
    st.caption("Fetch Sarvam Parse Records for one or more phone numbers.")

    phone_input = st.text_area(
        "Phone number(s)",
        placeholder="Enter one or more phone numbers, separated by commas or newlines",
        help="You can paste a comma-separated list or one number per line.",
        key="get_spr_phone_input",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        fetch_clicked = st.button("Fetch", type="primary", use_container_width=True)

    if fetch_clicked and phone_input.strip():
        phones = parse_phone_numbers(phone_input)

        errors = []
        for p in phones:
            err = validate_phone_number(p)
            if err:
                errors.append(err)
        if errors:
            for e in errors:
                st.error(e)
            return

        with st.spinner(f"Fetching SPR for {len(phones)} number(s)..."):
            if len(phones) == 1:
                _, data = get_spr(env, phones[0])
                results = {phones[0]: data}
            else:
                results = get_multiple_sprs(env, phones)

        st.session_state["get_spr_results"] = results
        st.success(f"Fetched {len(results)} record(s).")

    results = st.session_state.get("get_spr_results")
    if results:
        st.divider()
        for phone, spr_data in results.items():
            with st.expander(f"Phone: {phone}", expanded=len(results) == 1):
                render_spr(spr_data, key_prefix=f"get_{phone}")

        json_str, filename = to_json_download(results, "spr_results.json")
        st.download_button(
            "Export all results as JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
        )
