from aibrary.resources.models import Model


def generate_markdown_for_models(model: Model) -> str:
    import streamlit as st

    markdown = []
    markdown.append(f"### Model: {model.model_name}")
    markdown.append(f"- **Provider**: {model.provider}")
    markdown.append(f"- **Category**: {model.category}")
    if model.quality:
        markdown.append(f"- **Quality**: {model.quality}")
    if model.size:
        markdown.append(f"- **Size**: {model.size}")

    markdown.append("\n#### Pricing Information")
    markdown.append("| Unit Type | Price Per Input Unit | Price Per Output Unit |")
    markdown.append("|-----------|-----------------------|------------------------|")
    for pricing in model.ai_models_pricing:
        markdown.append(
            f"| {pricing.unit_type} | ${pricing.price_per_input_unit:.10f} | ${pricing.price_per_output_unit:.10f} |"
        )
    with st.expander(f"See {model.model_name} info"):
        st.markdown(f"\n".join(markdown))
        codes = [
            code for cat, code in code_example.items() if cat.startswith(model.category)
        ]
        try:
            if codes:
                st.markdown(
                    f'## Examples: \n❇️ Instead of using `model="{model.model_name}"`, you can use `model="{model.model_name}@{model.provider}"`. This is helpful when a model has different providers, allowing you to specify the exact provider you want to call.'
                )
                for code in codes:
                    display_code = False
                    formatted_model = f"{model.model_name}@{model.provider}"

                    if model.category == "image":
                        display_code = True
                        formatted_code = code.format(
                            formatted_model,
                            model.size,
                            f'"{model.quality}"' if model.quality else None,
                        )
                        st.code(formatted_code, language="python")
                        continue
                    elif model.category == "multimodal":
                        if ("audio" in model.model_name and "audio" in code) or (
                            "audio" not in model.model_name and "audio" not in code
                        ):
                            display_code = True
                    else:
                        display_code = True
                        formatted_model = (
                            model.model_name
                        )  # Use model_name without provider

                    if display_code:
                        # Display the code example header
                        st.markdown(
                            f"#### Python Code Example [{model.category.title()}]:"
                        )

                        # Format and display the code snippet
                        formatted_code = code.format(formatted_model)
                        st.code(formatted_code, language="python")
        except Exception as e:
            st.error(f"Python code example not found! Sorry 😔: \n {e}")


code_example = {
    "chat-1": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.chat.completions.create(
    model="{}",
    messages=[
        {{"role": "user", "content": "How are you today?"}},
        {{"role": "assistant", "content": "I'm doing great, thank you!"}},
    ],
)
""",
    "chat-2": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.chat.completions.create(
    model="{}",
    messages=[
        {{"role": "user", "content": "How are you today?"}},
        {{"role": "assistant", "content": "I'm doing great, thank you!"}},
    ],
    stream=True,
)
""",
    "multimodal-1": """
import base64
from aibrary import AiBrary
aibrary = AiBrary()

# Function to encode the image
def encode_file(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Getting the base64 string
base64_image = encode_file("tests/assets/test-image.jpg")

return aibrary.chat.completions.create(
    model="{}",
    messages=[
        {{
            "role": "user",
            "content": [
                {{
                    "type": "text",
                    "text": "What is in this image?",
                }},
                {{
                    "type": "image_url",
                    "image_url": {{"url": f"data:image/jpeg;base64,{{base64_image}}"}},
                }},
            ],
        }}
    ],
)
""",
    "multimodal-2": """
import base64
from aibrary import AiBrary

aibrary = AiBrary()

# Function to encode the image
def encode_file(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Getting the base64 string
english_audio_base64 = encode_file("tests/assets/file.mp3")
return aibrary.chat.completions.create(
    model="{}",
    modalities=["text", "audio"],
    audio={{"voice": "alloy", "format": "wav"}},
    messages=[
        {{"role": "system", "content": "translate to persian"}},
        {{
            "role": "user",
            "content": [
                {{
                    "type": "input_audio",
                    "input_audio": {{"data": english_audio_base64, "format": "mp3"}},
                }}
            ],
        }},
    ],
)

""",
    "stt": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.audio.transcriptions.create(
    model="{}", file=open("path/to/audio", "rb")
)

""",
    "tts": """
from aibrary import AiBrary

aibrary = AiBrary()
response = aibrary.audio.speech.create(
    input="Hey Cena", model="{}", response_format="mp3", voice="alloy"
)
open("file.mp3", "wb").write(response.content)
""",
    "ocr-1": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.ocr(
    providers="{}",
    file=open("tests/assets/ocr-test.jpg", "rb").read(),
    file_name="test.jpg",
)
""",
    "ocr-2": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.ocr(providers="{}", file="tests/assets/ocr-test.jpg")
""",
    "ocr-3": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.ocr(
    providers="{}",
    file_url="https://builtin.com/sites/www.builtin.com/files/styles/ckeditor_optimize/public/inline-images/5_python-ocr.jpg",
)
""",
    "object detection-1": """
from aibrary import AiBrary
aibrary = AiBrary()

aibrary.object_detection(
    providers="{}",
    file=open("tests/assets/ocr-test.jpg", "rb").read(),
    file_name="test.jpg",
)

""",
    "object detection-2": """
from aibrary import AiBrary
aibrary = AiBrary()

aibrary.object_detection(
    providers="{}",
    file_url="https://builtin.com/sites/www.builtin.com/files/styles/ckeditor_optimize/public/inline-images/5_python-ocr.jpg",
)

""",
    "object detection-3": """
from aibrary import AiBrary
aibrary = AiBrary()

aibrary.object_detection(
    providers="{}", file="tests/assets/ocr-test.jpg"
)

""",
    "image-1": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.images.generate(model="{}", size="{}",quality={}, prompt="Draw cat")

""",
    "translation-1": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.translation.automatic_translation("HI", "{}", "en", "fa")

""",
    "embedding-1": """
from aibrary import AiBrary

aibrary = AiBrary()
aibrary.embeddings.create(
    model="{}",
    input="Hi!",
    encoding_format="float",
)

""",
}
