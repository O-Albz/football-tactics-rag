from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    valid_key = os.getenv("RAG_API_KEY")
    if not valid_key:
        raise HTTPException(status_code=500, detail="API key not configured on server")
    if api_key != valid_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key