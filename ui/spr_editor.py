import json
import copy

import streamlit as st


SPR_SECTIONS = [
    ("Agent Variables", "agent_variables"),
    ("Internal Variables", "internal_variables"),
    ("User Information", "user_information"),
    ("Authoring Config", "authoring_config"),
    ("Custom App Config", "custom_app_config"),
]


def render_editor(spr_data: dict, key_prefix: str = "editor") -> dict:
    """
    Render an inline SPR editor.
    Returns the modified SPR dict reflecting the user's edits.
    """
    edited = copy.deepcopy(spr_data)

    use_raw = st.toggle("Raw JSON editor", value=False, key=f"{key_prefix}_raw_toggle")

    if use_raw:
        raw = st.text_area(
            "Edit SPR JSON",
            value=json.dumps(edited, indent=2, default=str),
            height=500,
            key=f"{key_prefix}_raw_json",
        )
        try:
            edited = json.loads(raw)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
        return edited

    for section_name, section_key in SPR_SECTIONS:
        section_data = edited.get(section_key, {})
        if not isinstance(section_data, dict):
            continue

        with st.expander(section_name, expanded=(section_key == "agent_variables")):
            if not section_data:
                st.caption("Empty section.")
                continue

            cols = st.columns(2)
            for idx, (field, value) in enumerate(section_data.items()):
                str_value = str(value) if value is not None else ""
                col = cols[idx % 2]
                with col:
                    new_val = st.text_input(
                        field,
                        value=str_value,
                        key=f"{key_prefix}_{section_key}_{field}",
                        label_visibility="visible",
                    )
                    if new_val != str_value:
                        section_data[field] = new_val
            edited[section_key] = section_data

    return edited


def render_diff(original: dict, modified: dict) -> bool:
    """
    Show a side-by-side diff of changed fields.
    Returns True if there are changes, False otherwise.
    """
    changes = []
    for section_name, section_key in SPR_SECTIONS:
        orig_section = original.get(section_key, {})
        mod_section = modified.get(section_key, {})
        if not isinstance(orig_section, dict) or not isinstance(mod_section, dict):
            if orig_section != mod_section:
                changes.append((section_name, "(entire section)", str(orig_section), str(mod_section)))
            continue
        all_keys = set(list(orig_section.keys()) + list(mod_section.keys()))
        for key in sorted(all_keys):
            old_val = str(orig_section.get(key, "")) if orig_section.get(key) is not None else ""
            new_val = str(mod_section.get(key, "")) if mod_section.get(key) is not None else ""
            if old_val != new_val:
                changes.append((section_name, key, old_val, new_val))

    if not changes:
        st.info("No changes detected.")
        return False

    st.subheader(f"{len(changes)} field(s) changed")
    for section, field, old, new in changes:
        with st.container(border=True):
            st.markdown(f"**{section}** > `{field}`")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Before", value=old, disabled=True, key=f"diff_old_{section}_{field}")
            with col2:
                st.text_input("After", value=new, disabled=True, key=f"diff_new_{section}_{field}")

    return True
