from aibrary import AiBrary
from aibrary.resources.models import Model


def translation_category(model: "Model", aibrary: "AiBrary"):

    import streamlit as st
    from utils.title_with_btn import title_with_clearBtn

    st.session_state.setdefault("translation_data", [])
    title_with_clearBtn("🌎 Translation", ["translation_data"])

    languages = {
        "en": "English",
        "fa": "Persian",
        "af": "Afrikaans",
        "ar": "Arabic",
        "bn": "Bengali",
        "bg": "Bulgarian",
        "ca": "Catalan",
        "zh": "Chinese",
        "hr": "Croatian",
        "cs": "Czech",
        "da": "Danish",
        "nl": "Dutch",
        "et": "Estonian",
        "fi": "Finnish",
        "fr": "French",
        "de": "German",
        "el": "Greek",
        "he": "Hebrew",
        "hi": "Hindi",
        "hu": "Hungarian",
        "id": "Indonesian",
        "it": "Italian",
        "ja": "Japanese",
        "ko": "Korean",
        "lv": "Latvian",
        "lt": "Lithuanian",
        "ms": "Malay",
        "no": "Norwegian",
        "pl": "Polish",
        "pt": "Portuguese",
        "ro": "Romanian",
        "ru": "Russian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "es": "Spanish",
        "sv": "Swedish",
        "th": "Thai",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "vi": "Vietnamese",
    }

    # Dropdowns for source and destination languages
    col1, col2 = st.columns(2)

    with col1:
        source_language = st.selectbox(
            "Source Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
        )

    with col2:
        destination_language = st.selectbox(
            "Destination Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=1,
        )

    # Display selected languages
    st.write(f"Source Language: {languages[source_language]} ({source_language})")
    st.write(
        f"Destination Language: {languages[destination_language]} ({destination_language})"
    )

    for message in st.session_state.translation_data:
        with st.chat_message(message["role"]):
            st.code(message["content"], language="md", wrap_lines=True)

    if prompt := st.chat_input("Write something you'd like to translate!"):
        st.session_state.translation_data.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = aibrary.translation(
                    source_language=source_language,
                    target_language=destination_language,
                    text=prompt,
                    model=model.model_name,
                )
                st.code(response.text, language="md", wrap_lines=True)

                st.session_state.translation_data.append(
                    {"role": "assistant", "content": response.text}
                )

            except Exception as e:
                st.error(f"Error: {e}")
