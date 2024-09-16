# application/rag/retriever.py
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain.schema import BaseRetriever, Document
from pydantic import Field
from typing import List, Any
import json

# Define a Custom Document Retrieval class (PostgresRetriever) that extends LangChain's BaseRetriever  
# Vector-based retrieval: This uses vector similarity search using the pgvector extension in PostgreSQL.

class PostgresRetriever(BaseRetriever):
    connection_string: str = Field(...)
    embedding_function: Any = Field(...)

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str) -> List[Document]:
        query_embedding = self.embedding_function.embed_query(query)

        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT question_id, question_full, answers, metadata,
                           question_vector <-> %s::vector AS document_distance,
                           answers_vector <-> %s::vector AS answers_distance,
                           question_vector::text as question_vector_text
                    FROM talk
                    ORDER BY question_vector <-> %s::vector
                    LIMIT 20
                """, (json.dumps(query_embedding), json.dumps(query_embedding), json.dumps(query_embedding)))
                results = cur.fetchall()

        all_answers = []
        for result in results:
            metadata = result['metadata']
            answers = result['answers']
            document_relevance = 1 - result['document_distance']
            answers_relevance = 1 - result['answers_distance']
            question_vector = json.loads(result['question_vector_text'])

            for answer in answers:
                answer_text = answer['answer']
                source = answer['source']

                # Assign trust score based on source
                if source == 'AskTheraRAGBuddy':
                    trust_score = 0.5
                elif source == 'Mental Health Dataset':
                    trust_score = 0.75
                else:
                    trust_score = 1.0

                # Combine document relevance, answer relevance, and trust score
                combined_score = (
                    document_relevance * 0.4 +  # Document relevance
                    answers_relevance * 0.4 +   # Answer relevance
                    trust_score * 0.2           # Trust score
                )

                all_answers.append({
                    'question_id': result['question_id'],
                    'question_full': result['question_full'],
                    'answer_text': answer_text,
                    'source': source,
                    'score': combined_score,
                    'metadata': metadata,
                    'question_vector': question_vector  # Add this line
                })

        # Sort answers and select top 10
        sorted_answers = sorted(all_answers, key=lambda x: x['score'], reverse=True)[:10]

        # Create Document objects for the top 10 answers
        documents = []
        for answer in sorted_answers:
            doc = Document(
                page_content=f"Question: {answer['question_full']}\nAnswer: {answer['answer_text']}",
                metadata={
                    'question_id': answer['question_id'],
                    'source': answer['source'],
                    'score': answer['score'],
                    'topic': answer['metadata'].get('topic', ''),
                    'question_title': answer['metadata'].get('question_title', ''),
                    'question_vector': answer['question_vector']  # Use this line
                }
            )
            documents.append(doc)
        return documents
        
    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)