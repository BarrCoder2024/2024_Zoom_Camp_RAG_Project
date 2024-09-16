import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get PostgreSQL connection details from environment variables
username = os.getenv('PG_ADMIN_USERNAME')
password = os.getenv('PG_ADMIN_PASSWORD')
host = os.getenv('PG_SERVER_NAME')
port = os.getenv('POSTGRES_PORT')
database = os.getenv('PG_DATABASE')

# The PostgreSQL connection string 
POSTGRESQL_CONNECTION = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create a vector index to allow for faster similarity searches.

def create_vector_index():
    try:
        # Connect to the database
        with psycopg2.connect(POSTGRESQL_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Create the index
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS talk_question_vector_idx 
                    ON talk USING ivfflat (question_vector vector_cosine_ops)
                    WITH (lists = 100);
                """)
                
                # Commit the transaction
                conn.commit()
                
        print("Vector index created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the index: {e}")

# Run the function to create the index
if __name__ == "__main__":
    create_vector_index()