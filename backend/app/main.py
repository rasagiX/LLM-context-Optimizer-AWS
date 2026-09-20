"""
AI Context Compiler - FastAPI entrypoint.
"""

import os
from dotenv import load_dotenv

# Load .env file before anything else so AWS credentials and config are available
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

app = FastAPI(
    title="AI Context Compiler",
    description="Middleware that reduces LLM input tokens while maintaining answer quality.",
    version="0.1.0",
)

# Read allowed origins from env so this can be locked down in production.
_raw_origins = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health():
    """Basic liveness check."""
    return {"status": "ok", "service": "ai-context-compiler"}


app.include_router(api_router, prefix="/api/v1")
