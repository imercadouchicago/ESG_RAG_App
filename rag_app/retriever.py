import os
import requests
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import streamlit as st

OLLAMA_HOST = os.environ["OLLAMA_HOST"]

def get_vector_collection() -> chromadb.Collection:
    """Gets or creates a ChromaDB collection for vector storage.

    Creates an Ollama embedding function using the nomic-embed-text model and initializes
    a persistent ChromaDB client. Returns a collection that can be used to store and
    query document embeddings.

    Returns:
        chromadb.Collection: A ChromaDB collection configured with the Ollama embedding
            function and cosine similarity space.
    """
    
    try:
        # Test basic connectivity first
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": "test"}
        )
        if not response.ok:
            raise ValueError(f"Ollama API error: {response.status_code} - {response.text}")
    except Exception as e:
        raise ValueError(f"Connection to Ollama failed: {e}")
    
    # Set nomic-embed-text from ollama as embedding model
    # 768 dimensions and context window of 8192
    ollama_ef = OllamaEmbeddingFunction(
        url = f"{OLLAMA_HOST}/api/embeddings",
        model_name="nomic-embed-text:latest",
    )

    try:
        ollama_ef(["Embedding function test"])
    except Exception as e:
        raise ValueError(f"Issue with embedding function: {e}")

    # Initialize ChromaDB client in specified path
    chroma_client = chromadb.PersistentClient(path = "./chromadb")

    # Creating a collection in the database
    # Compares vectors in database based on cosine similarity
    return chroma_client.get_or_create_collection(
        name="document_collection" ,
        embedding_function=ollama_ef,
        metadata={"hnsw:space": "cosine"},
    )

def add_to_vector_collection(indexed_chunks_list: list[dict]):
    """Adds document splits from multiple files to a vector collection.

    Args:
        indexed_chunks_list: A list of dictionaries, each containing 'id' (file ID)
                             and 'text' (list of Document objects/chunks for that file).
    Returns:
        int: Number of documents in collection after addition.
    """
    collection = get_vector_collection()
    documents, metadatas, ids = [], [], []

    # Calculate total number of chunks for progress bar
    total_chunks = sum(len(item['text']) for item in indexed_chunks_list)
    if total_chunks == 0:
        st.warning("No text chunks found to add to the collection.")
        return collection.count()

    progress_bar = st.progress(0, text=f"Preparing {total_chunks} text chunks for embedding...")
    chunks_processed = 0

    try:
        for indexed_chunks in indexed_chunks_list:
            file_name = indexed_chunks['id']
            for idx, chunk in enumerate(indexed_chunks['text']):
                documents.append(chunk.page_content)
                metadatas.append(chunk.metadata)
                # Using file_name and chunk index for ID
                ids.append(f"{file_name}_{idx+1}")
                chunks_processed += 1
                if chunks_processed < 5:
                    st.write(f"Document: {chunk.page_content}, ID: {ids[-1]}")
                progress_percentage = chunks_processed / total_chunks
                progress_bar.progress(progress_percentage, text=f"Preparing chunk {chunks_processed}/{total_chunks}...")
    except Exception as e:
        st.error(f"Error preparing chunks for embedding: {e}")
        return collection.count() # Return current count if preparation fails

    # Ensure progress bar is at 100% before upserting
    progress_bar.progress(1.0, text=f"Prepared {total_chunks} chunks. Upserting into collection...")
    try:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        progress_bar.empty()
        st.success(f"Successfully added {len(ids)} chunks to the vector collection.")
    except Exception as e:
        st.error(f"Error upserting documents into ChromaDB: {e}")
        progress_bar.empty() # Clear progress bar even on error
    return collection.count()

def query_collection(prompts: str | list[str], n_results: int = 10):
    """Queries the vector collection with one or more prompts to retrieve relevant documents.

    Args:
        prompts: Single query string or list of query strings
        n_results: Maximum number of results to return per query. Defaults to 10.

    Returns:
        dict: Query results containing documents, distances and metadata from the collection.

    Raises:
        ChromaDBError: If there are issues querying the collection.
    """
    collection = get_vector_collection()
    query_texts = [prompts] if isinstance(prompts, str) else prompts
    results = collection.query(query_texts=query_texts, n_results=n_results)
    return results

def check_collection_stats():
    """Checks the number of documents in the collection and extracts 3 examples.

    Returns:
        tuple: (count of documents, list of 3 example documents) or (count, None) if error.
    """
    try:
        collection = get_vector_collection()
        collection_count = collection.count()

        # Extract up to 3 examples if the collection is not empty
        if collection_count > 0:
            results = collection.get(
                limit=min(3, collection_count),
                include=["documents", "metadatas"]
            )

            examples = []
            if results and results.get("documents"):
                for i in range(len(results["documents"])):
                    doc_text = results["documents"][i]
                    doc_id = results["ids"][i] if results.get("ids") else f"Document {i+1}"
                    metadata = results["metadatas"][i] if results.get("metadatas") else {}

                    examples.append({
                        "id": doc_id,
                        "text": doc_text[:150] + "..." if len(doc_text) > 150 else doc_text,  # Show first 150 chars
                        "metadata": metadata
                    })
                return collection_count, examples
            else:
                # Handle case where get() returns empty or unexpected results
                st.warning("Could not retrieve example documents from the collection.")
                return collection_count, []
        else:
            # Collection is empty
            return collection_count, []
    except Exception as e:
        st.error(f"Error checking collection stats: {e}")
        return 0, None