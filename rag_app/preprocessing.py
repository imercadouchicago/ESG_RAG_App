import os
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import warnings

from rag_app.retriever import add_to_vector_collection

def process_document(file):
    """
    Processes a PDF document by loading its content and splitting it into text chunks.

    This function uses the PyMuPDFLoader to load the content of a PDF file and then
    splits the content into smaller text chunks using the RecursiveCharacterTextSplitter.
    The text is split based on specified separators and chunk sizes.

    Args:
        file: A file object representing the PDF document to be processed.

    Returns:
        list: A list of text chunks obtained from the PDF document.
    """
    loader = PyMuPDFLoader(file)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message=".*Empty content on page.*"
        )
        docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
    )
    list_chunks = text_splitter.split_documents(docs)
    return list_chunks

def process_directory_documents(data_dir_path: str):
    """
    Processes all PDF documents in a specified directory by converting them to text chunks.

    This function checks if the specified directory exists and creates it if it doesn't.
    It then iterates over all files in the directory, processing each PDF file by splitting
    its content into text chunks and displays a progress bar.

    Args:
        data_dir_path (str): The path to the directory containing PDF files.

    Returns:
        list: A list of dictionaries, each containing the filename and its corresponding
              text chunks.
    """
    indexed_chunks = []
    os.makedirs(os.path.dirname(data_dir_path), exist_ok=True)
    pdf_files = [f for f in os.listdir(data_dir_path) if f.endswith(".pdf")]
    total_files = len(pdf_files)

    progress_bar = st.progress(0, text=f"Processing {total_files} documents...")

    for i, filename in enumerate(pdf_files):
        file_path = os.path.join(data_dir_path, filename)
        try:
            file_chunks = process_document(file_path)
            indexed_chunks.append({"id": filename, "text": file_chunks})
            progress_percentage = (i + 1) / total_files
            progress_bar.progress(progress_percentage, text=f"Processing {filename} ({i+1}/{total_files})...")
        except Exception as e:
            st.error(f"Error processing {filename}: {e}")

    # Ensure progress bar reaches 100%
    progress_bar.progress(1.0, text=f"Processed {total_files} documents.")

    return indexed_chunks

def process_uploaded_document(uploaded_file: UploadedFile, data_dir_path: str) -> list[Document]:
    """Processes an uploaded PDF file by converting it to text chunks.

    Takes an uploaded PDF file and loads and splits the content
    into text chunks using recursive character splitting.

    Args:
        uploaded_file: A Streamlit UploadedFile object containing the PDF file

    Returns:
        A dictionary of Document objects containing the chunked text from the PDF

    Raises:
        IOError: If there are issues writing the file
        Error: If uploaded file already exists within the database
    """
    normalized_file_name = uploaded_file.name.replace(".pdf", "").translate(
                str.maketrans({"-": "_", ".": "_", " ": "_"})
            )
    new_file = open(f"{data_dir_path}/{normalized_file_name}.pdf", "wb")
    new_file.write(uploaded_file.read())

    list_doc_chunks = process_document(new_file.name)
    indexed_chunk = [{"id": new_file.name, "text": list_doc_chunks}]
    
    return indexed_chunk

def embed_downloaded_files():
    """
    Processes and embeds downloaded files using the Ollama embedding function.
    """
    with st.spinner("Processing downloaded documents..."):
        indexed_chunks = process_directory_documents("./rag_app/downloads")

    if not indexed_chunks:
        st.warning("No PDF documents found in the downloads directory to process.")
        return 0

    with st.spinner("Adding documents to vector collection..."):
        collection_count = add_to_vector_collection(indexed_chunks)

    return collection_count