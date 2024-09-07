from ingest_to_azure import create_blob_service_client, run_upload
from dotenv import load_dotenv
import os

def main():
    # Load environment variables from .env file
    load_dotenv()

    local_directory = os.getenv('DATASET_PATH')  # Main dataset directory
    connection_string = os.getenv('AZURE_CONNECTION_STRING')
    container_name = os.getenv('ADLS_CONTAINER_NAME')

    # Create the BlobServiceClient
    blob_service_client = create_blob_service_client(connection_string)

    # Upload counsel_chat_data
    run_upload(local_directory, container_name, 'counsel_chat_data', 'counsel_chat_data', blob_service_client)

    # Upload mentalhealth_data
    run_upload(local_directory, container_name, 'mentalhealth_data', 'mentalhealth_data', blob_service_client)

# Python entry point
if __name__ == "__main__":
    main()