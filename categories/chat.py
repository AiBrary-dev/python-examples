from utils.chat_hyper_param import chat_hyper_param

from aibrary import AiBrary
from aibrary.resources.models import Model


def chat_category(model: "Model", aibrary: "AiBrary"):
    import streamlit as st
    from utils.title_with_btn import title_with_clearBtn

    st.session_state.setdefault("messages_data", [])
    title_with_clearBtn("🧠 Chat", ["messages_data"])
    with st.sidebar:
        chat_hyper_param()
    for message in st.session_state.messages_data:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your message:"):
        st.session_state.messages_data.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = aibrary.chat.completions.create(
                    model=f"{model.model_name}@{model.provider}",
                    messages=st.session_state.messages_data,
                    stream=True,
                    **(
                        st.session_state.params
                        if st.session_state.get("use_hyper_param", False)
                        else {}
                    ),
                )
                response = st.write_stream(response)
                st.session_state.messages_data.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.error(f"Error: {e}")
