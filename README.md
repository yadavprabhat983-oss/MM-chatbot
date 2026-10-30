# Multimodal AI Personal Assistant (MVP)

A modern, responsive, full-stack AI Assistant featuring **Retrieval-Augmented Generation (RAG)**, **live web search citations**, **document editing & versioning**, and **compassionate emotional assistance**.

---

## 1. Project Overview

The Multimodal AI Personal Assistant is designed as a local-first, developer-friendly MVP. It bridges the gap between text chatbots and real-world assistant workflows by supporting:
- **Multimodal Interactions:** Text, image understanding, audio transcription, and speech synthesis (TTS).
- **RAG Knowledge Base:** Upload PDF, TXT, Markdown, and Word (DOCX) files. Content is chunked, embedded, stored, and retrieved using PostgreSQL and `pgvector`.
- **Live Web Search:** Real-time web search integration (Tavily, DuckDuckGo) with source citation cards.
- **Document Workspace:** In-app document creator and editor with AI-assisted rewriting/summarization, diff reviews (Accept/Discard), version history tracking, and automatic re-indexing.
- **Empathetic Emotional Support:** A dedicated mode offering supportive, active listening, 5-4-3-2-1 grounding exercises, and box breathing, with automated crisis interception and emergency hotline referrals (988, Crisis Text Line 741741).

---

## 2. Architecture Diagram

```mermaid
flowchart TD
    subgraph Frontend["React (Vite + TypeScript)"]
        UI[Chat Interface & Composer]
        DW[Document Workspace & Editor]
        CIT[Citations Card & Audio Player]
        API_CLIENT[Typed API Service]
    end

    subgraph Backend["FastAPI Application"]
        ROUTERS["API Routers\n(/chat, /documents, /conversations, /search, /health)"]
        CHAT_SVC[Chat Orchestration Service]
        RAG_SVC[RAG Service & Chunker]
        SAFETY_SVC[Safety & Crisis Filter]
        SEARCH_SVC[Search Adapter\nTavily / DuckDuckGo]
        DOC_SVC[Document & Version Service]
        AI_ADAPTER["Provider Adapter\nOpenAI / Gemini / Mock"]
    end

    subgraph Database["PostgreSQL + pgvector"]
        CONV_TBL[(Conversations & Messages)]
        DOC_TBL[(Documents & Versions)]
        VEC_TBL[(Document Chunks & Embeddings)]
    end

    UI --> API_CLIENT
    DW --> API_CLIENT
    API_CLIENT --> ROUTERS

    ROUTERS --> CHAT_SVC
    ROUTERS --> DOC_SVC
    ROUTERS --> SEARCH_SVC

    CHAT_SVC --> SAFETY_SVC
    CHAT_SVC --> RAG_SVC
    CHAT_SVC --> SEARCH_SVC
    CHAT_SVC --> AI_ADAPTER

    RAG_SVC --> VEC_TBL
    DOC_SVC --> DOC_TBL
    CHAT_SVC --> CONV_TBL
```

---

## 3. Technology Stack

### Frontend
- **Framework:** React 18 with Vite
- **Language:** TypeScript
- **Styling:** Vanilla CSS design system with CSS custom properties, glassmorphism, responsive grid, and dark mode palette.
- **HTTP Client:** Native Fetch API with structured JSON handling and error parsing.

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Validation:** Pydantic v2 & Pydantic-Settings
- **ORM:** SQLAlchemy 2.0
- **Database Migrations:** Alembic
- **Document Extractors:** `pypdf`, `python-docx`
- **Testing:** `pytest`, `pytest-asyncio`, `httpx`

### Database
- **Engine:** PostgreSQL 16
- **Extension:** `pgvector` (`pgvector/pgvector:pg16` Docker image)
- **Vector Metric:** Cosine Distance (`<=>`)

---

## 4. Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Git**
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Docker & Docker Compose** (for PostgreSQL + pgvector)

---

## 5. Quick Start & Step-by-Step Installation

### One-Command Full Stack (Docker Compose)
Run the entire application (Postgres + pgvector, FastAPI Backend, and React Frontend) with one command:
```bash
docker compose up --build
```
- **Web App:** http://localhost:5173
- **FastAPI Docs:** http://localhost:8000/docs

---

### One-Click Local Scripts
- **Windows:** Run `start_all.bat` (or double-click it in File Explorer)
- **Linux / macOS:**
  ```bash
  chmod +x run_backend.sh run_frontend.sh
  ./run_backend.sh & ./run_frontend.sh
  ```

---

### Step 1: Clone or Navigate to the Workspace
```bash
cd mmchatbot
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Linux / macOS
cp .env.example .env

# On Windows (Command Prompt / PowerShell)
copy .env.example .env
```
*(By default, `.env` is pre-configured with `AI_PROVIDER=mock` so the entire application runs locally out of the box without requiring external API keys. See Section 7 for configuring real OpenAI or Gemini keys.)*

