import json

import streamlit as st

from core.spr_service import get_multiple_sprs, update_multiple_sprs
from ui.spr_viewer import render_spr
from utils.validators import parse_phone_numbers
from utils.export import to_json_download


def _render_bulk_get(env: str) -> None:
    st.subheader("Bulk Get")
    st.caption("Fetch SPRs for many phone numbers at once.")

    input_method = st.radio(
        "Input method",
        ["Text input", "Upload file"],
        horizontal=True,
        key="bulk_get_input_method",
    )

    phones: list[str] = []

    if input_method == "Text input":
        raw = st.text_area(
            "Phone numbers (one per line or comma-separated)",
            height=150,
            placeholder="09006609353\n09666583548\n09833087071",
            key="bulk_get_text",
        )
        if raw.strip():
            phones = parse_phone_numbers(raw)
    else:
        uploaded = st.file_uploader(
            "Upload .txt or .csv with phone numbers",
            type=["txt", "csv"],
            key="bulk_get_file",
        )
        if uploaded:
            content = uploaded.read().decode("utf-8")
            phones = parse_phone_numbers(content)

    if phones:
        st.caption(f"{len(phones)} phone number(s) detected.")

    if st.button("Fetch All", type="primary", disabled=not phones, key="bulk_get_btn"):
        progress_bar = st.progress(0, text="Fetching SPRs...")

        def on_progress(done: int, total: int) -> None:
            progress_bar.progress(done / total, text=f"Fetched {done}/{total}")

        with st.spinner("Fetching..."):
            results = get_multiple_sprs(env, phones, progress_callback=on_progress)

        progress_bar.progress(1.0, text="Done!")
        st.session_state["bulk_get_results"] = results
        st.success(f"Fetched {len(results)} record(s).")

    results = st.session_state.get("bulk_get_results")
    if results:
        st.divider()

        summary_data = []
        for phone, data in results.items():
            if isinstance(data, dict):
                name = data.get("agent_variables", {}).get("user_name", "")
                status = "OK"
            else:
                name = ""
                status = str(data)[:60] if data else "No data"
            summary_data.append({"Phone": phone, "Name": name, "Status": status})

        st.dataframe(summary_data, use_container_width=True, hide_index=True)

        for phone, spr_data in results.items():
            with st.expander(f"Phone: {phone}"):
                render_spr(spr_data, key_prefix=f"bulk_get_{phone}")

        json_str, filename = to_json_download(results, "bulk_spr_results.json")
        st.download_button(
            "Export all results as JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
            key="bulk_get_export",
        )


def _render_bulk_update(env: str) -> None:
    st.subheader("Bulk Update")
    st.caption("Update SPRs for multiple users from a JSON config file.")

    uploaded = st.file_uploader(
        "Upload phone_configs JSON",
        type=["json"],
        help="Same format as phone_configs.json: keys are phone numbers, values are SPR payloads.",
        key="bulk_update_file",
    )

    phone_configs: dict | None = None

    if uploaded:
        try:
            content = uploaded.read().decode("utf-8")
            phone_configs = json.loads(content)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON file: {e}")
            return

        st.caption(f"{len(phone_configs)} user(s) in uploaded config.")

        preview_data = []
        for phone, cfg in phone_configs.items():
            agent_vars = cfg.get("agent_variables", {})
            preview_data.append({
                "Phone": phone,
                "Name": agent_vars.get("user_name", ""),
                "Policy": agent_vars.get("policy_number", ""),
                "Product": agent_vars.get("product_name", ""),
            })
        st.dataframe(preview_data, use_container_width=True, hide_index=True)

    can_update = phone_configs is not None and len(phone_configs) > 0

    if env == "Production" and can_update:
        st.warning(
            f"You are about to update **{len(phone_configs)}** SPR(s) on **Production**.",
            icon=":material/warning:",
        )

    confirm = False
    if can_update:
        confirm = st.checkbox(
            f"I confirm I want to update {len(phone_configs)} SPR(s) on **{env}**.",
            key="bulk_update_confirm",
        )

    if st.button("Update All", type="primary", disabled=not (can_update and confirm), key="bulk_update_btn"):
        progress_bar = st.progress(0, text="Updating SPRs...")

        def on_progress(done: int, total: int) -> None:
            progress_bar.progress(done / total, text=f"Updated {done}/{total}")

        with st.spinner("Updating..."):
            results = update_multiple_sprs(env, phone_configs, progress_callback=on_progress)

        progress_bar.progress(1.0, text="Done!")
        st.session_state["bulk_update_results"] = results

        successes = sum(1 for s in results.values() if s == "Success")
        failures = len(results) - successes
        if failures == 0:
            st.success(f"All {successes} update(s) succeeded!")
        else:
            st.warning(f"{successes} succeeded, {failures} failed.")

    update_results = st.session_state.get("bulk_update_results")
    if update_results:
        st.divider()
        result_data = [
            {"Phone": phone, "Status": status}
            for phone, status in update_results.items()
        ]
        st.dataframe(result_data, use_container_width=True, hide_index=True)

        json_str, filename = to_json_download(update_results, "bulk_update_results.json")
        st.download_button(
            "Export results as JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
            key="bulk_update_export",
        )


def render(env: str) -> None:
    st.header("Bulk Operations")

    tab_get, tab_update = st.tabs(["Bulk Get", "Bulk Update"])

    with tab_get:
        _render_bulk_get(env)

    with tab_update:
        _render_bulk_update(env)
