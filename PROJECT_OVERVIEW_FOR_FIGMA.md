# Multi Agent Chatbot - Product and UX Brief (For Figma)

## 1) What this project does
This is a full stack AI chatbot platform with:
- User authentication (register, login, profile)
- Real time chat with selectable provider and model
- Agent routing between normal chat and document question answering
- Document upload and indexing to Pinecone for RAG
- Conversation memory using Redis
- Health monitoring for API, database, and Redis
- Audio features:
  - Speech to Text (user voice to text)
  - Text to Speech (assistant response audio)

Backend stack:
- FastAPI + async architecture
- LangGraph based agent orchestration
- PostgreSQL (users, conversations, messages, uploaded files)
- Redis (short term chat history cache)
- Pinecone vector database (document retrieval)

Frontend stack:
- Streamlit app with multi page navigation and modern chat interface

## 2) Main chatbot behavior
The chatbot supports three operational modes:

1. Basic Chatbot
- General Q and A
- Coding help, writing, brainstorming, explanations
- Uses recent conversation memory from Redis

2. Document QA
- User uploads documents
- Files are chunked, embedded, stored in Pinecone namespace
- Chat answers are generated only from retrieved context
- If context is missing, assistant responds that it does not have enough info

3. Multi Agent (currently fallback)
- Present in routing design
- Current graph maps this path to basic chat response behavior
- Can be expanded later to specialized agent workflows

Auto routing behavior:
- If user selects explicit use case, router respects it
- If conversation has documents, router prefers document QA
- Otherwise router LLM decides the next node

## 3) End to end user flow
1. User signs in
2. User enters chat page
3. User selects provider, model, use case
4. User sends text or voice input
5. Backend validates model and routes to the proper node
6. Assistant returns response (text and optional audio playback)
7. User can upload documents and switch to Document QA
8. User can check system health and conversation history

## 4) Use cases you should design in Figma
Primary use cases:
- Authentication (Sign in, Create account)
- Chat workspace (message list, composer, model controls)
- Voice interaction (record, transcribe, play response audio)
- Document workflow (upload, index status, namespace management)
- Health dashboard (backend, database, redis status)
- Conversation management (new conversation, current thread info)

Suggested Figma screens:
- Login and Register
- Main Chat (default)
- Chat with voice draft and transcription state
- Chat with assistant audio controls
- Document Upload and Indexing
- Document QA active state
- Health and diagnostics
- Conversation history timeline
- Error states (backend offline, invalid model, validation error)

## 5) Model and provider inventory
Configured providers:
- groq
- openai
- anthropic
- gemini

Important implementation note:
- Current active backend provider implementation is Groq only (factory currently instantiates Groq provider)
- Other providers are configured in settings but not fully wired in factory yet

Groq models configured:
- llama-3.3-70b-versatile (default)
- llama-3.1-70b-versatile
- llama-3.1-8b-instant
- llama3-8b-8192
- openai/gpt-oss-120b
- llama-3.2-11b-vision-preview
- llama-4-scout-17b-16e-instruct
- mixtral-8x7b-32768
- gemma2-9b-it
- gemma-7b-it

OpenAI models configured:
- gpt-4o
- gpt-4o-mini (default)
- gpt-4-turbo
- gpt-3.5-turbo

Anthropic models configured:
- claude-3-5-sonnet-20241022
- claude-3-opus-20240229
- claude-3-haiku-20240307 (default)

Gemini models configured:
- gemini-1.5-pro
- gemini-1.5-flash (default)
- gemini-1.0-pro

Audio models/services:
- STT: Groq Whisper (whisper-large-v3-turbo)
- TTS: OpenAI speech model (tts-1-hd)
- Voices: alloy, echo, fable, onyx, nova, shimmer

Embedding setup for RAG:
- Provider: Jina
- Model: jina-embeddings-v2-base-en
- Dimension: 768

## 6) Core API surfaces (for product mapping)
Auth:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

Chat and routing:
- POST /api/v1/chat/send
- GET /api/v1/chat/providers
- GET /api/v1/chat/models

Documents:
- POST /api/v1/chat/upload
- POST /api/v1/chat/delete-namespace

Audio:
- POST /api/v1/chat/speech-to-text
- POST /api/v1/chat/text-to-speech
- GET /api/v1/chat/audio/voices
- GET /api/v1/chat/audio/languages

Health:
- GET /health
- GET /health/details

## 7) UX recommendations for your Figma design
- Keep one persistent left sidebar for navigation and settings
- Keep provider and model selection easy to access near chat controls
- Show active mode badge: Basic Chat, Document QA, or Auto
- Provide clear upload to indexed status transition
- For voice:
  - recording state
  - transcribing state
  - draft inserted state
  - assistant audio play state
- Add graceful error states:
  - backend unavailable
  - auth expired
  - model unavailable fallback
  - no document context found

## 8) Current constraints to reflect in design
- Multi Agent mode exists conceptually, but currently behaves like Basic Chat in graph mapping
- Provider list shows multiple options, but backend factory currently supports Groq provider implementation
- README is currently empty, so this document is the primary project summary for UI planning
