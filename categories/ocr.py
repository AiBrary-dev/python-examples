from aibrary import AiBrary
from aibrary.resources.models import Model


def ocr_category(model: "Model", aibrary: "AiBrary"):
    import streamlit as st
    from PIL import Image
    from utils.file_tools import decode_file, draw_box_ocr, encode_file
    from utils.title_with_btn import title_with_clearBtn

    st.subheader("Optical Character Recognition")
    st.session_state.setdefault("ocr_data", [])
    title_with_clearBtn("🖼️ OCR", ["ocr_data"])
    st.session_state.setdefault("ocr_file_uploader_key", 0)

    for message in st.session_state.ocr_data:
        with st.chat_message(message["role"]):
            if message["type"] == "json":
                st.code(message["content"], language="json", wrap_lines=True)
            elif message["type"] == "image":
                st.image(decode_file(message["content"]))
            else:
                st.code(message["content"], language="md", wrap_lines=True)

    uploaded_file = st.file_uploader(
        "Upload an image or audio file",
        type=["jpg", "png", "jpeg"],
        key=st.session_state.ocr_file_uploader_key,
    )
    if uploaded_file:
        if uploaded_file.type.startswith("image"):
            image_file = uploaded_file.read()
            image = Image.open(uploaded_file)
            with st.chat_message("user"):
                st.image(
                    image,
                    caption="Uploaded Image",
                )
            st.session_state.ocr_data.append(
                {"role": "user", "type": "image", "content": encode_file(image_file)}
            )
            response = aibrary.ocr(
                providers=model.model_name,
                file=image_file,
                file_name=uploaded_file.name,
            )
            with st.chat_message("assistant"):

                try:
                    response_file = draw_box_ocr(image_file, response)
                    st.image(response_file)
                    st.session_state.ocr_data.extend(
                        [
                            {
                                "role": "assistant",
                                "type": "image",
                                "content": encode_file(response_file),
                            },
                        ]
                    )

                except:
                    st.warning("Draw box failed for this image")
                finally:
                    st.code(response.model_dump(), language="json", wrap_lines=True)
                    st.code(response.text, language="md", wrap_lines=True)
                    st.session_state.ocr_data.extend(
                        [
                            {
                                "role": "assistant",
                                "type": "json",
                                "content": response.model_dump(),
                            },
                            {
                                "role": "assistant",
                                "type": "text",
                                "content": response.text,
                            },
                        ]
                    )
                    st.session_state.ocr_file_uploader_key += 1
                    st.rerun()
