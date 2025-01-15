from utils.file_tools import encode_file

from aibrary import AiBrary
from aibrary.resources.models import Model


def tts_category(model: "Model", aibrary: "AiBrary"):
    import streamlit as st
    from utils.file_tools import decode_file
    from utils.title_with_btn import title_with_clearBtn

    st.session_state.setdefault("tts_data", [])
    title_with_clearBtn("📝🎤 Text to Speech", ["tts_data"])

    for message in st.session_state.tts_data:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.audio(decode_file(message["content"]))
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Write something you'd like me to say!"):
        st.session_state.tts_data.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = aibrary.audio.speech.create(
                    input=prompt,
                    model=model.model_name,
                    response_format="mp3",
                    voice="FEMALE" if model.provider != "openai" else "alloy",
                )
                response = response.read()
                st.audio(response)

                st.session_state.tts_data.append(
                    {"role": "assistant", "content": encode_file(response)}
                )

            except Exception as e:
                st.error(f"Error: {e}")
