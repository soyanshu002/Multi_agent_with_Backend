# Project Guidelines

## Code Style
- Keep backend code async-first. New API handlers, services, and DB flows should use `async def` and `await` consistently.
- Follow the existing layered structure in `backend/app`: keep route logic thin and move orchestration into services or agent nodes.
- Reuse existing service singletons (`agent_service`, `rag_service`, `redis_service`) instead of creating duplicate instances.
- Keep provider abstractions behind the LLM factory and `BaseLLMProvider` contract when adding model providers.
- For frontend, keep Streamlit state in `st.session_state` and route through page functions in `frontend/streamlit_app.py`.

## Architecture
- Backend entrypoint: `backend/app/main.py` (FastAPI app, lifespan hooks, router mounting).
- API layer: `backend/app/api/routes` (auth, chat, files, health).
- Agent orchestration: LangGraph state machine in `backend/app/agents/graph/graph.py`.
- Agent state contract: `backend/app/agents/state/state.py` (`AgentState` keys must stay compatible across nodes).
- Node implementations: `backend/app/agents/nodes` (router, basic chat, RAG).
- Services layer: `backend/app/services` (LLM providers/factory, RAG/Pinecone, Redis, Cloudinary).
- Persistence: async SQLAlchemy in `backend/app/db`.
- Frontend: Streamlit app in `frontend/streamlit_app.py` (current page stubs in `frontend/pages/` are not the active flow).

## Build and Test
- Backend install: `pip install -r backend/requirements.txt`
- Backend run (from `backend/`): `uvicorn app.main:app --reload`
- Frontend run (from `frontend/`): `streamlit run streamlit_app.py`
- Health checks:
  - `GET /health`
  - `GET /health/details`
- Tests are not yet configured in this repository. If adding features, include at least basic tests for changed behavior.

## Conventions
- Keep conversation-scoped document isolation via Pinecone namespace patterns (`conv_<conversation_id>`).
- Maintain Redis history key conventions and short-context retrieval patterns used by agent nodes.
- Preserve the current route contract used by the Streamlit frontend (`/api/v1/auth/*`, `/api/v1/chat/*`, `/health*`).
- Be careful when touching provider options: config lists multiple providers, but the active implementation is currently Groq in `backend/app/services/llm/factory.py`.
- Keep API payload compatibility with the current frontend chat request shape from `frontend/streamlit_app.py`.

## Environment and Pitfalls
- Local/dev setup expects external dependencies to be available:
  - PostgreSQL via `DATABASE_URL`
  - Redis via `REDIS_URL`
  - Pinecone via `PINECONE_API_KEY` and index settings
  - Groq via `GROQ_API_KEY`
- Use `.env.example` as the source of required variables.
- `frontend/requirements.txt` is currently empty; add explicit frontend dependencies there when updating frontend setup.
- Avoid committing debug prints or secrets (for example, API key preview logs in config code).