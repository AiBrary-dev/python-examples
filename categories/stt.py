from utils.file_tools import decode_file, encode_file
from utils.title_with_btn import title_with_clearBtn

from aibrary.resources.aibrary_sync import AiBrary
from aibrary.resources.models import Model


def stt_category(model: "Model", aibrary: "AiBrary"):

    import streamlit as st

    st.session_state.setdefault("stt_data", [])
    title_with_clearBtn("🎤📝 Speech to Text", ["stt_data"])

    for message in st.session_state.stt_data:
        with st.chat_message(message["role"]):
            if message["type"] == "audio":
                st.audio(decode_file(message["content"]))
            else:
                st.code(message["content"], language="md", wrap_lines=True)
    voice_input = st.audio_input(
        "Record your voice",
    )
    uploaded_file = st.file_uploader("OR Upload an audio file", type=["mp3", "wav"])
    if uploaded_file or voice_input:
        if uploaded_file and uploaded_file.type.startswith("audio"):
            voice_input = uploaded_file

        # if voice_input.type.startswith("audio"):
        audio_file = voice_input.read()
        with st.chat_message("user"):
            st.audio(
                voice_input,
            )

        response = aibrary.audio.transcriptions.create(
            model=model.model_name, file=voice_input
        )
        with st.chat_message("assistant"):
            st.code(response.text, language="md", wrap_lines=True)

        st.session_state.stt_data.extend(
            [
                {
                    "role": "user",
                    "type": "audio",
                    "content": encode_file(audio_file),
                },
                {
                    "role": "assistant",
                    "type": "text",
                    "content": response.text,
                },
            ]
        )
