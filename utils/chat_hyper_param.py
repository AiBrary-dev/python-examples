import streamlit as st

# Define default hyperparameters
default_params = {
    "temperature": 1.0,
    "max_tokens": 1028,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}


def chat_hyper_param():
    # Initialize session state for hyperparameters
    if "use_hyper_param" not in st.session_state:
        st.session_state.use_hyper_param = False
    # st.sidebar.header("Use Hyperparameters")
    st.session_state.use_hyper_param = st.checkbox(
        "Use Hyperparameters",
        value=st.session_state.use_hyper_param,
        key=st.session_state.use_hyper_param,
    )
    if st.session_state.use_hyper_param:
        if "params" not in st.session_state:
            st.session_state.params = default_params.copy()

        # Editable hyperparameters
        st.session_state.params["temperature"] = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.params["temperature"],
            step=0.01,
        )

        st.session_state.params["max_tokens"] = st.sidebar.slider(
            "Max Tokens",
            min_value=1,
            max_value=32384,
            value=st.session_state.params["max_tokens"],
            step=1,
        )

        st.session_state.params["top_p"] = st.sidebar.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.params["top_p"],
            step=0.01,
        )

        st.session_state.params["frequency_penalty"] = st.sidebar.slider(
            "Frequency Penalty",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.params["frequency_penalty"],
            step=0.1,
        )

        st.session_state.params["presence_penalty"] = st.sidebar.slider(
            "Presence Penalty",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.params["presence_penalty"],
            step=0.1,
        )
        # Optionally, display current hyperparameters
        st.json(st.session_state.params, expanded=False)
