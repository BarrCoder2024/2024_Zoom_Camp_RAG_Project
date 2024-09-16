# application/rag/chain.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from rag import PostgresRetriever

# Load environment variables from .env
load_dotenv()

# Set up LLM and embeddings
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key) #Instantiating a Language Model 
#llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5, openai_api_key=openai_api_key)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Get PostgreSQL connection string and collection name from environment variables

# Get PostgreSQL connection details from environment variables
username = os.getenv('PG_ADMIN_USERNAME')         # Get the server admin login name stored in .env file
password = os.getenv('PG_ADMIN_PASSWORD')         # Get the server password stored in .env file
host = os.getenv('PG_SERVER_NAME')                # Get the server name stored in .env file
port = os.getenv('POSTGRES_PORT')                 # Get the Standard PostgreSQL port stored in .env file
database = os.getenv('PG_DATABASE')               # Get the database name stored in .env file
collection_name = os.getenv('PG_COLLECTION_NAME') # Get the PostgreSQL table name from which documents are retrieved stored in .env file

# The PostgreSQL connection string 
POSTGRESQL_CONNECTION = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create an instance of the PostgresRetriever class
postgres_retriever = PostgresRetriever(
    connection_string=POSTGRESQL_CONNECTION, # PostgreSQL connection string
    collection_name=collection_name,  # Name of the collection storing documents
    embedding_function=embeddings # Embedding function to generate query vectors
)

CUSTOM_PROMPT = PromptTemplate(
    input_variables=["context", "input"],
    template="""
You are an AI assistant tasked with summarizing insights from mental health professionals about mental health related topics and issues.

## Provide an initial response that directly addresses the user's question or concern.
Use insights from the retrieved expert opinions to inform this response.

## After your initial response, provide a comprehensive summary, based only on the retrieved information, that:

## Based on what experts have said on topics relating to [summarized topic]
- [Provide a brief overview of the topic, including its definition and primary characteristics using only the retrieved documents]
- [List key aspects or identifiable features, if applicable. Only include information that is present in the retrieved documents]

## Key points regarding [summarized topic]
- Nature of the concept/issue: [Summarize the fundamental nature]
- Key aspects: [List main aspects or components]
- Related factors: [Summarize related factors or influences, if mentioned]
- Importance/Impact: [Outline the significance or effects]
- Professional perspectives: [Summarize expert views or approaches]

## Consensus among experts
- [Highlight any points of agreement among the experts]

## Specific insights or recommendations mentioned
- [List specific insights, advice, or recommendations given by experts, using bullet points]

Only include information that is present in the retrieved documents. Do not add any information from your own knowledge. 
If any section is not applicable based on the retrieved information, omit it from the summary. Ensure that bullet points are used consistently throughout the response.


Retrieved information:
{context}

User's question: {input}

Your summarized response:
"""
)

# Create the chain that processes retrieved documents & generates a response using the llm and CUSTOM_PROMPT
document_chain = create_stuff_documents_chain(llm, CUSTOM_PROMPT)

# Create a RAG chain that retrieves documents & generates a response using document_chain
rag_chain = create_retrieval_chain(postgres_retriever, document_chain)
