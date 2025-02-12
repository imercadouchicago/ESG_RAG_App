from rag_app.generator import call_llm
from collections import defaultdict

def query_augmentation(prompt: str):
    """
    Augments the user's query using a language model.

    This function takes a user's query and uses a language model to generate a list of
    queries that are similar to the original query.

    Args:
        prompt (str): The user's query to be augmented

    Returns:
        list: A list of augmented queries
    """
    system_prompt = """
    You are an AI language model assistant. Your task is to generate 5 different 
    versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Context will be passed as "Context:"
    Question will be passed as "Question:"
    I will be using queries = response.split("\n") to parse your response. 
    Please format your response as a list of queries in the following format: 
    "<query 1>\n<query 2>\n<query 3>\n<query 4>\n<query 5>"
    """
    # Collect all chunks into a single string
    full_response = ""
    for chunk in call_llm(system_prompt, prompt):
        full_response += chunk
    
    # Split the complete response into queries
    queries = [q.strip() for q in full_response.split('\n') if q.strip()]
    return queries

def reciprocal_rank_fusion(
    results: dict,
    k: float = 60.0
) -> list[tuple[str, float, dict]]:
    """
    Implements reciprocal rank fusion to combine multiple ranked lists into a single ranking.
    
    Args:
        results: Query results from ChromaDB
        k: Constant that helps prevent rankings from being swamped by high rankings
    
    Returns:
        List of tuples containing (document, fused_score, metadata) sorted by fused_score desc
    """
    fusion_scores = defaultdict(float)
    doc_metadata: dict[str, dict] = {}
    
    for query_idx, (docs, dists, metas) in enumerate(zip(
        results['documents'], 
        results['distances'], 
        results['metadatas']
    )):
        # Create ranked list based on distances
        ranked_items = sorted(enumerate(zip(docs, dists, metas)), key=lambda x: x[1][1])
        
        # Calculate fusion scores
        for rank, (_, (doc, _, meta)) in enumerate(ranked_items, start=1):
            fusion_scores[doc] += 1.0 / (k + rank)
            doc_metadata[doc] = meta
    
    # Create and sort final results
    return sorted(
        [(doc, score, doc_metadata[doc]) for doc, score in fusion_scores.items()],
        key=lambda x: x[1],
        reverse=True
    )

