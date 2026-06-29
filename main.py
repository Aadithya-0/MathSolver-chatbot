"""
FastAPI Backend for Math Solver Chatbot
Handles API endpoints for image processing and math problem solving
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

# Import AI engine
from ai_engine import get_solver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Math Solver API",
    description="API for solving math problems from images using AI",
    version="1.0.0"
)

# Configure CORS for Gradio frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads folder if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize AI solver
try:
    solver = get_solver()
    logger.info("Math Solver Engine initialized successfully")
except ValueError as e:
    logger.warning(f"Math Solver Engine initialization: {e}")
    solver = None


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "running",
        "service": "Math Solver API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/solve")
async def solve(
    image: UploadFile = File(...),
    variables: Optional[str] = Form(default="{}"),
    step_by_step: Optional[bool] = Form(default=True)
) -> Dict[str, Any]:
    """
    Solve a math problem from an uploaded image
    
    Args:
        image: Image file containing the math problem
        variables: JSON string of variables to consider
        step_by_step: Whether to provide step-by-step solution
        
    Returns:
        Solution details including steps, explanation, and confidence
    """
    file_path = None
    try:
        # Validate image file
        if not image.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
        safe_filename = f"{timestamp}{image.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Validate file size (max 10MB)
        contents = await image.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Image uploaded: {safe_filename}")
        
        # Validate solver is initialized
        if solver is None:
            raise HTTPException(
                status_code=503, 
                detail="AI Solver not initialized. Check OpenAI API key."
            )
        
        # Process image with AI engine
        logger.info(f"Processing image: {safe_filename} with variables: {variables}")
        result = solver.solve_math_problem(
            str(file_path),
            variables=variables,
            solve_step_by_step=step_by_step
        )
        
        # Handle errors from solver
        if "error" in result and result["error"]:
            logger.error(f"Solver error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Return successful response
        response = {
            "status": "success",
            "filename": safe_filename,
            **result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully processed: {safe_filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Cleanup: optionally delete the uploaded file after processing
        # Uncomment if you want to save storage space
        # if file_path and file_path.exists():
        #     file_path.unlink()
        pass


@app.post("/batch-solve")
async def batch_solve(
    images: list[UploadFile] = File(...),
    variables: Optional[str] = Form(default="{}")
) -> Dict[str, Any]:
    """
    Solve multiple math problems in batch
    
    Args:
        images: List of image files
        variables: JSON string of variables
        
    Returns:
        List of solutions for each image
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    if len(images) > 10:
        raise HTTPException(status_code=413, detail="Maximum 10 images per batch")
    
    results = []
    for image in images:
        try:
            result = await solve(image, variables)
            results.append(result)
        except HTTPException as e:
            results.append({
                "filename": image.filename,
                "status": "error",
                "detail": e.detail
            })
    
    return {
        "status": "completed",
        "total": len(results),
        "successful": sum(1 for r in results if r.get("status") == "success"),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    """Get API and system status"""
    return {
        "api_status": "running",
        "solver_initialized": solver is not None,
        "uploads_directory": str(UPLOAD_DIR),
        "max_file_size_mb": 10,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )