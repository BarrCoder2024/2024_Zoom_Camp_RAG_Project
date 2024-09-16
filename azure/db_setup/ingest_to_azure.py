import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Function to connect to ADLS Gen2

def create_blob_service_client(connection_string):
    return BlobServiceClient.from_connection_string(connection_string)

# Function to upload files to the respective directories in Azure

def upload_file_to_adls(file_path, container_name, azure_directory, blob_service_client):
    blob_path = f"{azure_directory}/{os.path.basename(file_path)}"  # Preserving file name
    print(f"Uploading {file_path} to {blob_path}...")
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"Upload complete for {file_path} to {blob_path}")
    except Exception as e:
        print(f"Failed to upload {file_path} to {blob_path}: {e}")

# Function to iterate over the files and upload to corresponding directories

def upload_files_to_adls(local_directory, container_name, directory_mapping, blob_service_client):
    for local_subdirectory, azure_directory in directory_mapping.items():
        full_local_path = os.path.join(local_directory, local_subdirectory)
        if os.path.isdir(full_local_path):
            for file_name in os.listdir(full_local_path):
                file_path_on_local = os.path.join(full_local_path, file_name)
                if os.path.isfile(file_path_on_local):
                    upload_file_to_adls(file_path_on_local, container_name, azure_directory, blob_service_client)

# Function to run the upload process for a specific directory

def run_upload(local_directory, container_name, local_data_folder, adls_directory, blob_service_client):
    directory_mapping = {local_data_folder: adls_directory}
    upload_files_to_adls(local_directory, container_name, directory_mapping, blob_service_client)