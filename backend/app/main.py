"""
AI Context Compiler - FastAPI entrypoint.

Step 1 of the build plan: expose a health check and wire up the API router.
Step 2 onward (LLM connection, baseline runner, optimizer, judge) is added
incrementally in app/api and app/services.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env file before anything else so AWS credentials and config are
# available when the service modules initialise.
load_dotenv()

from app.api.routes import router as api_router

app = FastAPI(
    title="AI Context Compiler",
    description="Middleware that reduces LLM input tokens while maintaining answer quality.",
    version="0.1.0",
)

# Read allowed origins from env so this can be locked down in production.
# Set CORS_ORIGINS to a comma-separated list of origins, e.g.
#   CORS_ORIGINS=https://myapp.example.com,https://staging.example.com
# Defaults to "*" only when the env var is absent (local dev convenience).
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
