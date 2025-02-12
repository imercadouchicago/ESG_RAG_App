import os
import streamlit as st

from rag_app.preprocessing import process_uploaded_document
from rag_app.retriever import add_to_vector_collection, query_collection
from rag_app.fusion import query_augmentation, reciprocal_rank_fusion
from rag_app.reranking import re_rank_cross_encoders
from rag_app.generator import call_llm

DATA_DIR_PATH = os.environ["DATA_DIR_PATH"]

# Document Upload Area
with st.sidebar:
    st.set_page_config(page_title="Sustainability Reports Chatbot")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf"], accept_multiple_files=False)
    process = st.button("Process")

    if uploaded_file and process:
        indexed_chunk = process_uploaded_document(uploaded_file, DATA_DIR_PATH)
        count = add_to_vector_collection(indexed_chunk)
        st.success(f"Data added to vector database! Collection size: {count}")

# Question and Answer Area
st.header("Sustainability Reports Chatbot")
prompt = st.text_area("Ask a question related to corporate sustainability reports!")
ask = st.button("Ask")

if ask and prompt:
    # Main Status Container
    status_container = st.empty()
    
    # Detailed Status Section
    with st.expander("See processing status", expanded=True):
        status_placeholder = st.empty()
        
        def update_status(message):
            current_status = status_placeholder.text
            if current_status:
                status_placeholder.text(f"{current_status}\n{message}")
            else:
                status_placeholder.text(message)
    
    # Update main status and detailed status
    status_container.info("Processing your query...")
    update_status("Augmenting query...")
    queries_list = query_augmentation(prompt)
    update_status("Querying collection...")
    results_dict = query_collection(queries_list)
    update_status("Fusing results...")
    fused_results = reciprocal_rank_fusion(results_dict)
    update_status("Re-ranking documents...")
    documents = [doc for doc, _, _ in fused_results]
    relevant_text, relevant_ids = re_rank_cross_encoders(documents, prompt)
    update_status("Generating response...")
    response = call_llm(context=relevant_text, prompt=prompt)
    
    # Clear the processing status once complete
    status_container.empty()
    update_status("Processing complete!")

    st.write_stream(response)
    with st.expander("See retrieved documents"):
        st.write(documents)

    with st.expander("See most relevant document ids"):
        st.write(relevant_ids)
        st.write(relevant_text)