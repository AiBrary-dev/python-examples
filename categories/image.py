from aibrary import AiBrary
from aibrary.resources.models import Model


def image_category(model: "Model", aibrary: "AiBrary"):

    import streamlit as st
    from openai.types.images_response import ImagesResponse
    from utils.file_tools import decode_file
    from utils.title_with_btn import title_with_clearBtn

    st.session_state.setdefault("image_data", [])
    title_with_clearBtn("🖼️ Image Generation", ["image_data"])
    for message in st.session_state.image_data:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.image(decode_file(message["content"]))
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("What you want to draw?"):
        st.session_state.image_data.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response: ImagesResponse = aibrary.images.generate(
                    model=f"{model.model_name}",
                    prompt=prompt,
                    size=model.size,
                    quality=model.quality,
                    response_format="b64_json",
                    n=1,
                )
                if len(response.data) == 0:
                    st.error("🔴 No image generated")
                    return
                st.session_state.image_data.append(
                    {"role": "assistant", "content": response.data[0].b64_json}
                )
                st.image(decode_file(response.data[0].b64_json))

            except Exception as e:
                st.error(f"Error: {e}")
