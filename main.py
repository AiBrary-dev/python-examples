import base64
import os
import random
from typing import Tuple

import httpx
import streamlit as st
from aibrary import AiBrary
from aibrary.resources.models import Model

from categories.chat import chat_category
from categories.embedding import rag_category
from categories.image import image_category
from categories.multimodal import multimodal_category
from categories.object_detection import object_detection_category
from categories.ocr import ocr_category
from categories.stt import stt_category
from categories.translation import translation_category
from categories.tts import tts_category
from utils.model_info_generator import generate_markdown_for_models
from utils.render_model_option import get_all_models_cached, render_model_option


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    return html


def intro():
    import streamlit as st

    logo = render_svg(open("assets/AiBrary - Logo - PRP.svg").read())
    st.markdown(
        f"""
    <h1 style="display: flex; align-items: center;">
        Welcome to
        {logo}
        👋
    </h1>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""

    # Main view
    with st.form("api_key_form"):
        col1, col2 = st.columns(
            spec=[0.7, 0.2],
            vertical_alignment="bottom",
            gap="small",
        )

        with col1:
            main_api_key = st.text_input(
                "🔑 Enter your API Key",
                key="api_key_field",
                value=st.session_state["api_key"],
                type="password",
            )

        with col2:
            submitted = st.form_submit_button(
                "Enter",
                icon="🚪",
            )
            if submitted:
                if "all_models" in st.session_state:
                    del st.session_state["all_models"]
                st.session_state["api_key"] = main_api_key
                st.rerun()

        st.markdown(
            "Don't have an API Key? [Click here to get your API key.](https://www.aibrary.dev/dashboard/apikey)"
        )


def sidebar() -> Tuple["Model", "AiBrary"]:

    import streamlit as st
    from aibrary import AiBrary

    with st.sidebar:
        aibrary_api_key = st.text_input(
            "AiBrary API Key",
            key="api_key_field_side_bar",
            value=st.session_state["api_key"],
            type="password",
        )

        if aibrary_api_key != st.session_state["api_key"]:
            st.session_state["api_key"] = aibrary_api_key
            if "all_models" in st.session_state:
                del st.session_state["all_models"]

        try:
            aibrary = (
                AiBrary(
                    api_key=aibrary_api_key,
                )
                if aibrary_api_key
                else AiBrary()
            )
            categories = sorted(
                {item.category for item in get_all_models_cached(aibrary)} - {"chat"}
            )

            categories.insert(0, "chat")
            category_name = st.selectbox(
                "Choose a category",
                categories,
                format_func=lambda x: {
                    "tts": "text to speech",
                    "stt": "speech to text",
                    "embedding": "RAG",
                }
                .get(x, x)
                .title(),
            )
            if category_name == "intro":
                return None, None
            models, model_name = render_model_option(aibrary, category_name)

            # Add this stmt here
            st.session_state["api_key"] = aibrary_api_key

            return models[model_name], aibrary
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                st.warning("Unauthorized: Please check your credentials.")
            elif e.response.status_code == 402:
                st.warning("Payment Required: Please check your account credit.")
            elif e.response.status_code == 500:
                st.warning("Server Error: Something went wrong on the server.")
            elif e.response.status_code == 503:
                st.warning("Service Unavailable: The server is currently unavailable. Please try again later.")
            else:
                st.warning(f"Unexpected error occurred: {e.response.status_code} - {e.response.reason_phrase}")

    return None, None


def page_router(demo_name: str, model: "Model", aibrary: "AiBrary"):

    if demo_name == "intro":
        intro()
    elif demo_name == "chat":
        chat_category(model, aibrary)
    elif demo_name == "multimodal":
        multimodal_category(model, aibrary)
    elif demo_name == "image":
        image_category(model, aibrary)
    elif demo_name == "ocr":
        ocr_category(model, aibrary)
    elif demo_name == "object detection":
        object_detection_category(model, aibrary)
    elif demo_name == "stt":
        stt_category(model, aibrary)
    elif demo_name == "tts":
        tts_category(model, aibrary)
    elif demo_name == "translation":
        translation_category(model, aibrary)
    elif demo_name == "embedding":
        rag_category(model, aibrary)
    else:
        st.markdown("## 🚧 This category is under development.")
        st.markdown("## 🚧 We are working on it...")


st.set_page_config(
    page_title="AiBrary",
    page_icon="assets/AiBrary - Icon - PRM.svg",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
try:
    model, aibrary = sidebar()
    generate_markdown_for_models(model)
except:
    model, aibrary = None, None

demo_name = model.category if model else "intro"
page_router(demo_name, model, aibrary)
