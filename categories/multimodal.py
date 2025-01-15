from utils.file_tools import decode_file, encode_file, prepare_audio, prepare_image
from utils.title_with_btn import title_with_clearBtn

from aibrary import AiBrary
from aibrary.resources.models import Model


def multimodal_category(model: "Model", aibrary: "AiBrary"):

    import streamlit as st
    from PIL import Image

    isAudio = "audio" in model.model_name
    st.session_state.setdefault("multimodal_data", [])
    st.session_state.setdefault("next_prompt_data", [])
    st.session_state.setdefault("multimodal_file_uploader_key", 0)
    st.session_state.setdefault("multimodal_audio_input_key", 1)
    title_with_clearBtn("🖼️🎤📝 Multimodal", ["multimodal_data", "next_prompt_data"])
    for message in st.session_state.multimodal_data:
        if "type" in message:
            with st.chat_message(message["role"]):
                if (tmessage := message.get("type")) is not None and tmessage == "text":
                    st.markdown(message["content"])
                elif tmessage == "image":
                    st.image(decode_file(message["content"]))
                elif tmessage == "audio":
                    st.audio(decode_file(message["content"]))
    if isAudio:
        voice_input = st.audio_input(
            "Record your voice",
            key=st.session_state["multimodal_audio_input_key"],
        )
    else:
        voice_input = None
    uploaded_file = st.file_uploader(
        "Upload an image or audio file",
        type=["jpg", "png", "jpeg", "mp3", "wav"],
        key=st.session_state["multimodal_file_uploader_key"],
    )
    if uploaded_file or voice_input:
        with st.chat_message("user"):
            if uploaded_file:
                if uploaded_file.type.startswith("image"):
                    image_file = uploaded_file.read()
                    image = Image.open(uploaded_file)
                    st.image(
                        image,
                        caption="Uploaded Image",
                    )
                    st.session_state.multimodal_data.append(
                        {
                            "role": "user",
                            "type": "image",
                            "content": encode_file(image_file),
                        }
                    )
                    st.session_state.next_prompt_data.append(
                        prepare_image(uploaded_file.type, image_file)
                    )
                if uploaded_file.type.startswith("audio"):
                    voice_input = uploaded_file
            if voice_input:
                audio_file = voice_input.read()
                st.audio(
                    voice_input,
                )
                st.session_state.multimodal_data.append(
                    {
                        "role": "user",
                        "type": "audio",
                        "content": encode_file(audio_file),
                    }
                )
                st.session_state.next_prompt_data.append(
                    prepare_audio(voice_input.type, audio_file)
                )
            st.session_state["multimodal_file_uploader_key"] += 1
            st.session_state["multimodal_audio_input_key"] += 1

    if prompt := st.chat_input("Describe the file or ask a question:") or voice_input:
        if not voice_input and prompt:

            st.session_state.multimodal_data.append(
                {"role": "user", "type": "text", "content": prompt}
            )
            st.session_state.next_prompt_data.append(
                {"role": "user", "content": prompt}
            )
            with st.chat_message("user"):
                st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                response = aibrary.chat.completions.create(
                    model=f"{model.model_name}@{model.provider}",
                    messages=st.session_state.next_prompt_data,
                    modalities=["text", "audio"] if isAudio else None,
                    audio={"voice": "alloy", "format": "wav"} if isAudio else None,
                )
                if isAudio and response.choices[0].message.audio:
                    response_audio = response.choices[0].message.audio.data
                    response_transcript = response.choices[0].message.audio.transcript
                    audio_response = decode_file(response_audio)
                    st.audio(audio_response)
                    st.markdown(response_transcript)
                    st.session_state.multimodal_data.append(
                        {
                            "role": "assistant",
                            "type": "audio",
                            "content": response_audio,
                        }
                    )
                    st.session_state.multimodal_data.append(
                        {
                            "role": "assistant",
                            "type": "text",
                            "content": response_transcript,
                        }
                    )
                    st.session_state.next_prompt_data.append(
                        {
                            "role": "assistant",
                            "content": response_transcript,
                        }
                    )

                else:
                    response = response.choices[0].message.content

                    st.markdown(response)
                    st.session_state.multimodal_data.append(
                        {"role": "assistant", "type": "text", "content": response}
                    )
                    st.session_state.next_prompt_data.append(
                        {
                            "role": "assistant",
                            "content": response,
                        }
                    )
            except Exception as e:
                st.error(f"Error: {e}")

        st.rerun()
