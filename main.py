from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import base64
from ai_engine.llm_chain import solve_math_stream

# Initialize the FastAPI Server
app = FastAPI(title="Practical GenAI Math Assistant")

@app.post("/solve")
async def solve_endpoint(
    image: UploadFile = File(...),
    variables: str = Form("")
):
    """
    This endpoint receives the multipart image file and variables from Gradio,
    converts the image to base64, and streams the AI Engine solver response.
    """
    try:
        contents = await image.read()
        encoded_img = base64.b64encode(contents).decode('utf-8')
        
        def generator():
            for chunk in solve_math_stream(encoded_img, variables):
                yield chunk
                
        return StreamingResponse(generator(), media_type="text/plain")
    except Exception as e:
        return StreamingResponse(iter([f"Backend Error: {str(e)}"]), media_type="text/plain")

@app.get("/")
async def health_check():
    return {"status": "FastAPI Backend is running perfectly!"}