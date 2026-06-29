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

## Docker Deployment

### Build Docker Image

```bash
docker build -t math-solver-api:latest .
```

### Run Docker Container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key-here" \
  -v $(pwd)/uploads:/app/uploads \
  math-solver-api:latest
```

## Google Cloud Run Deployment

### Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and configured
- Docker installed

### Deploy Using Cloud Build

1. **Set up GCP project**
   ```bash
   export PROJECT_ID="your-project-id"
   export REGION="us-central1"
   gcloud config set project $PROJECT_ID
   ```

2. **Enable required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com
   ```

3. **Create Cloud Build configuration** (cloudbuild.yaml is provided)

4. **Deploy with Cloud Build**
   ```bash
   gcloud builds submit \
     --config cloudbuild.yaml \
     --substitutions=_SERVICE_NAME=math-solver-api,_REGION=$REGION,_OPENAI_API_KEY="your-key"
   ```

### Direct Cloud Run Deployment

```bash
gcloud run deploy math-solver-api \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="your-key-here" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

## File Structure

```
MathSolver-chatbot/
├── main.py                  # FastAPI application
├── Dockerfile              # Container configuration
├── cloudbuild.yaml         # GCP Cloud Build config
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .dockerignore          # Docker build ignore
├── .gcloudignore          # GCP build ignore
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

## Integration with Abishek's LangChain Functions

The AI engine is designed to integrate with LangChain solving functions. 

**Current Status**: Placeholder implementation in `ai_engine/math_solver.py`

**TODO**: Replace the `_call_langchain_solver()` method with Abishek's actual LangChain implementation.

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

### Docker build fails
- Check Docker is running
- Ensure all files are in the correct location
- Check internet connectivity for pip package downloads

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally with `uvicorn main:app --reload`
4. Commit with clear messages
5. Push and create a pull request

## Team Responsibilities

- **Frontend Developer (Gradio)**: Create the UI interface
- **API Backend Developer**: Main.py, FastAPI setup, deployment ✅ (This role)
- **AI Engineer (Abishek)**: LangChain solver functions

## Next Steps

1. ✅ Set up FastAPI backend with all endpoints
2. ✅ Create Docker configuration for Cloud Run
3. 🔄 Integrate Abishek's LangChain solver functions
4. 🔄 Connect Gradio frontend to API
5. 🔄 Test end-to-end flow
6. 🔄 Deploy to Google Cloud Run
7. 🔄 Set up monitoring and logging

## License

[Your License Here]

## Contact

For questions about the backend API, contact: [Backend Developer Email]
For LangChain integration questions, contact: Abishek
For Gradio frontend questions, contact: [Frontend Developer Email]
