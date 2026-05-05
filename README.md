# SynapseAI - Context-Aware Business Copilot

SynapseAI is an AI-powered business copilot for uploading, processing, and managing business documents. The project is being built as a production-style full-stack AI application with FastAPI, React, SQLAlchemy, Docker, and a planned RAG pipeline for document-grounded chat, summarization, citations, and structured extraction.

## Current Status

Implemented MVP foundation:

- FastAPI backend with modular architecture
- JWT authentication: register, login, current user
- User-owned document upload, list, detail, rename, and delete APIs
- Local file storage for PDF, DOCX, CSV, and TXT uploads
- Text extraction for CSV, TXT, PDF, and DOCX
- SQLAlchemy models for users, documents, and document chunks
- Dashboard stats API
- React/Vite frontend with login, register, dashboard, upload, preview, rename, delete, refresh, and logout flows
- Docker Compose setup for backend, PostgreSQL, and Redis
- GitHub Actions CI for backend tests, frontend build, and Docker build
- Automated backend API flow test and live smoke test script

Planned next milestone:

- Chunking service
- Embedding service
- FAISS or pgvector vector search
- RAG chat API with source citations
- Document summarization
- Structured information extraction
- Background jobs with Redis/Celery

## Architecture

```text
React/Vite Frontend
        |
        | REST API + JWT
        v
FastAPI Backend
        |
        | SQLAlchemy
        v
SQLite locally / PostgreSQL in Docker
        |
        +--> Local file storage: backend/storage/uploads
        |
        +--> Future RAG layer: parser -> chunker -> embeddings -> vector DB -> LLM

Redis is included in Docker Compose for upcoming background jobs and agent workflows.
```

## Tech Stack

Backend:

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose JWT auth
- Passlib bcrypt password hashing
- pypdf
- python-docx
- pytest

Frontend:

- React
- TypeScript
- Vite
- Lucide React icons
- CSS

Infrastructure:

- Docker
- Docker Compose
- GitHub Actions
- PostgreSQL
- Redis

## Project Structure

```text
.
├── .github/workflows/ci.yml
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── samples/
│   ├── scripts/
│   ├── storage/uploads/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── start-dev.ps1
```

## Prerequisites

Install these locally:

- Python 3.12 or newer
- Node.js 20 or newer
- Docker Desktop, optional but recommended
- Git

This project currently uses port `8001` for the backend because port `8000` may already be used on some machines.

## Start Both Servers

From the repository root in PowerShell:

```powershell
python -m pip install -r backend\requirements.txt
npm.cmd install --prefix frontend
.\start-dev.ps1
```

Open:

```text
Frontend: http://127.0.0.1:5174
API docs: http://127.0.0.1:8001/docs
Backend health: http://127.0.0.1:8001/health
```

## Start Backend Only

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## Start Frontend Only

```powershell
cd frontend
npm.cmd install
$env:VITE_API_BASE_URL="http://127.0.0.1:8001/api/v1"
npm.cmd run dev -- --port 5174
```

## Run With Docker

Create the backend environment file:

```powershell
copy backend\.env.example backend\.env
```

Start services:

```powershell
docker compose up --build
```

Docker services:

- `backend`
- `frontend`
- `postgres`
- `redis`

## Environment Variables

Backend example: `backend/.env.example`

```text
DATABASE_URL=postgresql+psycopg://synapse:synapse_password@postgres:5432/synapseai
SECRET_KEY=replace-with-a-long-random-secret
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5174
UPLOAD_DIR=storage/uploads
MAX_UPLOAD_MB=25
```

Frontend example: `frontend/.env.example`

```text
VITE_API_BASE_URL=http://127.0.0.1:8001/api/v1
```

## API Endpoints

Auth:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

Documents:

```text
POST   /api/v1/documents/upload
GET    /api/v1/documents
GET    /api/v1/documents/{document_id}
PATCH  /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}
```

Dashboard:

```text
GET /api/v1/dashboard/stats
```

Health:

```text
GET /health
```

## Test The Project

Backend tests:

```powershell
cd backend
python -m pytest tests -q
```

Frontend build:

```powershell
cd frontend
npm.cmd run build
```

Live API smoke test:

```powershell
cd backend
$env:SYNAPSE_API_ROOT="http://127.0.0.1:8001"
python scripts\smoke_live_api.py
```

The smoke test checks:

- Health endpoint
- Register
- Login
- Current user
- Upload CSV
- List documents
- Read document detail
- Rename document
- Dashboard stats
- Delete document
- Confirm deleted document returns 404

## CI/CD

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

The workflow runs on pushes and pull requests to `main` and `synapse-dev`.

Jobs:

- Backend tests with Python
- Frontend production build with Node
- Docker Compose config validation
- Docker Compose full-stack build
- Deployment readiness marker on push events

## Sample Files

Sample files are available in:

```text
backend/samples/sample_invoice.csv
backend/samples/meeting_notes.txt
```

Use these to test document upload and extraction.

## Development Notes

- `frontend/node_modules`, `frontend/dist`, local database files, logs, and uploaded files are ignored by Git.
- `backend/storage/uploads/.gitkeep` is committed so the upload directory exists.
- The default local backend database is SQLite unless `DATABASE_URL` points to PostgreSQL.
- Production should use PostgreSQL, object storage such as S3, background workers, and a managed vector database or pgvector.

## Roadmap

Milestone 1: Foundation

- Backend app structure
- Authentication
- Document upload and CRUD
- Frontend dashboard
- CI pipeline

Milestone 2: RAG Core

- Text chunking
- Embeddings
- Vector database
- Retrieval service
- Chat endpoint
- Source citations

Milestone 3: Business Intelligence

- Document summaries
- Invoice and contract field extraction
- Multi-document comparison
- Dashboard activity timeline

Milestone 4: Agent Workflows

- Scheduled weekly summaries
- Background jobs
- Agent task history
- Business risk detection

Milestone 5: Production Hardening

- Refresh tokens
- Role-based access control
- Organization/workspace support
- S3 storage
- Observability
- Rate limiting
- Deployment pipeline
