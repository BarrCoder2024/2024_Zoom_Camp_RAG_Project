import os
from dotenv import load_dotenv
import json
import psycopg2
from psycopg2.extras import Json, execute_batch
from azure.storage.blob import BlobServiceClient
from langchain_openai import OpenAIEmbeddings
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Azure Blob Storage setup
azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")
container_name = os.getenv("ADLS_CONTAINER_NAME")
blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
container_client = blob_service_client.get_container_client(container_name)

# PostgreSQL connection string
POSTGRESQL_CONNECTION = f"postgresql://{os.getenv('PG_ADMIN_USERNAME')}:{os.getenv('PG_ADMIN_PASSWORD')}@{os.getenv('PG_SERVER_NAME')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('PG_DATABASE')}"

# OpenAI Embeddings setup
openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-ada-002")

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(POSTGRESQL_CONNECTION)

def list_blobs_in_directory(directory_name):
    """List all blobs in a specified Azure Blob Storage directory."""
    return [blob.name for blob in container_client.list_blobs(name_starts_with=directory_name) if '.' in blob.name]

def download_blob_to_string(blob_name):
    """Download a blob's content as a string."""
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client.download_blob().readall().decode("utf-8")

# Global variable to track API calls
api_call_count = 0

def process_questions_batch(questions_data: List[Dict[Any, Any]], batch_size: int = 100):
    """Process a batch of questions, generate embeddings, and prepare data for insertion."""
    global api_call_count
    start_time = time.time()

    # Extract all texts (questions and answers) for embedding
    all_texts = []
    for question_data in questions_data:
        all_texts.append(question_data['question_full'])
        for answer_data in question_data['answers']:
            all_texts.append(answer_data['answer'])

    # Process embeddings in batches
    all_embeddings = []
    for i in range(0, len(all_texts), batch_size):
        batch = all_texts[i:i+batch_size]
        embed_start = time.time()
        batch_embeddings = embedding_model.embed_documents(batch)
        embed_end = time.time()
        print(f"Batch embedding time: {embed_end - embed_start:.2f} seconds")
        all_embeddings.extend(batch_embeddings)
        api_call_count += 1

    # Prepare results for database insertion
    results = []
    embedding_index = 0
    for question_data in questions_data:
        question_id = question_data['question_id']
        topic = question_data['topic']
        question_title = question_data['question_title']
        question_full = question_data['question_full']
        answers = question_data['answers']

        question_embedding = all_embeddings[embedding_index]
        embedding_index += 1

        answer_embeddings = []
        answer_sources = []
        for answer_data in answers:
            answer_source = answer_data['source']
            answer_embedding = all_embeddings[embedding_index]
            embedding_index += 1
            answer_embeddings.append(answer_embedding)
            answer_sources.append(answer_source)

        # Calculate combined answer embedding
        combined_answer_embedding = [sum(x) / len(x) for x in zip(*answer_embeddings)]

        metadata = {
            "topic": topic,
            "question_title": question_title,
            "sources": answer_sources
        }

        results.append((question_id, question_full, Json(answers), question_embedding, combined_answer_embedding, Json(metadata)))

    end_time = time.time()
    print(f"Total batch processing time: {end_time - start_time:.2f} seconds")
    print(f"API calls made: {api_call_count}")

    return results

def process_blob(blob_name):
    """Process a single blob: download, parse JSON, and process questions."""
    blob_content = download_blob_to_string(blob_name)
    json_data = json.loads(blob_content)
    return process_questions_batch(json_data)

def insert_batch(conn, data_batch):
    """Insert a batch of processed data into the database."""
    with conn.cursor() as cur:
        execute_batch(cur, """
            INSERT INTO talk (question_id, question_full, answers, question_vector, answers_vector, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (question_id) DO NOTHING;
        """, data_batch)
    conn.commit()

def load_data():
    """Main function to load data from Azure Blob Storage, process it, and insert into the database."""
    directories = ["counsel_chat_data/", "mentalhealth_data/"]
    all_blobs = []
    for directory in directories:
        all_blobs.extend(list_blobs_in_directory(directory))

    processed_data = []
    # Process blobs concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_blob = {executor.submit(process_blob, blob_name): blob_name for blob_name in all_blobs}
        for future in tqdm(as_completed(future_to_blob), total=len(all_blobs), desc="Processing blobs"):
            blob_name = future_to_blob[future]
            try:
                processed_data.extend(future.result())
            except Exception as exc:
                print(f'{blob_name} generated an exception: {exc}')

    # Insert processed data into the database
    conn = connect_to_db()
    try:
        batch_size = 100
        for i in tqdm(range(0, len(processed_data), batch_size), desc="Inserting batches"):
            batch = processed_data[i:i+batch_size]
            insert_batch(conn, batch)
    finally:
        conn.close()

    return len(processed_data)