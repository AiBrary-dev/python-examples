def title_with_clearBtn(title: str, key: list | str):

    import streamlit as st

    col1, col2 = st.columns(
        spec=[0.7, 0.2],
        vertical_alignment="center",
        gap="large",
    )

    with col1:
        st.title(title)

    with col2:
        if isinstance(key, str):
            key = [key]

        if st.button("Clear All", icon="🗑"):
            for item in key:
                st.session_state.get(item, {}).clear()
            st.rerun()
