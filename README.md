# TriCoach AI — Endurance & Triathlon Coach Agent

![TriCoach AI Demo](demo.gif)

**TriCoach AI** is an intelligent endurance and triathlon coaching assistant built with Google's Agent Development Kit (`google-adk`), powered by Gemini Flash (`gemini-flash-latest`), and deployed on Google Cloud Agent Runtime. It provides personalized heart rate zone calculations, workout catalog queries, outdoor training route elevation analysis, live weather reports, RAG-assisted training manual guidance, AI-generated achievement badges, and video clips—all presented through a responsive web interface with dynamic A2UI rich surface cards and a Dark/Light mode theme toggle.

---

## 🚀 Key Features & Google Cloud Services

The agent implements the following integrated tools and Google Cloud services:

* **Vertex AI Memory Bank**: Preserves user profiles, target race dates, FTP (Functional Threshold Power), max heart rate, and training history across session turns using `PreloadMemoryTool` and `callback_context.add_session_to_memory()`.
* **Google Cloud Firestore**: Persists workout logs and queries workout catalog items (`list_workouts`, `get_workout_details`, `log_completed_workout`) from Firestore (`workouts` collection).
* **Google Cloud Storage (GCS)**: Stores generated motivational achievement badges and training video clips in a public Cloud Storage bucket for direct HTTPS serving.
* **Vertex AI Search & RAG**: Accesses triathlon manuals and exercise science guidelines via `consult_triathlon_manual` querying a Vertex AI Search corpus.
* **Imagen 3 Image Generation**: Generates custom achievement badges (`generate_triathlon_badge_image`) using `imagen-3.0-generate-002`, saving output artifacts and uploading directly to GCS.
* **Google Omni Video Generation**: Produces short triathlon training video clips (`generate_triathlon_video`) using `gemini-omni-flash-preview` in the `global` region via the Vertex AI Interactions API.
* **A2UI Structured Surface Rendering**: Generates rich, dynamic UI components (cards, columns, rows, text, images) using A2UI schema manager v0.8 Basic Catalog for seamless frontend rendering.
* **Google Maps Elevation API**: Analyzes outdoor running and cycling routes (`analyze_outdoor_route_feasibility`) for distance, elevation gain, incline slope grade, and safety feasibility.
* **Open-Meteo Weather API**: Retrieves real-time outdoor training weather conditions (`get_outdoor_training_weather`) including temperature and wind speed.
* **Heart Rate Zone Calculator**: Calculates 5-zone cardiovascular training ranges based on maximum heart rate (`calculate_training_zones`).
* **Agent Engine Sandbox Code Executor**: Safely executes Python code in a sandboxed runtime environment (`AgentEngineSandboxCodeExecutor`).

---

## 📁 Repository Structure

```
tricoach-ai/
├── app/                      # Core agent logic and tools
│   ├── agent.py              # Agent definition, Memory Bank, and A2UI callbacks
│   ├── a2ui_utils.py         # A2UI response processing utilities
│   └── tools/                # Specialized domain tools
│       ├── elevation_tool.py   # Google Maps Elevation & Route feasibility
│       ├── image_tool.py       # Imagen 3 badge generation & GCS upload
│       ├── rag_tool.py         # Vertex AI RAG manual consultation
│       ├── video_tool.py       # Google Omni video generation & GCS upload
│       ├── weather_tool.py     # Weather forecast integration
│       ├── workout_tools.py    # Firestore workout database tools
│       └── zone_calculator.py  # Heart rate zone calculator
├── frontend/                 # FastAPI proxy server and branded chat UI
│   ├── main.py               # FastAPI proxy forwarding A2A chat requests
│   └── static/               # HTML/CSS UI with Dark/Light theme toggle & A2UI renderer
├── demo.gif                  # Looping demo recording
├── agents-cli-manifest.yaml  # Agent manifest configuration
└── pyproject.toml            # Project dependencies and configuration
```

---

## 💻 Local Setup & Execution

### Prerequisites

* Python 3.10+
* `uv` package manager (`pip install uv`)
* `google-agents-cli` (`uv tool install google-agents-cli`)
* Google Cloud SDK (`gcloud`) with active GCP authentication (`gcloud auth application-default login`)

### Running the Web Frontend Locally

1. Install project dependencies:
   ```bash
   uv sync
   ```

2. Set environment variables and start the FastAPI frontend proxy:
   ```bash
   cd frontend
   export AGENT_ENGINE_RESOURCE_NAME="projects/<your-project-id>/locations/us-east1/reasoningEngines/<your-reasoning-engine-id>"
   export AGENT_DIRECTORY="app"
   uv run python main.py
   ```

3. Open your web browser to port `8080` on localhost to interact with TriCoach AI.

### Testing with Agent Playground

To interact directly with the agent in the local CLI playground:
```bash
agents-cli playground
```

---

## ☁️ Deployment

### Deploying the Agent to Agent Platform

Deploy the agent to Google Cloud Agent Runtime:
```bash
agents-cli deploy --project <your-gcp-project-id> --no-confirm-project
```

### Deploying the Frontend to Cloud Run

Deploy the FastAPI frontend proxy to Google Cloud Run:
```bash
cd frontend
gcloud run deploy tricoach-ai-frontend \
    --source . \
    --region us-central1 \
    --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<your-project-id>/locations/us-east1/reasoningEngines/<your-reasoning-engine-id>",AGENT_DIRECTORY="app" \
    --allow-unauthenticated \
    --project <your-gcp-project-id>
```
