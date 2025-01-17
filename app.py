import os
import streamlit as st

from rag_app.preprocessing import process_uploaded_document
from rag_app.retriever import add_to_vector_collection, query_collection
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
    results = query_collection(prompt)
    context = results.get("documents")[0]
    relevant_text, relevant_text_ids = re_rank_cross_encoders(context, prompt)
    response = call_llm(context=relevant_text, prompt=prompt)

    st.write_stream(response)
    with st.expander("See retrieved documents"):
        st.write(results)

    with st.expander("See most relevant document ids"):
        st.write(relevant_text_ids)
        st.write(relevant_text)