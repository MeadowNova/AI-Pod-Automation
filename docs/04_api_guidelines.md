# API Interaction Guidelines

**Internal Worker Service (FastAPI):**
- Base URL: `http://{WORKERS_SERVICE_HOST}:{WORKERS_SERVICE_PORT}` (from `.env`, default http://localhost:8000)[cite: 7].
- Endpoints: Refer to `pod_automation/workers/workers_service.py` for available routes (e.g., `/generate_design`, `/create_mockup`, `/optimize_seo`).
- Use `requests` library to call this service from agents when needed.

**Ollama API:**
- URL: `{OLLAMA_URL}` (from `.env`, default http://localhost:11434/api/generate)[cite: 7].
- Model: `{MODEL_NAME}` (from `.env`, default `llama3:latest`)[cite: 7].
- Use the `ollama` library or `requests` for interaction[cite: 13].

**External APIs (Printify, Stable Diffusion, Etsy, etc.):**
- Use API keys stored in `.env`[cite: 7, 17].
- Follow standard REST principles using the `requests` library[cite: 13].
- Handle errors, rate limits, and response parsing carefully. Refer to official API docs.