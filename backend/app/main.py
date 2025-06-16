from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.endpoints import router as api_router
from .db.database import engine, SessionLocal
from .db import models
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Activity Tracker",
    description="A system that uses LLM to process and analyze employee activity data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include API router with prefix
app.include_router(api_router, prefix="/api/v1", dependencies=[Depends(get_db)])

# Include API router without prefix for backward compatibility
app.include_router(api_router, dependencies=[Depends(get_db)])

@app.get("/")
async def root():
    """Serve the frontend application"""
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {
        "message": "Welcome to Employee Activity Tracker API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "frontend": "Frontend files not found"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 