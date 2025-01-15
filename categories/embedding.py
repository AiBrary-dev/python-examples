import hashlib
import os
import tempfile

from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from utils.chat_hyper_param import chat_hyper_param
from utils.model_info_generator import generate_markdown_for_models

from aibrary import AiBrary
from aibrary.resources.models import Model


def hash_file(file_bytes):
    """Generate a hash for the uploaded file."""
    return hashlib.sha256(file_bytes).hexdigest()


def rag_category(embedding_model: "Model", aibrary: "AiBrary"):

    import streamlit as st
    from utils.render_model_option import render_model_option
    from utils.title_with_btn import title_with_clearBtn

    st.session_state.setdefault("rag_data", {})
    st.session_state.setdefault("rag_message_data", [])
    st.session_state.setdefault("rag_file_uploader_key", 0)
    with st.sidebar:
        models, model_name = render_model_option(
            aibrary, "chat", selectbox_title="Select a llm model"
        )
    chat_model = models[model_name]
    with st.sidebar:
        chat_hyper_param()
    generate_markdown_for_models(chat_model)
    title_with_clearBtn(
        "🦉 RAG",
        [
            "rag_message_data",
        ],
    )
    uploaded_file = st.file_uploader(
        "Upload a text file for knowledge base:",
        key=st.session_state.rag_file_uploader_key,
        type=[
            "txt",
            "pdf",
            "pptx",
            "docx",
            "xlsx",
            "xls",
            "csv",
            "jpg",
            "jpeg",
            "png",
            "mp3",
            "wav",
            "m4a",
            "html",
            "htm",
            "csv",
            "json",
            "xml",
            "zip",
            "md",
        ],
    )
    if st.button("Remove Knowledge Base"):
        st.session_state.vectorstore = None
        st.session_state.file_hash = None
        st.success("Knowledge base removed.")
        st.rerun()  # This effectively removes the current state

    for message in st.session_state.rag_message_data:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # Initialize session state for vectorstore and file hash
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "file_hash" not in st.session_state:
        st.session_state.file_hash = None

    # base_url = str(aibrary._client.base_url)
    base_url = str(aibrary._client.base_url)
    # File upload for the knowledge base

    if uploaded_file or st.session_state.vectorstore is not None:
        try:

            # Check if the uploaded file is different from the one stored in session_state
            if uploaded_file and (
                (st.session_state.vectorstore is None)
                or (st.session_state.file_hash != current_file_hash)
            ):
                # Generate a hash for the uploaded file to identify it uniquely
                file_bytes = uploaded_file.read()
                current_file_hash = hash_file(file_bytes)
                uploaded_file.seek(0)  # Reset file pointer after reading
                # Create a temporary directory to store the uploaded file
                with tempfile.TemporaryDirectory() as tmp_dir:
                    temp_file_path = os.path.join(tmp_dir, uploaded_file.name)

                    # Save the uploaded file to the temporary directory
                    with open(temp_file_path, "wb") as f:
                        f.write(file_bytes)
                    st.success(f"File saved to temporary directory: {temp_file_path}")

                    # Process the uploaded file based on its type
                    from markitdown import MarkItDown

                    md = MarkItDown()
                    result = md.convert(temp_file_path)
                    file_content = result.text_content

                    st.write("File content loaded successfully!")

                    # Split the file content into chunks
                    text_splitter = CharacterTextSplitter(
                        chunk_size=500, chunk_overlap=50
                    )
                    texts = text_splitter.split_text(file_content)
                    st.write(f"Text split into {len(texts)} chunks.")

                    # Generate embeddings and create a FAISS vector store
                    embeddings = OpenAIEmbeddings(
                        api_key=st.session_state["api_key"],
                        base_url=base_url,
                        model=embedding_model.model_name,
                        model_kwargs={
                            "encoding_format": "float",
                        },
                    )
                    vectorstore = FAISS.from_texts(texts, embeddings)
                    st.success("Knowledge base created!")

                    # Store the vectorstore and file hash in session_state
                    st.session_state.vectorstore = vectorstore
                    st.session_state.file_hash = current_file_hash
                    st.session_state["rag_file_uploader_key"] += 1
            else:
                st.info("Using cached knowledge base.")

            # Initialize LLM and set up the QA chain only if vectorstore is available
            if st.session_state.vectorstore:
                llm = ChatOpenAI(
                    api_key=st.session_state["api_key"],
                    base_url=base_url,
                    model=f"{chat_model.model_name}@{chat_model.provider}",
                    **(
                        st.session_state.params
                        if st.session_state.get("use_hyper_param", False)
                        else {}
                    ),
                )

                # Define the RetrievalQA chain with the custom prompt
                qa = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",  # 'stuff' combines all retrieved docs
                    retriever=st.session_state.vectorstore.as_retriever(),
                    return_source_documents=False,
                )

                # User input for query
                query = st.chat_input("Ask your question:")
                if query:
                    with st.chat_message("user"):
                        st.markdown(query)

                    with st.chat_message("assistant"):
                        with st.spinner("Generating response..."):
                            answer = qa.run(query)
                            st.markdown(answer)
                    st.session_state.rag_message_data.append(
                        {"role": "user", "content": query}
                    )
                    st.session_state.rag_message_data.append(
                        {"role": "assistant", "content": answer}
                    )
                    st.rerun()

        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
            st.error(f"An error occurred while processing the file: {e}")
