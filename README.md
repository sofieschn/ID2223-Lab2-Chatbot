# ID2223-Lab2-Chatbot

Local LLaMA chatbot with a React frontend and FastAPI backend.

## Running Locally

### Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- (Optional) Docker and Docker Compose for containerized local development

### Quick Start

1. **Start the backend** (in one terminal):
   ```bash
   cd app
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   The backend will be available at `http://localhost:8000`

2. **Start the frontend** (in another terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173` (or the URL printed by Vite)

3. **Open your browser** and navigate to the frontend URL. The chat interface will automatically connect to the backend.

### Backend Configuration

#### API Endpoints

- `GET /health` – quick status check
- `POST /chat` – expects `{ "message": "...", "history": [] }` and returns the assistant answer plus updated history

#### Choosing Model Backend

The FastAPI backend can use either:

- A **local GGUF model** from the `models/` folder (`chatbot.py`), or
- A **Hugging Face–hosted model** from `SofieSchn/kth-llama-lora` (`chatbot_hf.py`)

This is controlled via the `LLM_BACKEND` environment variable:

**Option 1: Local GGUF Model (Recommended for local development)**
```bash
export LLM_BACKEND=local
cd app
source .venv/bin/activate
uvicorn main:app --reload
```

**Option 2: Hugging Face Model**
```bash
export LLM_BACKEND=hf
# Optional: if repo is private (this one is public)
# export HUGGINGFACE_HUB_TOKEN=hf_...your_token...
cd app
source .venv/bin/activate
uvicorn main:app --reload
```

**Note**: For local development, the local model (`LLM_BACKEND=local`) is typically faster since it doesn't need to download files from Hugging Face. Make sure you have the model files in the `models/` directory:
- `models/Llama-3.2-1B-Instruct-Q4_1.gguf`
- `models/lora_adapter_q8_0.gguf` (optional, for LoRA adapters)

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` by default. If your backend runs on a different port or host, you can configure it:

1. Create a `.env` file in the `frontend/` directory:
   ```bash
   VITE_API_URL=http://localhost:8000/chat
   ```

2. Restart the dev server:
   ```bash
   npm run dev
   ```

### Running with Docker Locally

If you prefer to run the application using Docker containers locally:

1. **Build the images**:
   ```bash
   # Backend
   cd app
   docker build -t chatbot-backend .
   
   # Frontend
   cd ../frontend
   docker build --build-arg VITE_API_URL=http://localhost:8000/chat -t chatbot-frontend .
   ```

2. **Run the containers**:
   ```bash
   # Backend (in one terminal)
   docker run -p 8000:8000 -e LLM_BACKEND=hf chatbot-backend
   
   # Frontend (in another terminal)
   docker run -p 80:80 chatbot-frontend
   ```

3. **Access the application**:
   - Frontend: `http://localhost`
   - Backend API: `http://localhost:8000`

## Deployment

The application is deployed using Docker containers on **KTH Cloud**, a free hosting service for KTH students.

### Architecture

- **Frontend**: React application built with Vite, served via Nginx in a Docker container
- **Backend**: FastAPI application running in a Python Docker container
- **Model**: Loaded from Hugging Face Hub (`SofieSchn/kth-llama-lora`) at runtime

### Docker Containers

#### Backend Container (`app/Dockerfile`)
- Base image: `python:3.12-slim`
- Installs system dependencies (`build-essential`, `cmake`, `git`) required for `llama-cpp-python`
- Copies application code and installs Python dependencies
- Defaults to Hugging Face backend (`LLM_BACKEND=hf`)
- Exposes port 8000

#### Frontend Container (`frontend/Dockerfile`)
- Multi-stage build:
  1. Build stage: Node.js Alpine image compiles React app with Vite
  2. Serve stage: Nginx Alpine image serves static files
- Build-time argument `VITE_API_URL` configures backend API endpoint
- Exposes port 80

### Deployment Process

1. Build Docker images locally or on KTH Cloud
2. Push images to KTH Cloud container registry
3. Deploy containers as services on KTH Cloud
4. Configure environment variables (e.g., `LLM_BACKEND`, `VITE_API_URL`)

### Performance Considerations

**⚠️ Important**: The deployed application runs slower than local development due to:

1. **Limited CPU resources**: KTH Cloud provides minimal CPU allocation (typically 1-4 cores), which significantly impacts model inference speed
2. **Model loading from Hugging Face**: The model files are downloaded from Hugging Face Hub at container startup, not pre-deployed. 

For faster responses, consider:
- Running locally with more CPU cores
- Using a dedicated GPU instance (not available on free KTH Cloud tier)

### Improving Model Performance
Why We Chose a Model-Centric Approach

In this project we focused on a model-centric approach to improve performance. Since the dataset (FineTome) was predefined and limited, the most effective way to optimize the chatbot was to adjust how the model learns rather than collecting or engineering new data.

We improved performance by tuning key aspects of the fine-tuning process, such as learning rate, number of training steps, batch size, LoRA configuration, and inference parameters (context length, temperature, max tokens, etc.). These adjustments allowed us to get better, more stable responses from the model without changing the dataset.

There were threee main hyperparameters that we tested out:
- Lora alpha: it rescales the update of the Lora mechanisms before adding it to the weights, a strong one can lead to instability while a low one would have a weak adaptation
- Lora attention dimension: Adds more dimensions to the trainable matrices of Lora. A high one will have more capacity but will defeat the purpose of low-rank matrices of finetunning. A low number of dimensions would underfit.
- Lora dropout: defines the dropout number of the Lora brances that would get dropped, it's a regularization method. A high value will lead to more regularization, slow convergence and prevents forgetting. A low one lads to a fast learning but can overfit in small datasets.

Basic configuration:
1) lora alpha = 16, r (lora attention dimensions) = 16, lora dropout = 0 (optimized for the notebook)
2) lora alpha = 32, r (lora attention dimensions) = 16, lora dropout = 0 (optimized for the notebook)
3) lora alpha = 16, r (lora attention dimensions) = 32, lora dropout = 0 (optimized for the notebook)
4) lora alpha = 32, r (lora attention dimensions) = 32, lora dropout = 0 (optimized for the notebook)
4) lora alpha & r (lora attention dimensions) on the best model, lora dropout = 0.05 (optimized for the notebook)