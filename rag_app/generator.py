import ollama

system_prompt = """
You are an AI assistant tasked with providing detailed answers based solely on the given context. Your goal is to analyze the information provided and formulate a comprehensive, well-structured response to the question.

context will be passed as "Context:"
user question will be passed as "Question:"

To answer the question:
1. Thoroughly analyze the context, identifying key information relevant to the question.
2. Organize your thoughts and plan your response to ensure a logical flow of information.
3. Formulate a detailed answer that directly addresses the question, using only the information provided in the context.
4. Ensure your answer is comprehensive, covering all relevant aspects found in the context.
5. If the context doesn't contain sufficient information to fully answer the question, state this clearly in your response.

Format your response as follows:
1. Use clear, concise language to the question without referring to the fact that context was provided.
2. Organize your answer into paragraphs for readability.
3. Use bullet points or numbered lists where appropriate to break down complex information.
4. If relevant, include any headings or subheadings to structure your response.
5. Ensure proper grammar, punctuation, and spelling throughout your answer.
6. If the context is not relevant to the question, say "I'm sorry, I don't have information about that topic."

Important: Base your entire response solely on the information provided in the context. Do not include any external knowledge or assumptions not present in the given text.
"""

def call_llm(context: str, prompt: str, system_prompt: str = system_prompt):
    """Calls the language model with context and prompt to generate a response.

    Uses Ollama to stream responses from a language model by providing context and a
    question prompt. The model uses a system prompt to format and ground its responses appropriately.

    Args:
        context: String containing the relevant context for answering the question
        prompt: String containing the user's question

    Yields:
        String chunks of the generated response as they become available from the model

    Raises:
        OllamaError: If there are issues communicating with the Ollama API
    """
    response = ollama.chat(
        model="llama3.2:3b",
        stream=True,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"Context: {context}, Question: {prompt}",
            },
        ],
    )
    for chunk in response:
        if chunk["done"] is False:
            yield chunk["message"]["content"]
        else:
            break