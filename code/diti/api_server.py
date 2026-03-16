"""
Simple FastAPI server to connect frontend with backend
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import asyncio
import sys
from pathlib import Path
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from soham.orchestrator import BugHunterOrchestrator
from common.logger import get_logger

logger = get_logger("api_server")

app = FastAPI(title="Bug Hunter API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup"""
    global orchestrator
    logger.info("Starting Bug Hunter API server...")
    orchestrator = BugHunterOrchestrator()
    logger.info("API server ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global orchestrator
    if orchestrator:
        await orchestrator.cleanup()
    logger.info("API server shutdown complete")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Bug Hunter API is running"}


@app.post("/api/analyze")
async def analyze_code(file: UploadFile = File(...)):
    """
    Analyze a CSV file for bugs
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        Analysis results as JSON
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    logger.info(f"Received file for analysis: {file.filename}")
    
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        logger.info(f"File saved to: {temp_path}")
        
        # Run bug detection
        results = await orchestrator.run_bug_detection(temp_path)
        
        # Clean up temp file
        Path(temp_path).unlink()
        
        logger.info(f"Analysis complete. Found {len(results)} results")
        
        return {
            "status": "success",
            "results": results,
            "total": len(results),
            "bugs_found": sum(1 for r in results if r['Bug Line'] > 0)
        }
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/results/latest")
async def get_latest_results():
    """Get the latest analysis results"""
    # This would retrieve from database in production
    return {"message": "Not implemented yet"}


@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    if orchestrator and orchestrator.database:
        stats = orchestrator.database.get_statistics()
        return {"status": "success", "statistics": stats}
    return {"status": "error", "message": "Database not available"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
