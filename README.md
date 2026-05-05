# SynapseAI-Context-Aware-Business-Copilot
SynapseAI is an AI-powered business copilot that enables users to upload and interact with documents using natural language. It leverages RAG architecture for accurate question answering, summarization, and data extraction, delivering contextual insights with source references through a scalable, production-ready system.

## Backend MVP

The first backend milestone is implemented with FastAPI:

- JWT authentication: register, login, current user
- User-owned document upload, list, detail, and delete APIs
- Local file storage for PDF, DOCX, CSV, and TXT files
- PostgreSQL-ready SQLAlchemy models for users, documents, and chunks
- CSV/TXT text extraction starter service
- Docker Compose services for backend, PostgreSQL, and Redis

### Run Locally

```bash
cd backend
copy .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

### Run Full Stack Locally

On Windows PowerShell:

```powershell
npm.cmd install --prefix frontend
python -m pip install -r backend\requirements.txt
.\start-dev.ps1
```

The local development URLs are:

```text
Frontend: http://127.0.0.1:5174
Backend:  http://127.0.0.1:8001
API docs: http://127.0.0.1:8001/docs
```

### Run With Docker

```bash
copy backend\.env.example backend\.env
docker compose up --build
```

### API Endpoints

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me

POST   /api/v1/documents/upload
GET    /api/v1/documents
GET    /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}
PATCH  /api/v1/documents/{document_id}

GET /api/v1/dashboard/stats
```
