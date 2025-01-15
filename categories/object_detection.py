from aibrary import AiBrary
from aibrary.resources.models import Model


def object_detection_category(model: "Model", aibrary: "AiBrary"):

    import streamlit as st
    from PIL import Image
    from utils.file_tools import decode_file, draw_box_object_detection, encode_file
    from utils.title_with_btn import title_with_clearBtn

    st.session_state.setdefault("object_detection_data", [])
    title_with_clearBtn("🖼️ Object Detection", ["object_detection_data"])
    st.session_state.setdefault("object_detection_file_uploader_key", 0)

    for message in st.session_state.object_detection_data:
        with st.chat_message(message["role"]):
            if message["type"] == "image":
                st.image(decode_file(message["content"]))
            elif message["type"] == "json":
                st.code(message["content"], language="json", wrap_lines=True)
            else:
                st.markdown(message["content"])

    uploaded_file = st.file_uploader(
        "Upload an image or audio file",
        type=["jpg", "png", "jpeg"],
        key=st.session_state.object_detection_file_uploader_key,
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
            st.session_state.object_detection_data.append(
                {"role": "user", "type": "image", "content": encode_file(image_file)}
            )
            response = aibrary.object_detection(
                providers=model.model_name,
                file=image_file,
                file_name=uploaded_file.name,
            )
            with st.chat_message("assistant"):

                try:
                    response_file = draw_box_object_detection(image_file, response)
                    st.image(response_file)
                    st.session_state.object_detection_data.append(
                        {
                            "role": "assistant",
                            "type": "image",
                            "content": encode_file(response_file),
                        },
                    )
                except:
                    pass
                finally:
                    st.session_state.object_detection_data.append(
                        {
                            "role": "assistant",
                            "type": "json",
                            "content": response.model_dump(),
                        },
                    )
                    st.code(response.model_dump(), language="json", wrap_lines=True)
                    st.session_state.object_detection_file_uploader_key += 1
                    st.rerun()
