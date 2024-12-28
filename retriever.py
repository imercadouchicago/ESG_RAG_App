
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

def get_vector_collection() -> chromadb.Collection:
    """Gets or creates a ChromaDB collection for vector storage.

    Creates an Ollama embedding function using the nomic-embed-text model and initializes
    a persistent ChromaDB client. Returns a collection that can be used to store and
    query document embeddings.

    Returns:
        chromadb.Collection: A ChromaDB collection configured with the Ollama embedding
            function and cosine similarity space.
    """
    # Set nomic-embed-text from ollama as embedding model
    # 768 dimensions and context window of 8192
    ollama_ef = OllamaEmbeddingFunction(
        url = "http://ollama:11434/api/embeddings",
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

def add_to_vector_collection(indexed_chunks: list[dict]):
    """Adds document splits to a vector collection for semantic search.

    Takes a list of document splits and adds them to a ChromaDB vector collection
    along with their metadata and unique IDs based on the filename.

    Args:
        all_splits: List of Document objects containing text chunks and metadata

    Returns:
        None. Displays a success message via Streamlit when complete.

    Raises:
        ChromaDBError: If there are issues upserting documents to the collection
    """
    collection = get_vector_collection()
    documents, metadatas, ids = [], [], []

    try:
        for file_name, chunks in indexed_chunks:
            for idx, chunk in enumerate(chunks):
                documents.append(chunk.page_content)
                metadatas.append(chunk.metadata)
                ids.append(f"{file_name}_{idx+1}")
    except:
        raise ValueError("Error vectorizing document chunks")

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    return collection.count()

def query_collection(prompt: str, n_results: int = 10):
    """Queries the vector collection with a given prompt to retrieve relevant documents.

    Args:
        prompt: The search query text to find relevant documents.
        n_results: Maximum number of results to return. Defaults to 10.

    Returns:
        dict: Query results containing documents, distances and metadata from the collection.

    Raises:
        ChromaDBError: If there are issues querying the collection.
    """
    collection = get_vector_collection()
    results = collection.query(query_texts=[prompt], n_results=n_results)
    return results