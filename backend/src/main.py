"""
FastAPI application entry point.
This implements the basic FastAPI application to satisfy contract tests (Task 1.4).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.api.v1.api import router as api_v1_router
from src.core.logging import logger

app = FastAPI(
    title="Prompt Center API",
    description="API for prompt management system",
    version="0.1.0"
)

# CORS middleware - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Prompt Center API"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Prompt Center API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
