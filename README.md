# ID2223-Lab2-Chatbot

Local LLaMA chatbot with a React frontend and FastAPI backend.

Visit the deployed app: https://chatbot-sofieyair.app.cloud.cbh.kth.se/

## Running Locally

### Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- (Optional) Docker and Docker Compose for containerized local development

### Local Development Setup

**Important**: For local development, use the **Hugging Face backend** (`LLM_BACKEND=hf`) and configure the frontend to connect to `localhost`.

#### Step 1: Start the Backend (Terminal 1)

1. Navigate to the backend directory:
   ```bash
   cd app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set the backend to use Hugging Face model** and start the server:
   ```bash
   export LLM_BACKEND=hf
   uvicorn main:app --reload
   ```

   The backend will be available at `http://localhost:8000`

   **Note**: The first time you run this, the model files will be downloaded from Hugging Face Hub (this may take a few minutes). Subsequent runs will be faster.

#### Step 2: Configure and Start the Frontend (Terminal 2)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already done):
   ```bash
   npm install
   ```

3. **Configure the frontend to use localhost**:
   
   Open `frontend/src/App.tsx` and set:
   ```ts
   const USE_LOCAL_BACKEND = true;
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173` (or the URL printed by Vite)

#### Step 3: Open the Application

Open your browser and navigate to the frontend URL (typically `http://localhost:5173`). The chat interface will automatically connect to your local backend at `http://localhost:8000`.

### Switching Between Local and Deployed Backend

- **To use local backend**: Set `USE_LOCAL_BACKEND = true` in `frontend/src/App.tsx`
- **To use deployed backend**: Set `USE_LOCAL_BACKEND = false` in `frontend/src/App.tsx` (or use the default KTH Cloud URL)

### Backend Configuration

#### API Endpoints

- `GET /health` – quick status check
- `POST /chat` – expects `{ "message": "...", "history": [] }` and returns the assistant answer plus updated history

#### Conversation Context & History Handling

Both backends keep an internal text buffer that represents the ongoing conversation, which is sent to the model on every turn.

- **Local backend (`chatbot.py`)**:  
  - The class `LLM_model` maintains a `history_str` attribute.  
  - For each new user message, it appends  
    `User: <message>\nAssistant: `  
    to `history_str`, calls the model with that full string, and then appends the generated answer.  
  - As long as `save_hist=True` (default in `chatbot.py`), the full dialogue history is preserved and the model can use previous turns as context. If `save_hist=False`, the history is cleared after each response, and every turn is effectively stateless.

- **Hugging Face backend (`chatbot_hf.py`)**:  
  - The `LLM_model` also maintains a `history_str`, but it is initialized with a system message that sets the assistant behavior (friendly KTH chatbot, conversational style, etc.).  
  - On every turn it appends  
    `User: <message>\nAssistant: `,  
    calls the model with the accumulated `history_str`, then appends the answer.  
  - There is no explicit toggle to disable history here; the conversation remains stateful for the lifetime of the Python process.

In both cases, the **conversation is reset** when the backend process restarts (e.g., when you restart `uvicorn` or redeploy the container). The frontend sends each new message to `/chat`, and the backend uses its own internal `history_str` to give the model access to previous turns.

#### Choosing Model Backend

The FastAPI backend can use either:

- A **local GGUF model** from the `models/` folder (`chatbot.py`), or
- A **Hugging Face–hosted model** from `SofieSchn/kth-llama-lora` (`chatbot_hf.py`)

This is controlled via the `LLM_BACKEND` environment variable:

**For Local Development: Use Hugging Face Backend**

```bash
export LLM_BACKEND=hf
cd app
source .venv/bin/activate
uvicorn main:app --reload
```

**Note**: The Hugging Face backend (`LLM_BACKEND=hf`) is recommended for local development as it matches the deployed environment. The model files will be downloaded automatically from Hugging Face Hub on first run.

**Alternative: Local GGUF Model**

If you have the model files locally and want to use them instead:

```bash
export LLM_BACKEND=local
cd app
source .venv/bin/activate
uvicorn main:app --reload
```

Make sure you have the model files in the `models/` directory:
- `models/Llama-3.2-1B-Instruct-Q4_1.gguf`
- `models/lora_adapter_q8_0.gguf` (optional, for LoRA adapters)

### Frontend Configuration

The frontend backend URL is controlled by the `USE_LOCAL_BACKEND` flag in `frontend/src/App.tsx`:

- **`USE_LOCAL_BACKEND = true`**: Connects to `http://localhost:8000/chat` (for local development)
- **`USE_LOCAL_BACKEND = false`**: Uses the deployed backend URL (default: KTH Cloud)

Alternatively, you can set the `VITE_API_URL` environment variable:

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