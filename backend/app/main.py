"""
Zepto Support Ticket Manager — Main Entry Point

FastAPI application declaration with CORS middleware and API routes.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ALLOWED_ORIGINS, HOST, PORT
from app.api.routes import api_router

app = FastAPI(
    title="Zepto Support Ticket Manager API",
    description="Agentic support ticket decision engine, precedent similarity search, and automated resolution system.",
    version="1.0.0"
)

# CORS Configuration for React Frontend & Local/Prod origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Zepto Support Ticket Manager API",
        "version": "1.0.0"
    }

# Health Check Endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "datasets": "3 CSV files loaded and cached",
        "similarity_engine": "TF-IDF + Cosine Similarity ready",
        "decision_engine": "Deterministic guardrails active"
    }

# Mount all API routes under /api
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
