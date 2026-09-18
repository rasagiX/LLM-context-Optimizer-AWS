"""
AI Context Compiler - FastAPI entrypoint.

Step 1 of the build plan: expose a health check and wire up the API router.
Step 2 onward (LLM connection, baseline runner, optimizer, judge) is added
incrementally in app/api and app/services.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

app = FastAPI(
    title="AI Context Compiler",
    description="Middleware that reduces LLM input tokens while maintaining answer quality.",
    version="0.1.0",
)

# Permissive CORS for local frontend development. Tighten before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health():
    """Basic liveness check."""
    return {"status": "ok", "service": "ai-context-compiler"}


app.include_router(api_router, prefix="/api/v1")
