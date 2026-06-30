# Math AI Assistant - Backend

A FastAPI-based backend service for solving math problems from images using AI/LangChain integration.

## Overview

This service provides REST API endpoints for:
- Uploading images containing math problems
- Processing images with AI to extract and solve the problems
- Returning step-by-step solutions with explanations
- Batch processing multiple images

## Architecture

```
┌─────────────────────┐
│   Gradio Frontend   │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │ FastAPI     │
    │ (main.py)   │
    └──────┬──────┘
           │
    ┌──────▼──────────┐
    │  AI Engine      │
    │ (LangChain)     │
    └─────────────────┘
```

## API Endpoints

### Health & Status

- **GET** `/` - Root endpoint (health check)
- **GET** `/health` - Health check for Cloud Run
- **GET** `/status` - Detailed API status

### Image Solving

- **POST** `/solve` - Solve a single math problem from an image
  ```bash
  curl -X POST "http://localhost:8000/solve" \
    -F "image=@problem.png" \
    -F "variables={}" \
    -F "step_by_step=true"
  ```

- **POST** `/batch-solve` - Solve multiple math problems
  ```bash
  curl -X POST "http://localhost:8000/batch-solve" \
    -F "images=@problem1.png" \
    -F "images=@problem2.png" \
    -F "variables={}"
  ```

## Gradio Frontend & Integration

The Gradio frontend component (`frontend/app.py`) provides the web interface for the application:
1. **Upload Equation Image**: Lets a user upload an image of a math problem (handwritten or typed).
2. **Provide Variables**: Lets the user optionally type in variable values (e.g. `x = 5, y = 3`).
3. **Solve**: Sends both parameters to the FastAPI backend, which runs OCR + the LangChain/FAISS retrieval chain and returns a solved answer.
4. **Step-by-Step Explanation**: Displays the answer and formatted step-by-step working if provided.

### Frontend-Backend Contract
The frontend communicates with the FastAPI backend using the following protocol:
- **Endpoint**: `POST {BACKEND_URL}/solve`
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `image`: file (the uploaded image)
  - `variables`: string (free-text variable values, e.g. "x = 5", may be empty)
- **Response Format (JSON Stream)**:
  ```json
  {
    "answer": "string",
    "steps": "string (optional)",
    "error": "string (optional)"
  }
  ```

### Configuration
Set the `BACKEND_URL` in a `.env` file or environment variable. If not set, it defaults to `http://127.0.0.1:{PORT}` (using local loopback) for integrated deployment.

## Setup & Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd MathSolver-chatbot
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## Google Cloud Deployment

This application can be deployed directly to Google Cloud Platform (GCP) without using Docker. There are two primary recommended ways to host:

### Option 1: Google App Engine (Standard Environment)

Google App Engine Standard runs Python applications natively and manages the scaling and environment automatically.

#### Prerequisites
- A Google Cloud Project with billing enabled
- The `gcloud` CLI installed and configured on your machine

#### Steps to Deploy
1. **Configure Environment Variables**:
   Define any environment variables required by your application (e.g. `GROQ_API_KEY`, `OPENAI_API_KEY`) inside `app.yaml`:
   ```yaml
   runtime: python311
   entrypoint: uvicorn main:app --host 0.0.0.0 --port $PORT

   env_variables:
     GROQ_API_KEY: "your-groq-api-key"
     OPENAI_API_KEY: "your-openai-api-key"
     ENVIRONMENT: "production"
   ```

2. **Run Deploy Command**:
   Run the following command from the root directory:
   ```bash
   gcloud app deploy
   ```

### Option 2: Google Cloud Run (Source-Based Deployment)

Google Cloud Run allows you to deploy directly from source code without having Docker installed locally. Google Cloud Buildpacks will automatically detect the Python runtime, build a container image, and run it using the `Procfile` entrypoint.

#### Steps to Deploy
1. **Deploy from Source**:
   Run the `gcloud run deploy` command with the `--source` option:
   ```bash
   gcloud run deploy math-solver-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GROQ_API_KEY="your-groq-api-key",ENVIRONMENT="production" \
     --memory 2Gi \
     --cpu 2 \
     --timeout 3600
   ```


## File Structure

```
MathSolver-chatbot/
├── main.py                  # FastAPI application
├── app.yaml                 # GCP App Engine Standard configuration
├── Procfile                 # GCP Cloud Run Buildpacks configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gcloudignore          # GCP deployment ignore list
├── ai_engine/
│   ├── __init__.py
│   └── math_solver.py     # AI solver engine with LangChain
├── frontend/              # Gradio UI (separate)
└── uploads/               # Uploaded images (auto-created)
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for LangChain/GPT-4 Vision
- `ENVIRONMENT` - "development" or "production"
- `PORT` - Port to run the service (default: 8000)
- `LANGCHAIN_API_KEY` - Optional LangChain tracing API key
- `LOG_LEVEL` - Logging level (default: INFO)

## LangChain AI Solver Engine

The AI core in `ai_engine/` handles math problem evaluation using LangChain and a custom RAG (Retrieval-Augmented Generation) setup:
- `ai_engine/llm_chain.py`: Coordinates the prompt generation, guardrails, and streaming response from the Groq vision model.
- `ai_engine/rag_setup.py`: Implements the retrieval mechanism using FAISS vector store and HuggingFace embeddings.

## Testing

### Run Tests
```bash
pytest tests/
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Solve an image
curl -X POST "http://localhost:8000/solve" \
  -F "image=@test_image.png" \
  -F "variables={\"x\": 5}" \
  -F "step_by_step=true"
```

## Monitoring & Logging

- **Local**: Logs printed to console and file
- **Cloud Run**: Logs available in Cloud Logging dashboard
- **Health Check**: Automatic at `GET /health`

## Performance & Scaling

- **Max file size**: 10MB per image
- **Batch size**: Max 10 images per request
- **Recommended Cloud Run**: 2 vCPU, 2GB memory
- **Timeout**: 3600 seconds (1 hour) for long-running tasks

## Common Issues

### "OPENAI_API_KEY not set"
- Ensure you've created `.env` file with your OpenAI API key
- Or set the environment variable in your shell

### "Module not found" errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct virtual environment

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally with `uvicorn main:app --reload`
4. Commit with clear messages
5. Push and create a pull request

## Team Responsibilities

- **Frontend Developer (Gradio)**: Create the UI interface
- **API Backend Developer**: Main.py, FastAPI setup, deployment
- **AI Engineer**: LangChain solver functions

## Next Steps

1. ✅ Set up FastAPI backend with all endpoints
2. ✅ Configure non-docker direct deployment configurations for GCP
3. 🔄 Integrate LangChain solver functions
4. 🔄 Connect Gradio frontend to API
5. 🔄 Test end-to-end flow
6. 🔄 Deploy to Google Cloud Run
7. 🔄 Set up monitoring and logging

## License

[Your License Here]

## Contact

For questions about the backend API, contact: [Backend Developer Email]
For LangChain integration questions, contact: [AI Engineer Email]
For Gradio frontend questions, contact: [Frontend Developer Email]