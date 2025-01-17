import os
from typing import Tuple

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


def intro():
    import streamlit as st

    st.markdown(
        """
    <h1 style="display: flex; align-items: center;">
        Welcome to
        <img src="https://www.aibrary.dev/_next/static/media/logo.3c3e5d20.svg" alt="Logo" style="margin-left: 10px; width: 200px;">
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
        st.session_state["api_key"] = os.environ.get("AIBRARY_API_KEY", "")

    with st.form("api_key_form"):
        col1, col2 = st.columns(
            spec=[0.7, 0.2],
            vertical_alignment="bottom",
            gap="small",
        )

        with col1:
            main_api_key = st.text_input(
                "🔑 Enter your API Key",
                value=st.session_state["api_key"],
                type="password",
            )

        with col2:
            submitted = st.form_submit_button("Enter", icon="🚪")
        if submitted:
            # Update the session state on form submission
            st.session_state["api_key"] = main_api_key

    # def update_api_key(new_value):
    #     st.session_state["api_key"] = new_value
    #     st.rerun()

    # col1, col2 = st.columns(
    #     spec=[0.7, 0.2],
    #     vertical_alignment="bottom",
    #     gap="small",
    # )

    # with col1:
    #     main_api_key = st.text_input(
    #         "🔑 Enter your API Key",
    #         value=st.session_state["api_key"],
    #         on_change=lambda: update_api_key(st.session_state["api_key"]),
    #         type="password",
    #     )
    # with col2:
    #     if st.button(
    #         "Enter",
    #         icon="🚪",
    #     ):
    #         if main_api_key != st.session_state["api_key"]:
    #             update_api_key(main_api_key)


def sidebar() -> Tuple["Model", "AiBrary"]:

    import streamlit as st
    from aibrary import AiBrary

    with st.sidebar:
        if (
            aibrary_api_key := st.text_input(
                "AiBrary API Key",
                key="aibrary_api_key",
                value=st.session_state["api_key"],
                type="password",
            )
            or os.environ.get("AIBRARY_API_KEY") is not None
        ):
            if not aibrary_api_key:
                aibrary_api_key = os.environ.get("AIBRARY_API_KEY")
                st.rerun()
            st.session_state["api_key"] = aibrary_api_key
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
                format_func=lambda x: {"embedding": "rag"}.get(x, x).title(),
            )
            if category_name == "intro":
                return None, None
            models, model_name = render_model_option(aibrary, category_name)

            return models[model_name], aibrary
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
    page_icon="https://3389077816-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/organizations%2F2FbkTed5GwFvxgjieEqg%2Fsites%2Fsite_BrVCS%2Ficon%2FT6IoEo4vpVFwZq7zZU5N%2FAiBrary%20-%20Icon%20-%20PRM.svg?alt=media&token=08764038-7540-4388-b061-fe4f19b6636e",
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
