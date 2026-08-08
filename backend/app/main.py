"""
Zepto Support Ticket Manager — Main Entry Point

FastAPI application declaration with CORS middleware and API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router

app = FastAPI(
    title="Zepto Support Ticket Manager API",
    description="Agentic support ticket decision engine, precedent similarity search, and automated resolution system.",
    version="1.0.0"
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local hackathon development & deployment
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
