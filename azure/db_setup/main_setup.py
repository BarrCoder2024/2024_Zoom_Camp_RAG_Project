import os
from dotenv import load_dotenv
from ingest_to_azure import create_blob_service_client, run_upload  # Import the functions from ingest_to_azure.py
from setup_db_table import table_creation  # Import the table creation function from setup_db_table.py
from data_loader import load_data  # Import the load_data function
from create_vector_index import create_vector_index # Import the create_vector_index function

def main():
    # Load environment variables from .env file
    load_dotenv()

    local_directory = os.getenv('DATASET_PATH')  # Main dataset directory
    connection_string = os.getenv('AZURE_CONNECTION_STRING')
    container_name = os.getenv('ADLS_CONTAINER_NAME')

    # Create the BlobServiceClient
    blob_service_client = create_blob_service_client(connection_string)
    
    # Upload datasets
    run_upload(local_directory, container_name, 'counsel_chat_data', 'counsel_chat_data', blob_service_client) # Upload counsel_chat_data 
    run_upload(local_directory, container_name, 'mentalhealth_data', 'mentalhealth_data', blob_service_client) # Upload mentalhealth_data

    # Call the table creation function to create the database table
    table_creation()

    # Load data into the database
    items_processed = load_data()
    print(f"Processed and inserted {items_processed} items into the database.")

    # Create the vector index
    create_vector_index()

# Python entry point
if __name__ == "__main__":
    main()

