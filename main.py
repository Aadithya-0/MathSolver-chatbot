"""
FastAPI Backend for Math Solver Chatbot
Handles API endpoints for image processing and math problem solving
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import base64
import gradio as gr
from frontend.app import demo

# Import AI engine
from ai_engine.llm_chain import solve_math_stream, solve_math

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
app.gr.mount_gradio_app(app, demo, path="/gradio")

# Create uploads folder if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize AI solver
logger.info("Math Solver Engine ready (dynamic initialization)")


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
    variables: Optional[str] = Form(default="")
):
    """
    Solve a math problem from an uploaded image (streaming response)
    """
    try:
        # Validate image file
        if not image.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
        safe_filename = f"{timestamp}{image.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save uploaded file
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Image uploaded: {safe_filename}")
        
        # Convert image to base64 for llm_chain
        encoded_img = base64.b64encode(contents).decode('utf-8')
        
        def generator():
            for chunk in solve_math_stream(encoded_img, variables or ""):
                yield chunk
                
        return StreamingResponse(generator(), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        return StreamingResponse(iter([f"Backend Error: {str(e)}"]), media_type="text/plain")


@app.post("/batch-solve")
async def batch_solve(
    images: list[UploadFile] = File(...),
    variables: Optional[str] = Form(default="")
) -> Dict[str, Any]:
    """
    Solve multiple math problems in batch
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    if len(images) > 10:
        raise HTTPException(status_code=413, detail="Maximum 10 images per batch")
    
    results = []
    for image in images:
        try:
            if not image.filename:
                continue
            contents = await image.read()
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
            safe_filename = f"{timestamp}{image.filename}"
            file_path = UPLOAD_DIR / safe_filename
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Solve math synchronously
            encoded_img = base64.b64encode(contents).decode('utf-8')
            solution = solve_math(encoded_img, variables or "")
            
            results.append({
                "status": "success",
                "filename": safe_filename,
                "solution": solution,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            results.append({
                "filename": image.filename,
                "status": "error",
                "detail": str(e)
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
        "solver_initialized": True,
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
    import os
    
    # Force the default to 8080 to match Cloud Run requirements
    port = int(os.getenv("PORT", 8080))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )