
from sentence_transformers import CrossEncoder

def re_rank_cross_encoders(documents: list[str], prompt) -> tuple[str, list[int]]:
    """Re-ranks documents using a cross-encoder model for more accurate relevance scoring.

    Uses the MS MARCO MiniLM cross-encoder model to re-rank the input documents based on
    their relevance to the query prompt. Returns the concatenated text of the top 3 most
    relevant documents along with their indices.

    Args:
        documents: List of document strings to be re-ranked.

    Returns:
        tuple: A tuple containing:
            - relevant_text (str): Concatenated text from the top 3 ranked documents
            - relevant_text_ids (list[int]): List of indices for the top ranked documents

    Raises:
        ValueError: If documents list is empty
        RuntimeError: If cross-encoder model fails to load or rank documents
    """
    relevant_text = ""
    relevant_text_ids = []

    encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    ranks = encoder_model.rank(prompt, documents, top_k=3)
    for rank in ranks:
        relevant_text += documents[rank["corpus_id"]]
        relevant_text_ids.append(rank["corpus_id"])

    return relevant_text, relevant_text_ids