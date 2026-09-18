"""
AI Context Compiler - FastAPI entrypoint.

Step 1 of the build plan: expose a health check and wire up the API router.
Step 2 onward (LLM connection, baseline runner, optimizer, judge) is added
incrementally in app/api and app/services.
"""

# Load .env FIRST — before any module that calls os.getenv() is imported.
# Without this, AWS_REGION, AWS_ACCESS_KEY_ID, BEDROCK_MODEL_ID, and
# EMBEDDER_BACKEND are all silently empty when the server starts.
from dotenv import load_dotenv
load_dotenv()  # reads backend/.env (or .env in cwd) into os.environ

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
