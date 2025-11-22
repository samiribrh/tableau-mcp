"""
Tableau AI Assistant - Main Application
FastAPI server with Ollama integration for AI-powered Tableau operations.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from src.config import setup_logging, settings, get_logger
from src.api import router

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tableau AI Assistant",
    description="AI-powered assistant for Tableau Server operations using local LLM",
    version="1.0.0"
)

# Mount static files (for HTML/CSS/JS)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Include API routes
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the chat interface."""
    index_path = static_dir / "index.html"
    
    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Tableau AI Assistant</h1><p>index.html not found</p>",
            status_code=404
        )
    
    with open(index_path, "r") as f:
        return HTMLResponse(content=f.read())


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("="*60)
    logger.info("🚀 Tableau AI Assistant Starting...")
    logger.info("="*60)
    logger.info(f"Server: {settings.server_host}:{settings.server_port}")
    logger.info(f"Tableau Server: {settings.tableau_server}")
    logger.info(f"Ollama Model: {settings.ollama_model}")
    logger.info(f"Default Project: {settings.tableau_project_name}")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Tableau AI Assistant shutting down...")


if __name__ == "__main__":
    logger.info("Starting Tableau AI Assistant server...")
    
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,  # Auto-reload on code changes
        log_level=settings.log_level.lower()
    )
