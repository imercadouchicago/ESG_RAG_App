import os
import requests
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

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
    # Test basic connectivity first
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": "test"}
        )
        print(f"Raw API response: {response.text}")
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

    # Vector database client with client in specified path
    # Default database is SQLite
    chroma_client = chromadb.PersistentClient(path = "./chromadb")

    # Creating a collection (~table) called rag_app in the database
    # Compares vectors in database based on cosine similarity
    return chroma_client.get_or_create_collection(
        name="document_collection" ,
        embedding_function=ollama_ef,
        metadata={"hnsw:space": "cosine"},
    )

def add_to_vector_collection(indexed_chunks: dict):
    """Adds document splits to a vector collection for semantic search.
    Args:
        indexed_chunks: Dictionary containing file ID and list of Document objects
    Returns:
        int: Number of documents in collection after addition
    """
    collection = get_vector_collection()
    documents, metadatas, ids = [], [], []
    
    try:
        file_name = indexed_chunks['id']
        for idx, chunk in enumerate(indexed_chunks['text']):
            documents.append(chunk.page_content)
            metadatas.append(chunk.metadata)
            ids.append(f"{file_name}_{idx+1}")
            
    except Exception as e:
        raise e
        
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    
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