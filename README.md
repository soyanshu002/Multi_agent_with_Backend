# Multi Agent Chatbot - Smruti AgentX

Smruti AgentX is a full-stack AI chatbot workspace with FastAPI backend orchestration and two frontend experiences:
- Primary UI: backend-served figma mock pages
- Secondary UI: Streamlit app

It supports chat, document Q&A (RAG), image Q&A (vision), and audio workflows (STT/TTS), with local JWT auth and Supabase-based OAuth exchange.

## What Has Been Implemented

### 1. Core Backend Foundation
- FastAPI app with async startup/shutdown lifecycle
- Router-based API structure
- SQLAlchemy async database setup
- Redis connection lifecycle management
- Health endpoints for quick environment checks

### 2. Agent and LLM Flow
- Agent orchestration through LangGraph
- Usecase-aware routing for:
  - basic_chat
  - document_qa
  - multi_agent (currently fallback behavior for assistant flow)
- Provider/model abstraction with LLM factory pattern
- Dynamic provider/model listing endpoints for frontend selection

### 3. RAG and Documents
- Document upload and indexing flow
- Pinecone namespace support per conversation
- Expanded file support in document loading/chunking path
- Structured response metadata support for richer frontend rendering

### 4. Audio and Vision
- Speech-to-Text endpoint integration (Groq-based STT)
- Text-to-Speech endpoint integration (OpenAI TTS style response)
- Vision image Q&A endpoint
- Vision model fallback/candidate handling for reliability

### 5. Authentication
- Local email/password register and login endpoints
- JWT-based protected API access
- Supabase config endpoint for frontend OAuth setup
- Supabase token exchange endpoint to issue local backend JWT
- Auth UI and logout behavior improvements for account switching

### 6. Frontend (Figma Mock Workspace)
- Final workspace route: /ui-final
- Auth route: /ui-auth
- Prototype alias route retained: /ui-prototype
- Chat-focused workspace with sidebar navigation
- Recent thread/history persistence and per-user local isolation
- Usecase-aware response rendering
- Rich response cards for summary/document/multi flows
- Simple bubble responses for normal basic chat prompts
- Dark theme pass and text contrast improvements

### 7. Streamlit Frontend
- Updated Streamlit interface to align visually with figma mock direction
- Integrated backend chat, document upload, health, and audio operations
- Thread/session behavior aligned with app flow

## Project Structure

- backend/app/main.py: FastAPI app entrypoint, router mounting, UI file serving routes
- backend/app/api/routes: Auth, Chat, Health route handlers
- backend/app/agents: Graph, nodes, and state for assistant orchestration
- backend/app/services: LLM, RAG, Redis, and other supporting services
- frontend/figma_mock: HTML-based primary UI (auth and workspace)
- frontend/streamlit_app.py: Streamlit-based secondary UI

## API Overview

### Auth
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- GET /api/v1/auth/supabase/config
- POST /api/v1/auth/supabase/exchange

### Chat and Multimodal
- POST /api/v1/chat/send
- POST /api/v1/chat/upload
- POST /api/v1/chat/delete-namespace
- GET /api/v1/chat/models
- GET /api/v1/chat/providers
- POST /api/v1/chat/speech-to-text
- POST /api/v1/chat/text-to-speech
- GET /api/v1/chat/audio/voices
- GET /api/v1/chat/audio/languages
- POST /api/v1/chat/vision/ask

### Health
- GET /health
- GET /health/details

## Run Locally

## Backend
1. Go to backend folder
2. Install dependencies:
	pip install -r requirements.txt
3. Start server:
	uvicorn app.main:app --reload

## Frontend (Streamlit)
1. Go to frontend folder
2. Install dependencies:
	pip install -r requirements.txt
3. Start Streamlit:
	streamlit run streamlit_app.py

## Primary HTML UI (served by backend)
- Workspace: /ui-final
- Auth: /ui-auth

## Environment Requirements

Typical required env values:
- DATABASE_URL
- REDIS_URL
- PINECONE_API_KEY and related Pinecone settings
- GROQ_API_KEY
- Supabase settings for OAuth mode:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY

## Current Status

Completed:
- Chat, RAG, audio endpoints, audio UI integration, and multimodal vision flow
- Dynamic provider/model handling
- Supabase + local auth bridge
- Final figma mock workspace and auth routing
- Thread persistence and cross-account isolation fixes
- UI styling passes (including dark mode adjustments)

Pending:
- Full audio feature end-to-end validation pass

## Notes

- Keep API payload compatibility between frontend clients and backend ChatRequest.
- Keep conversation-based namespace isolation for document operations.
- Avoid committing secrets or environment values.
