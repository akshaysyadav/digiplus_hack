"""
Zepto Support Ticket Manager — Main Entry Point

FastAPI Application declaration and root API routing placeholder.
Implementation of specific route logic will be added by Developer 1 (Backend).
"""

from fastapi import FastAPI

app = FastAPI(
    title="Zepto Support Ticket Manager API",
    description="Agentic support ticket decision engine, precedent similarity search, and automated resolution system.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Zepto Support Ticket Manager API",
        "version": "0.1.0"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "CSV datasets ready",
        "engine": "TF-IDF similarity ready"
    }