---

### Step 3: Start PostgreSQL with pgvector (Docker Compose)
Launch the pgvector-enabled PostgreSQL container:
```bash
docker-compose up -d
```
Verify the container is healthy:
```bash
docker ps
```
The database runs on `localhost:5432` with user `postgres`, password `postgres`, and database `mmchatbot_db`.

---

### Step 4: Setup and Run the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Windows (CMD)
   .venv\Scripts\activate.bat

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend API is now live at: `http://localhost:8000`
   Interactive Swagger documentation is available at: `http://localhost:8000/docs`

---

### Step 5: Setup and Run the Frontend

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open your browser at: `http://localhost:5173`

---

## 6. Database Schema & Migrations

The database manages five core tables:
- **`conversations`**: Chat sessions with titles and timestamps.
- **`messages`**: Multi-turn history, sender role (`user`, `assistant`), and multimodal metadata (citations, audio URL, image URL).
- **`documents`**: Ingested knowledge files, extraction status (`indexing`, `indexed`, `failed`), and error messages.
- **`document_versions`**: Historical snapshots of document edits.
- **`document_chunks`**: Text chunks with `vector` embedding columns and chunk indices.

### Useful Alembic Migration Commands
```bash
# Check current migration revision
alembic current

# Apply all migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

---

## 7. Configuration & Environment Variables

Edit `.env` to configure AI providers and search services:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/mmchatbot_db` |
| `AI_PROVIDER` | Active AI provider (`openai`, `gemini`, `mock`) | `mock` |
| `OPENAI_API_KEY` | OpenAI API key (required if `AI_PROVIDER=openai`) | `""` |
| `OPENAI_CHAT_MODEL` | OpenAI LLM chat model | `gpt-4o-mini` |
| `OPENAI_VISION_MODEL` | OpenAI Vision model | `gpt-4o-mini` |
| `OPENAI_IMAGE_MODEL` | OpenAI Image generation model | `dall-e-3` |
| `OPENAI_TTS_MODEL` | OpenAI Speech synthesis model | `tts-1` |
| `GEMINI_API_KEY` | Google Gemini API key (if `AI_PROVIDER=gemini`) | `""` |
| `GEMINI_CHAT_MODEL` | Gemini LLM chat model | `gemini-1.5-flash` |
| `EMBEDDING_PROVIDER` | Embedding model provider (`openai`, `gemini`, `mock`) | `mock` |
| `EMBEDDING_DIMENSIONS`| Vector dimensions (1536 for OpenAI, 768 for Gemini) | `1536` |
| `SEARCH_PROVIDER` | Web search provider (`duckduckgo`, `tavily`, `mock`) | `duckduckgo` |
| `TAVILY_API_KEY` | Tavily Search API key (optional) | `""` |
| `RAG_CHUNK_SIZE` | Target character length for document chunks | `500` |
| `RAG_CHUNK_OVERLAP` | Overlapping characters between consecutive chunks | `100` |
| `RAG_TOP_K` | Number of most similar chunks retrieved for prompts | `4` |
| `RAG_SIMILARITY_THRESHOLD` | Minimum cosine similarity score for RAG retrieval | `0.65` |

---

## 8. RAG Ingestion & Vector Retrieval Workflow

1. **Upload & Extract:**
   - Supported formats: `.pdf`, `.docx`, `.txt`, `.md`.
   - Text is parsed using `pypdf` (extracting per page) or `python-docx` (extracting paragraphs).
2. **Chunking:**
   - `chunk_text()` splits text with sliding-window overlap (`RAG_CHUNK_SIZE` and `RAG_CHUNK_OVERLAP`), respecting paragraph breaks.
3. **Embedding Generation:**
   - The configured embedding service generates vector representations for each text chunk.
4. **PostgreSQL pgvector Storage:**
   - Chunks are stored in `document_chunks` with the `vector` type.
5. **Retrieval & Citations:**
   - On incoming questions, the prompt is embedded and compared against chunk vectors using `<=>` (cosine distance).
   - Relevant chunks passing the similarity threshold are inserted into the system prompt under `[RETRIEVED DOCUMENT CONTEXT]`.
   - Source citations containing the document name and chunk index are returned to the frontend.

---

## 9. Document Workspace & AI-Assisted Editing Workflow

1. Click **Documents** in the header to open the Document Workspace.
2. Upload existing documents or click **+ New Document** to create one.
3. Select any document to open the **Document Editor**.
4. Use the **AI Assist** toolbar:
   - **Summarize:** Extracts core takeaways.
   - **Expand:** Elaborates on key concepts.
   - **Rewrite:** Improves clarity and structure.
   - **Fix Grammar:** Polishes punctuation and grammar.
   - **Custom Prompt:** Provide tailored instructions (e.g., *"Convert into a numbered FAQ"*).
