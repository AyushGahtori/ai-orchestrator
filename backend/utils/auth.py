from fastapi import Header, HTTPException
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

# Simple API key system. Uses env var 'DEMO_API_KEY'.
DEMO_KEY = os.getenv('DEMO_API_KEY', 'demo_key')


def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key is None or x_api_key != DEMO_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return True
