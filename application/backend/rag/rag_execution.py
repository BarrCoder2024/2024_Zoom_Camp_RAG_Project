# application/rag/rag_execution.py
from rag import postgres_retriever, rag_chain  
from rag import PostgresRetriever  
from rag import is_special_topic, get_single_response, post_process_rag_output   

# This is the main function to execute the RAG pipeline.
# It first checks if the user's query matches a special topic, such as a greeting or farewell.
# If the query matches a special topic, a random answer is selected from the documents
# retrieved by the Postgres retriever, and the response is returned without post-processing.
# If the query does not match a special topic, the standard RAG pipeline is used to generate a response.
# In this case, the response is post-processed before being returned to the user.

def run_rag(query):
    topic = is_special_topic(query)
    
    # If it's a greeting or farewell, retrieve documents from the postgres retriever
    if topic:
        documents = postgres_retriever.invoke(query)
        response = get_single_response(documents, topic)
        
        if response:
            return response
    
    # Fallback to the standard RAG response generation if no special topic found
    response = rag_chain.invoke({"input": query})
    formatted_response = post_process_rag_output(response)
    return formatted_response