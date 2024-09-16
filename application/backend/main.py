# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import uuid
import uvicorn
from openai import OpenAI, AuthenticationError, APIConnectionError, RateLimitError, BadRequestError
from rag.rag_execution import run_rag

# Load environment variables from .env file
load_dotenv()

# Initialise Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

try:
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        decode_responses=True,
        socket_timeout=30,
        socket_connect_timeout=30,
        retry_on_timeout=True,
        max_connections=10
    )
    redis_client.ping()  # Test connection
    print("Redis connection successful")
except redis.ConnectionError as e:
    redis_client = None
    print(f"Redis connection failed: {e}")

# Helper function to get the OpenAI client with a specific API key
def get_openai_client(api_key: str):
    return OpenAI(api_key=api_key)

# Helper functions for storing and retrieving API keys from Redis
def store_api_key(session_id: str, api_key: str):
    if redis_client:
        redis_client.set(session_id + "_api_key", api_key)

def get_api_key(session_id: str):
    return redis_client.get(session_id + "_api_key") if redis_client else None

# Create FastAPI app instance
app = FastAPI()

# Initialise OpenAI client with API key from environment variables
client = get_openai_client(os.getenv("OPENAI_API_KEY"))

# Models for request validation
class QuestionRequest(BaseModel):
    question: str

class ApiKeyRequest(BaseModel):
    api_key: str

# Helper functions for session management
def get_session_id(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id)
    return session_id

# Function to validate the OpenAI API key for >=1.0.0
def validate_openai_api_key(api_key: str) -> bool:
    try:
        temp_client = get_openai_client(api_key)
        temp_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=5
        )
        return True
    except AuthenticationError:
        return False
    except APIConnectionError:
        raise HTTPException(status_code=500, detail="Network error while connecting to OpenAI.")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request to OpenAI: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://asktheraragbuddy-e7eagmgje3gcf3db.uksouth-01.azurewebsites.net",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type"]
)

# FastAPI Endpoints
@app.post("/ask")
async def ask_question(request: Request, question_request: QuestionRequest, response: Response):
    session_id = get_session_id(request, response)
    api_key = get_api_key(session_id)

    if api_key:
        client = get_openai_client(api_key)
    else:
        client = get_openai_client(os.getenv("OPENAI_API_KEY"))

    try:
        response_text = run_rag(question_request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

    return {"answer": response_text}

@app.post("/submit-api-key")
async def submit_api_key(request: Request, api_key_request: ApiKeyRequest, response: Response):
    session_id = get_session_id(request, response)

    if not validate_openai_api_key(api_key_request.api_key):
        raise HTTPException(status_code=400, detail="Invalid OpenAI API key.")

    store_api_key(session_id, api_key_request.api_key)

    return {"message": "API key accepted."}

# Python entry point
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