5. **Review AI Diffs:** The editor presents proposed changes in a dedicated diff box with **Accept Changes** and **Discard** buttons.
6. **Save & Version:** Clicking **Save & Re-index RAG** creates a new version entry in `document_versions` and updates the vector index.
7. **Export:** Click **⬇ .md** or **⬇ .txt** to download the document.

---

## 10. Emotional Assistance & Safety Behavior

- **Empathetic Listening Mode:** Activate the **💖 Emotional Support** toggle in the composer. Responses prioritize emotional validation, empathetic active listening, gentle open-ended questions, and evidence-based grounding tools (5-4-3-2-1 technique, box breathing).
- **Crisis Interception:** Automated regex and pattern detection scans for explicit expressions of self-harm or suicidal intent.
- **Safety Response:** When a crisis is detected, the assistant immediately provides emergency contact numbers:
  - **988 Suicide & Crisis Lifeline** (US & Canada, call or text 988)
  - **Crisis Text Line** (Text HOME to 741741)
  - **International Support:** [findahelpline.com](https://findahelpline.com/)
  - Immediate local emergency referral (911 / 999 / 112).
- **Ethical Disclaimer:** The assistant clearly disclaims that it is an AI, not a doctor, therapist, or crisis monitor, and never prescribes medication or diagnoses conditions.

---

## 11. API Endpoints with Sample Requests

### 1. Health & Readiness
```bash
# App Health
curl -X GET http://localhost:8000/api/health

# Database & pgvector Readiness
curl -X GET http://localhost:8000/api/health/ready
```

### 2. Chat with RAG and Web Search
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does our project architecture look like?",
    "search_web": false,
    "emotional_mode": false,
    "generate_tts": false
  }'
```

### 3. List and Create Conversations
```bash
# List conversations
curl -X GET http://localhost:8000/api/conversations

# Create conversation
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Product Research"}'
```

### 4. Upload and Ingest Document
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@notes.txt" \
  -F "title=Meeting Notes"
```

### 5. AI Edit Document
```bash
curl -X POST http://localhost:8000/api/documents/1/ai-edit \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Summarize this into bullet points",
    "action": "summarize"
  }'
```

### 6. Live Web Search
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fastapi best practices",
    "max_results": 3
  }'
```

---

## 12. Automated Testing

The project includes an automated test suite verifying health endpoints, conversations, document uploads, text extraction, RAG vector retrieval, stale index removal, crisis interception, and web search fallback.

To execute tests:
```bash
cd backend
pytest -v
```

All unit tests use mocked AI and search providers with an in-memory SQLite database, requiring **zero API tokens or network calls**.

---

## 13. Troubleshooting Common Issues

### 1. `pgvector` extension error during migration
- **Symptom:** `type "vector" does not exist`
- **Fix:** Ensure you are using the official `pgvector/pgvector:pg16` image specified in `docker-compose.yml`. Standard PostgreSQL images do not include the C-extension for vector operations.

### 2. Port 5432 conflict
- **Symptom:** `Bind for 0.0.0.0:5432 failed: port is already allocated`
- **Fix:** Another local PostgreSQL instance is running. Stop the local service or change the port mapping in `docker-compose.yml` to `5433:5432` and update `DATABASE_URL` in `.env`.

### 3. Audio transcription or TTS generation fails
- **Symptom:** `AIProviderError: OpenAI API key is not configured`
- **Fix:** Audio features (Whisper transcription and TTS) require a valid `OPENAI_API_KEY` in `.env`. In mock mode, simulated audio responses and placeholders are provided.

---

## 14. Security & Privacy Considerations

> [!WARNING]
> This MVP is designed exclusively for local development and personal use.
> It does NOT include authentication, user authorization, or rate limiting.
> Do NOT expose this application directly to the public internet without implementing proper authentication (e.g. OAuth2/JWT), per-user data isolation, and API rate limits.

---

## 15. Next Recommended Improvements

1. **Authentication & Multi-User Support:** Add JWT/OAuth2 user sessions and row-level access control so users see only their documents.
2. **Hybrid Search (BM25 + Dense Vectors):** Combine PostgreSQL full-text search (`tsvector`) with `pgvector` for enhanced keyword recall.
3. **Streaming Responses:** Implement Server-Sent Events (SSE) or WebSockets for real-time word-by-word streaming in the chat interface.
4. **Local LLM Support (Ollama / vLLM):** Add an adapter for running local offline models (e.g. Llama 3, Mistral) via Ollama.
