# Multi Agent Chatbot - Project Instructions

## Scope
These instructions apply to the full repository and should guide all code edits, bug fixes, and feature additions.

## Current Product Shape
- Backend framework: FastAPI with async SQLAlchemy, Redis, Pinecone, and LangGraph orchestration.
- Primary web UI: backend-served figma mock HTML pages.
  - Workspace route: /ui-final
  - Auth route: /ui-auth
  - Legacy alias still supported: /ui-prototype
- Secondary UI: Streamlit app in frontend/streamlit_app.py.
- Authentication model: local JWT auth plus Supabase OAuth/email exchange flow.

## Architecture Rules
- Keep route handlers thin in backend/app/api/routes and move orchestration to services or agent nodes.
- Preserve the agent state contract across backend/app/agents/state/state.py and node files.
- Reuse service-level instances (agent_service, rag_service, redis_service) instead of creating duplicates.
- Keep provider logic behind backend/app/services/llm/factory.py and the LLM provider abstraction.
- Maintain compatibility between frontend request payloads and backend ChatRequest schema.

## API Contracts To Preserve
- Auth endpoints under /api/v1/auth/*
  - Includes local login/register/me and supabase exchange/config paths.
- Chat endpoints under /api/v1/chat/*
  - send, upload, delete-namespace, models, providers, speech-to-text, text-to-speech, audio metadata, vision/ask.
- Health endpoints:
  - /health
  - /health/details

## Frontend Behavior Requirements
- Do not break per-user local history isolation in figma workspace local storage.
- Keep conversation namespace isolation for document indexing using conv_<conversation_id> pattern.
- Preserve dynamic provider/model loading from backend endpoints.
- Keep usecase-specific rendering behavior:
  - basic chat can use simple bubble rendering
  - summary-style prompts may use rich cards
  - document_qa and multi_agent support structured/rich response views
- Keep logout behavior synchronized between app token and Supabase session handling.

## Coding Guidelines
- Backend code should be async-first for I/O paths.
- Avoid moving business logic into UI templates; keep logic in JS modules/functions or backend services.
- Prefer minimal, targeted edits over broad refactors.
- Keep naming and file organization aligned with current repository structure.
- Avoid introducing breaking API or schema changes unless explicitly requested.

## Run Commands
- Backend install: pip install -r backend/requirements.txt
- Backend run (from backend folder): uvicorn app.main:app --reload
- Frontend streamlit run (from frontend folder): streamlit run streamlit_app.py

## Environment Expectations
- Required services and keys typically include:
  - DATABASE_URL
  - REDIS_URL
  - PINECONE_API_KEY and index configuration
  - GROQ_API_KEY
  - Supabase public settings for OAuth flow when enabled
- Never commit secrets, tokens, or debug logs that expose credentials.

## Quality Checks After Edits
- Validate changed files for syntax/editor errors.
- For frontend behavior changes, verify at least:
  - login/logout flow
  - chat send flow
  - document upload flow for document_qa
  - provider/model list loading
  - health endpoint reachability