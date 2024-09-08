import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()

# Get PostgreSQL connection details from environment variables
username = os.getenv('PG_ADMIN_USERNAME')  # Get the server admin login name stored in .env file
password = os.getenv('PG_ADMIN_PASSWORD')  # Get the server password stored in .env file
host = os.getenv('PG_SERVER_NAME')         # Get the server name stored in .env file
port = os.getenv('POSTGRES_PORT')          # Get the Standard PostgreSQL port stored in .env file
database = os.getenv('PG_DATABASE')        # Get the database name stored in .env file

# Check if environment variables are properly loaded
if not all([username, password, host, port, database]):
    print("Error: Missing one or more environment variables. Please check your .env file.")
    exit(1)

# The PostgreSQL connection string
POSTGRESQL_CONNECTION = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Connect to the PostgreSQL database
def connect_to_db():
    try:
        connection = psycopg2.connect(POSTGRESQL_CONNECTION)
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit(1)

# Define the table creation function 
def table_creation():
    conn = connect_to_db()
    cursor = conn.cursor()

    # SQL query to create the table with metadata field containing topic, question_title, and source
    create_table_query = """
        -- Enable the pgvector extension if not already enabled
        CREATE EXTENSION IF NOT EXISTS vector;

        -- Create the table with vector and metadata fields
        CREATE TABLE IF NOT EXISTS talk (
            question_id VARCHAR(50) PRIMARY KEY,
            question_full TEXT,
            answers JSONB,
            vector VECTOR(1536),  -- Using text-embedding-ada-002 (OpenAI) which produces 1536-dimension vectors
            metadata JSONB  -- This will contain topic, question_title, and source
        );
    """

    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("Table created successfully!")
    except Exception as e:
        print(f"Error occurred while creating the table: {e}")
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()