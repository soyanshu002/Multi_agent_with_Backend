import base64
import html as html_lib
import os
import io
from datetime import datetime

import requests
import streamlit as st

# ══════════════════════════════════════════════════════════
# CONFIG — synced with backend
# ══════════════════════════════════════════════════════════
BASE_URL = "http://localhost:8000"
API_V1   = f"{BASE_URL}/api/v1"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BRANDMARK_PATH = os.path.join(APP_DIR, "assets", "brandmark.svg")
USERMARK_PATH = os.path.join(APP_DIR, "assets", "usermark.svg")

PROVIDERS = ["groq", "openai", "anthropic", "gemini"]
MODELS = {
    "groq":      ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192", "openai/gpt-oss-120b", "mixtral-8x7b-32768", "gemma2-9b-it"],
    "openai":    ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
    "gemini":    ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"],
}
USECASES = {
    "Basic Chatbot": "basic_chat",
    "Document QA":   "document_qa",
    "Multi-Agent":   "multi_agent",
    "Auto":          "auto",
}

st.set_page_config(page_title="Multi-Agent Chatbot", page_icon=BRANDMARK_PATH, layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #05070d;
    --panel: rgba(14, 19, 30, 0.82);
    --panel-strong: rgba(18, 24, 38, 0.92);
    --panel-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(255, 255, 255, 0.07);
    --text: #eef3ff;
    --muted: #8a96b2;
    --accent: #7c6cff;
    --accent-2: #22c1a8;
    --accent-3: #4f8dff;
    --shadow: 0 24px 90px rgba(0, 0, 0, 0.34);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 15% 10%, rgba(124, 108, 255, 0.17), transparent 28%),
        radial-gradient(circle at 85% 18%, rgba(34, 193, 168, 0.12), transparent 24%),
        radial-gradient(circle at 50% 100%, rgba(79, 141, 255, 0.08), transparent 30%),
        linear-gradient(180deg, #05070d 0%, #0a0f17 100%);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(12, 16, 26, 0.98) 0%, rgba(8, 12, 19, 0.98) 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stSidebar"] * {
    color: #dbe3f8;
}

[data-testid="stHeader"], [data-testid="stToolbar"] {
    background: transparent;
}

div[data-testid="stDecoration"] {
    background: transparent;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
}

.app-shell {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.logo-badge {
    width: 2.8rem;
    height: 2.8rem;
    border-radius: 0.95rem;
    overflow: hidden;
    box-shadow: 0 16px 28px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.04);
    flex: 0 0 auto;
}

.logo-badge img {
    width: 100%;
    height: 100%;
    display: block;
}

.app-copy h1 {
    margin: 0;
    font-size: 1.05rem;
    line-height: 1.15;
    color: #f7f9ff;
}

.app-copy p {
    margin: 0.18rem 0 0;
    color: var(--muted);
    font-size: 0.83rem;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}

.title-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    background: rgba(124, 108, 255, 0.14);
    border: 1px solid rgba(124, 108, 255, 0.24);
    color: #c7c1ff;
    font-size: 0.82rem;
    font-weight: 700;
}

.hero {
    border-radius: 24px;
    padding: 1rem 1.15rem;
    background: var(--panel);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    backdrop-filter: blur(16px);
}

.hero h1 {
    margin: 0;
    font-size: 1.35rem;
    line-height: 1.2;
    color: #f4f7ff;
}

.hero p {
    margin: 0.35rem 0 0;
    color: var(--muted);
    font-size: 0.92rem;
}

.panel {
    border-radius: 22px;
    background: var(--panel);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    padding: 1rem;
}

.panel-soft {
    border-radius: 18px;
    background: var(--panel-soft);
    border: 1px solid var(--border);
    padding: 0.9rem 1rem;
}

.section-label {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #7a869f;
    margin-bottom: 0.5rem;
}

.brand {
    font-size: 1.15rem;
    font-weight: 900;
    color: #f2f5ff;
}

.brand-sub {
    font-size: 0.8rem;
    color: #92a0c3;
}

.sidebar-card {
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0.95rem;
}

.sidebar-card .meta-label {
    font-size: 0.7rem;
    color: #7582a2;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}

.sidebar-card .meta-value {
    font-size: 0.95rem;
    font-weight: 800;
    color: #f5f8ff;
    margin-top: 0.15rem;
    word-break: break-word;
}

.nav-stack button {
    border-radius: 14px !important;
}

.bubble-user, .bubble-bot {
    padding: 0.9rem 1rem;
    margin: 0.35rem 0;
    border-radius: 18px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.bubble-user {
    background: linear-gradient(135deg, #7c6cff 0%, #5f52ff 100%);
    color: #fff;
    margin-left: 12%;
    border-top-right-radius: 6px;
}

.bubble-bot {
    background: rgba(255, 255, 255, 0.05);
    color: #edf1ff;
    margin-right: 12%;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-top-left-radius: 6px;
}

.lbl {
    font-size: 0.7rem;
    color: #7f8bab;
    margin-bottom: 0.2rem;
    font-weight: 600;
}

.lbl-r { text-align: right; }

.welcome {
    text-align: center;
    padding: 4rem 1rem 2rem;
    color: #7f8bab;
}

.welcome h2 {
    color: #f3f6ff;
    margin-bottom: 0.4rem;
}

.status-ok { color: #4ade80; font-weight: 700; }
.status-err { color: #fb7185; font-weight: 700; }

.stButton > button {
    background: linear-gradient(135deg, #7c6cff 0%, #5f52ff 100%) !important;
    color: white !important;
    border: 0 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.55rem 0.9rem !important;
    box-shadow: 0 12px 26px rgba(95, 82, 255, 0.22);
}

.stButton > button:hover {
    filter: brightness(1.08);
}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.04) !important;
    color: #eef2ff !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #7382a4 !important;
}

div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 20px;
    padding: 0.85rem;
}

.compact-stat {
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0.8rem 0.95rem;
}

.compact-stat .label {
    font-size: 0.72rem;
    color: #7f8bab;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.compact-stat .value {
    font-size: 0.96rem;
    font-weight: 700;
    color: #f4f7ff;
    margin-top: 0.15rem;
}

.composer-shell {
    border-radius: 24px;
    background: rgba(17, 22, 34, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: var(--shadow);
    padding: 0.9rem 1rem 1rem;
/* Audio Controls */
.stAudio {
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding: 0.8rem !important;
}

.stAudioInput {
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
}

.audio-button {
    border-radius: 12px;
    background: rgba(124, 108, 255, 0.2) !important;
    border: 1px solid rgba(124, 108, 255, 0.3) !important;
    color: #c7c1ff !important;
    font-weight: 600;
}

.audio-button:hover {
    background: rgba(124, 108, 255, 0.3) !important;
}
}

.composer-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
}

.composer-hint {
    margin-top: 0.55rem;
    color: #7a869f;
    font-size: 0.78rem;
}

.quick-prompts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
}

.quick-prompt {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: #dfe5f8;
    border-radius: 16px;
    padding: 0.78rem 0.9rem;
    font-size: 0.9rem;
    line-height: 1.35;
}

.quick-prompt small {
    display: block;
    color: #8b97b2;
    margin-top: 0.2rem;
}

.muted-ghost {
    color: #8c97b2;
}

</style>
""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
defaults = {
    "token":           None,
    "username":        "",
    "messages":        [],
    "conversation_id": f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "namespace":       None,
    "page":            "login",
    "provider":        "groq",
    "model":           "llama-3.3-70b-versatile",
    "usecase_key":     "basic_chat",
    "has_documents":   False,
    "audio_enabled":   True,
    "tts_voice":       "alloy",
    "tts_speed":       1.0,
    "stt_language":    "en",
    "auto_play":       False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.namespace:
    st.session_state.namespace = st.session_state.conversation_id

# ══════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════
def auth_header():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


def svg_data_uri(svg_text: str) -> str:
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


BRANDMARK_SVG = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 128 128\" fill=\"none\">
  <defs>
    <linearGradient id=\"g1\" x1=\"16\" y1=\"16\" x2=\"112\" y2=\"112\" gradientUnits=\"userSpaceOnUse\">
      <stop stop-color=\"#7C6CFF\"/>
      <stop offset=\"0.52\" stop-color=\"#4F8DFF\"/>
      <stop offset=\"1\" stop-color=\"#22C1A8\"/>
    </linearGradient>
    <linearGradient id=\"g2\" x1=\"32\" y1=\"30\" x2=\"98\" y2=\"102\" gradientUnits=\"userSpaceOnUse\">
      <stop stop-color=\"#FFFFFF\" stop-opacity=\"0.96\"/>
      <stop offset=\"1\" stop-color=\"#C7D2FE\" stop-opacity=\"0.92\"/>
    </linearGradient>
  </defs>
  <rect x=\"10\" y=\"10\" width=\"108\" height=\"108\" rx=\"30\" fill=\"url(#g1)\"/>
  <path d=\"M40 44C40 37.373 45.373 32 52 32H76C88.15 32 98 41.85 98 54C98 66.15 88.15 76 76 76H62L48 90V76C41.373 76 36 70.627 36 64V48C36 45.791 37.791 44 40 44Z\" fill=\"url(#g2)\" opacity=\"0.95\"/>
  <circle cx=\"55\" cy=\"55\" r=\"4.5\" fill=\"#0B0F17\"/>
  <circle cx=\"73\" cy=\"55\" r=\"4.5\" fill=\"#0B0F17\"/>
  <path d=\"M55 68C58.5 70.5 62.5 71.5 67 71.5C71.5 71.5 75.5 70.5 79 68\" stroke=\"#0B0F17\" stroke-width=\"4\" stroke-linecap=\"round\"/>
</svg>"""
USERMARK_SVG = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 128 128\" fill=\"none\">
  <defs>
    <linearGradient id=\"g1\" x1=\"16\" y1=\"16\" x2=\"112\" y2=\"112\" gradientUnits=\"userSpaceOnUse\">
      <stop stop-color=\"#22C1A8\"/>
      <stop offset=\"0.5\" stop-color=\"#4F8DFF\"/>
      <stop offset=\"1\" stop-color=\"#7C6CFF\"/>
    </linearGradient>
    <linearGradient id=\"g2\" x1=\"36\" y1=\"38\" x2=\"92\" y2=\"100\" gradientUnits=\"userSpaceOnUse\">
      <stop stop-color=\"#F8FAFF\"/>
      <stop offset=\"1\" stop-color=\"#D6DEFF\"/>
    </linearGradient>
  </defs>
  <rect x=\"10\" y=\"10\" width=\"108\" height=\"108\" rx=\"30\" fill=\"url(#g1)\"/>
  <circle cx=\"64\" cy=\"50\" r=\"20\" fill=\"url(#g2)\"/>
  <path d=\"M34 102C38.5 86.5 50.5 78 64 78C77.5 78 89.5 86.5 94 102\" fill=\"#F8FAFF\" fill-opacity=\"0.96\"/>
  <circle cx=\"57\" cy=\"49\" r=\"3.75\" fill=\"#0B0F17\"/>
  <circle cx=\"71\" cy=\"49\" r=\"3.75\" fill=\"#0B0F17\"/>
  <path d=\"M57 60C60.2 62.4 67.8 62.4 71 60\" stroke=\"#0B0F17\" stroke-width=\"3.5\" stroke-linecap=\"round\"/>
</svg>"""
BRANDMARK_DATA_URI = svg_data_uri(BRANDMARK_SVG)
USERMARK_DATA_URI = svg_data_uri(USERMARK_SVG)

def api_post(path, payload=None, auth=False):
    h = {"Content-Type": "application/json"}
    if auth: h.update(auth_header())
    try:
        return requests.post(f"{API_V1}{path}", json=payload, headers=h, timeout=60)
    except requests.exceptions.ConnectionError:
        return None

def api_get(path, auth=False):
    try:
        return requests.get(f"{API_V1}{path}", headers=auth_header() if auth else {}, timeout=15)
    except requests.exceptions.ConnectionError:
        return None

def get_models_for_provider(provider: str) -> list[str]:
    response = api_get(f"/chat/models?provider={provider}", auth=True)
    if response and response.status_code == 200:
        payload = response.json()
        models = payload.get("models") or []
        if models:
            return models
    return MODELS.get(provider, MODELS["groq"])


def escape_text(value: str) -> str:
    return html_lib.escape(value or "").replace("\n", "<br>")


def render_markdown_block(title: str, body: str, icon_data_uri: str | None = None) -> None:
    icon_html = f'<img src="{icon_data_uri}" style="width:42px;height:42px;border-radius:14px;object-fit:cover;" />' if icon_data_uri else ""
    st.markdown(
        f"""
        <div class='panel'>
            <div class='app-shell' style='margin-bottom:0.8rem;'>
                {icon_html}
                <div class='app-copy'>
                    <h1>{escape_text(title)}</h1>
                    <p>{escape_text(body)}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Audio Functions ────────────────────────────────────
def get_available_voices():
    """Fetch list of available TTS voices from backend."""
    try:
        r = api_get("/chat/audio/voices", auth=True)
        if r and r.status_code == 200:
            return [v["id"] for v in r.json().get("voices", [])]
    except:
        pass
    return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


def get_available_languages():
    """Fetch list of available STT languages from backend."""
    try:
        r = api_get("/chat/audio/languages", auth=True)
        if r and r.status_code == 200:
            langs = r.json().get("languages", [])
            return {lang["code"]: lang["name"] for lang in langs}
    except:
        pass
    return {"en": "English", "es": "Spanish", "fr": "French", "de": "German"}


def transcribe_audio(audio_bytes: bytes, language: str = "en", prompt: str = None) -> str:
    """Send audio to backend for transcription via Groq Whisper."""
    try:
        r = requests.post(
            f"{API_V1}/chat/speech-to-text",
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"language": language, "prompt": prompt or ""},
            headers=auth_header(),
            timeout=60,
        )
        if r and r.status_code == 200:
            result = r.json()
            if result.get("success"):
                return result.get("text", "")
            st.error(f"Transcription failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Transcription error: {e}")
    return ""


def synthesize_speech(text: str, voice: str = "alloy", speed: float = 1.0, language: str = "en") -> bytes | None:
    """Send text to backend for synthesis via OpenAI TTS."""
    try:
        payload = {
            "text": text,
            "voice": voice,
            "speed": speed,
            "language": language,
        }
        r = requests.post(
            f"{API_V1}/chat/text-to-speech",
            json=payload,
            headers=auth_header(),
            timeout=30,
        )
        if r and r.status_code == 200:
            result = r.json()
            if result.get("success"):
                audio_b64 = result.get("audio_base64", "")
                if audio_b64:
                    return base64.b64decode(audio_b64)
            st.error(f"TTS failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"TTS error: {e}")
    return None


def play_audio(audio_bytes: bytes, label: str = "Play response"):
    """Display audio player for audio bytes."""
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", label=label)



def api_upload(path, files, data=None, auth=False):
    try:
        return requests.post(f"{API_V1}{path}", files=files, data=data,
                             headers=auth_header() if auth else {}, timeout=120)
    except requests.exceptions.ConnectionError:
        return None

def go(page):
    st.session_state.page = page
    st.rerun()

def logout():
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.namespace = st.session_state.conversation_id
    st.session_state.has_documents = False
    go("login")

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div class='app-shell'>
                <div class='logo-badge'><img src='{BRANDMARK_DATA_URI}' alt='brandmark' /></div>
                <div class='app-copy'>
                    <h1>Nova Thread</h1>
                    <p>Secure multi-agent workspace</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown(f"<div class='meta-label'>Signed in as</div><div class='meta-value'>{escape_text(st.session_state.username or 'Guest')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='height:0.7rem'></div><div class='meta-label'>Thread</div><div class='meta-value'>{escape_text(st.session_state.conversation_id[-18:])}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Navigate</div>', unsafe_allow_html=True)
        for label, pg in [("Chat","chat"),("Upload Docs","upload"),("Health","health"),("History","history")]:
            if st.button(label, use_container_width=True, key=f"nav_{pg}"):
                go(pg)

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Settings</div>', unsafe_allow_html=True)

        uc_label = st.selectbox("Usecase", list(USECASES.keys()), key="uc_sel")
        st.session_state.usecase_key = USECASES[uc_label]

        prov = st.selectbox("Provider", PROVIDERS,
                            index=PROVIDERS.index(st.session_state.provider), key="prov_sel")
        st.session_state.provider = prov

        model_list  = get_models_for_provider(prov)
        default_idx = model_list.index(st.session_state.model) if st.session_state.model in model_list else 0
        st.session_state.model = st.selectbox("Model", model_list, index=default_idx, key="mdl_sel")

        if st.session_state.usecase_key == "document_qa":
            st.session_state.has_documents = st.checkbox(
                "Has uploaded documents", value=st.session_state.has_documents)

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Audio Settings</div>', unsafe_allow_html=True)

        st.session_state.audio_enabled = st.checkbox(
            "Enable audio", value=st.session_state.audio_enabled, key="audio_toggle")

        if st.session_state.audio_enabled:
            voices = get_available_voices()
            if voices:
                voice_idx = voices.index(st.session_state.tts_voice) if st.session_state.tts_voice in voices else 0
                st.session_state.tts_voice = st.selectbox("Voice", voices, index=voice_idx, key="voice_sel")

            st.session_state.tts_speed = st.slider(
                "Speed", 0.25, 4.0, st.session_state.tts_speed, 0.25, key="speed_slider"
            )

            languages = get_available_languages()
            if languages:
                lang_keys = list(languages.keys())
                lang_idx = lang_keys.index(st.session_state.stt_language) if st.session_state.stt_language in lang_keys else 0
                st.session_state.stt_language = st.selectbox(
                    "Language", lang_keys, index=lang_idx, format_func=lambda x: languages.get(x, x), key="lang_sel"
                )

            st.session_state.auto_play = st.checkbox(
                "Auto-play responses", value=st.session_state.auto_play, key="autoplay_toggle"
            )

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div class='sidebar-card'><div class='meta-label'>Current Thread</div><div class='meta-value'>{escape_text(st.session_state.conversation_id[-18:])}</div></div>",
            unsafe_allow_html=True,
        )
        if st.button("New Conversation", use_container_width=True):
            st.session_state.messages        = []
            st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state.namespace       = st.session_state.conversation_id
            st.session_state.has_documents   = False
            st.rerun()

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            logout()

# ══════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════
def page_login():
    left, center, right = st.columns([0.9, 1.2, 0.9])
    with center:
        render_markdown_block(
            "Nova Thread",
            "ChatGPT-style workspace for chat, document QA, and multi-agent flows.",
            BRANDMARK_DATA_URI,
        )
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign in", "Create account"])

        with tab1:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Access</div>', unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="Enter username", key="li_u")
            p = st.text_input("Password", placeholder="Enter password", type="password", key="li_p")
            if st.button("Continue", use_container_width=True):
                if not u or not p:
                    st.warning("Fill in both fields.")
                else:
                    with st.spinner("Authenticating..."):
                        try:
                            r = requests.post(f"{API_V1}/auth/login",
                                              data={"username": u, "password": p}, timeout=30)
                        except requests.exceptions.ConnectionError:
                            r = None
                    if r is None:
                        st.error("Backend offline.")
                    elif r.status_code == 200:
                        st.session_state.token    = r.json().get("access_token")
                        st.session_state.username = u
                        go("chat")
                    else:
                        try:    detail = r.json().get("detail", "Login failed")
                        except: detail = r.text
                        st.error(detail)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">New account</div>', unsafe_allow_html=True)
            ru  = st.text_input("Username", placeholder="Choose username",  key="rg_u")
            re  = st.text_input("Email",    placeholder="your@email.com",   key="rg_e")
            rp  = st.text_input("Password", placeholder="Choose password",  type="password", key="rg_p")
            rp2 = st.text_input("Confirm",  placeholder="Repeat password",  type="password", key="rg_p2")
            if st.button("Create account", use_container_width=True):
                if not ru or not re or not rp:
                    st.warning("Fill in all fields.")
                elif rp != rp2:
                    st.error("Passwords don't match.")
                else:
                    with st.spinner("Creating account..."):
                        r = api_post("/auth/register", {"username": ru, "email": re, "password": rp})
                    if r is None:
                        st.error("Backend offline.")
                    elif r.status_code in (200, 201):
                        st.success("Account created. Please sign in.")
                    else:
                        st.error(f"{r.json().get('detail', 'Registration failed')}")
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE: CHAT  ← 100% synced with ChatRequest schema
# ══════════════════════════════════════════════════════════
def page_chat():
    sidebar()
    uc   = st.session_state.usecase_key
    prov = st.session_state.provider
    mdl  = st.session_state.model

    uc_label = [k for k, v in USECASES.items() if v == uc][0]
    st.markdown(
        f"""
        <div class='topbar'>
            <div class='hero' style='flex:1;'>
                <div class='app-shell' style='margin-bottom:0.7rem;'>
                    <div class='logo-badge'><img src='{BRANDMARK_DATA_URI}' alt='brandmark' /></div>
                    <div class='app-copy'>
                        <h1>{escape_text(uc_label)}</h1>
                        <p>{escape_text(prov)} · {escape_text(mdl)} · {escape_text(st.session_state.conversation_id[-16:])}</p>
                    </div>
                </div>
            </div>
            <div class='title-chip'>● {escape_text(uc.replace('_', ' ').title())}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="welcome">
                <h2>Ask anything</h2>
                <p>Your responses appear here with branded assistant and user avatars.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            role = msg.get("role")
            content = msg.get("content", "")
            meta = msg.get("meta")
            avatar_path = USERMARK_PATH if role == "user" else BRANDMARK_PATH
            with st.chat_message(role, avatar=avatar_path):
                st.markdown(escape_text(content), unsafe_allow_html=True)

                if role == "assistant" and st.session_state.audio_enabled:
                    if st.button("Play audio", key=f"play_audio_{id(msg)}"):
                        with st.spinner("Generating audio..."):
                            audio_bytes = synthesize_speech(
                                content,
                                voice=st.session_state.tts_voice,
                                speed=st.session_state.tts_speed,
                                language=st.session_state.stt_language,
                            )
                            if audio_bytes:
                                play_audio(audio_bytes, label="Response audio")
                
                if meta:
                    with st.expander("Metadata"):
                        st.json(meta)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="composer-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class='quick-prompts' style='margin-bottom:0.75rem;'>
            <div class='quick-prompt'>Summarize the current project<small>Quick overview of repository status</small></div>
            <div class='quick-prompt'>Explain how document QA works<small>Ask about Pinecone and retrieval flow</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.audio_enabled:
        st.markdown("<div style='margin-bottom:0.8rem;'>", unsafe_allow_html=True)
        st.markdown('<div class="section-label" style="margin-bottom:0.5rem;">Voice Input</div>', unsafe_allow_html=True)

        audio_col1, audio_col2 = st.columns([1, 0.3])
        with audio_col1:
            audio_file = st.audio_input(
                "Click to record message",
                label_visibility="collapsed",
                key="audio_recorder",
            )
            audio_bytes = audio_file.getvalue() if audio_file else None

        with audio_col2:
            if audio_bytes and st.button("Transcribe", use_container_width=True, key="transcribe_btn"):
                with st.spinner("Transcribing..."):
                    transcribed_text = transcribe_audio(audio_bytes, language=st.session_state.stt_language)
                    if transcribed_text:
                        st.session_state.voice_input_text = transcribed_text
                        st.success(f"Transcribed: {transcribed_text[:50]}...")

        st.markdown("</div>", unsafe_allow_html=True)

    voice_text = st.session_state.get("voice_input_text", "")
    prompt = st.chat_input("Message Nova...")
    if voice_text:
        st.caption(f"Voice draft: {voice_text}")
        if st.button("Use voice draft", key="use_voice_draft"):
            prompt = voice_text
            st.session_state.voice_input_text = ""

    st.markdown('<div class="composer-hint">Enter to send. Voice input requires audio to be enabled.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt and prompt.strip():
        st.session_state.messages.append({"role": "user", "content": prompt})

        payload = {
            "messages":        [{"role": "user", "content": prompt}],
            "provider":        prov,
            "model":           mdl,
            "stream":          False,
            "conversation_id": st.session_state.conversation_id,
            "usecase":         uc,
            "has_documents":   st.session_state.has_documents,
            "namespace":       st.session_state.namespace,
        }

        with st.spinner("Thinking..."):
            r = api_post("/chat/send", payload, auth=True)

        if r is None:
            reply, meta = "Cannot reach backend.", {}
        elif r.status_code == 200:
            d     = r.json()
            reply = (d.get("final_response") or d.get("response") or d.get("message") or str(d))
            meta  = {k: v for k, v in d.items()
                     if k not in ("final_response","response","message","messages")}
        elif r.status_code == 401:
            st.error("Session expired."); logout(); return
        elif r.status_code == 422:
            st.error(f"Validation error: {r.json()}"); return
        else:
            reply, meta = f"Error {r.status_code}: {r.text}", {}

        st.session_state.messages.append({"role": "assistant", "content": reply, "meta": meta})

        if st.session_state.audio_enabled and st.session_state.auto_play and reply:
            with st.spinner("Generating audio response..."):
                audio_bytes = synthesize_speech(
                    reply,
                    voice=st.session_state.tts_voice,
                    speed=st.session_state.tts_speed,
                    language=st.session_state.stt_language,
                )
                if audio_bytes:
                    play_audio(audio_bytes, label="Auto-play audio")
        
        st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE: UPLOAD
# ══════════════════════════════════════════════════════════
def page_upload():
    sidebar()
    render_markdown_block(
        "Document QA",
        "Upload files, index them into Pinecone, and answer against the private knowledge base.",
        BRANDMARK_DATA_URI,
    )
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Upload</div>', unsafe_allow_html=True)
        st.markdown("### Upload a File")
        ns = st.text_input("Namespace", value=st.session_state.namespace)
        st.session_state.namespace = ns.strip() or st.session_state.conversation_id
        uploaded = st.file_uploader("Choose file", type=["pdf","docx","txt","md"])

        if uploaded:
            st.markdown(f"<div class='sidebar-card'><div class='meta-label'>File</div><div class='meta-value'>{escape_text(uploaded.name)}</div></div>", unsafe_allow_html=True)
            if st.button("Upload and index", use_container_width=True):
                if not st.session_state.namespace:
                    st.warning("Enter a namespace.")
                else:
                    with st.spinner(f"Indexing {uploaded.name}..."):
                        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                        r = api_upload("/chat/upload", files=files, data={"namespace": st.session_state.namespace}, auth=True)
                    if r is None:
                        st.error("Backend offline.")
                    elif r.status_code == 200:
                        d = r.json()
                        st.success(f"Indexed {d.get('chunks','?')} chunks")
                        st.session_state.has_documents = True
                        st.session_state.usecase_key = "document_qa"
                        st.session_state.page = "chat"
                        st.rerun()
                    else:
                        st.error(r.text)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Workflow</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="panel-soft">
        <b>1. Upload file</b><br><span style="color:#91a0c2;font-size:0.9rem">PDF, DOCX, TXT, and MD are supported.</span><br><br>
        <b>2. Select Document QA</b><br><span style="color:#91a0c2;font-size:0.9rem">The sidebar can switch the active routing mode.</span><br><br>
        <b>3. Ask questions</b><br><span style="color:#91a0c2;font-size:0.9rem">Responses come from the indexed Pinecone namespace.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        st.markdown("### Delete Namespace")
        del_ns = st.text_input("Namespace to delete")
        if st.button("Delete all docs", use_container_width=True) and del_ns:
            r = api_post("/chat/delete-namespace", {"namespace": del_ns}, auth=True)
            if r and r.status_code == 200:
                st.success(f"Deleted {del_ns}")
            else:
                st.error("Delete failed.")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE: HEALTH
# ══════════════════════════════════════════════════════════
def page_health():
    sidebar()
    render_markdown_block(
        "System Health",
        "Live checks for backend, Redis, auth state, and current model configuration.",
        BRANDMARK_DATA_URI,
    )
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    if st.button("Refresh"):
        st.rerun()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Backend</div>', unsafe_allow_html=True)
        st.markdown("### API")
        r = api_get("/health")
        if r and r.status_code == 200:
            st.markdown('<span class="status-ok">● ONLINE</span>', unsafe_allow_html=True)
            st.json(r.json())
        else:
            st.markdown('<span class="status-err">● OFFLINE</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Redis</div>', unsafe_allow_html=True)
        st.markdown("### Service")
        r = api_get("/health/details")
        if r and r.status_code == 200:
            details = r.json()
            redis_status = (details.get("services", {}) or {}).get("redis", "unknown")
            if isinstance(redis_status, str) and redis_status == "ok":
                st.markdown('<span class="status-ok">● CONNECTED</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-err">● DISCONNECTED</span>', unsafe_allow_html=True)
            st.json(details)
        else:
            st.markdown('<span class="status-err">● DISCONNECTED</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)
        st.markdown("### Auth Token")
        if st.session_state.token:
            st.markdown('<span class="status-ok">● ACTIVE</span>', unsafe_allow_html=True)
            st.code(st.session_state.token[:50] + "...", language=None)
        else:
            st.markdown('<span class="status-err">● NONE</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Active Config</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown(f"<div class='compact-stat'><div class='label'>Provider</div><div class='value'>{escape_text(st.session_state.provider)}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='height:0.5rem'></div><div class='compact-stat'><div class='label'>Model</div><div class='value'>{escape_text(st.session_state.model)}</div></div>", unsafe_allow_html=True)
    with cb:
        st.markdown(f"<div class='compact-stat'><div class='label'>Usecase</div><div class='value'>{escape_text(st.session_state.usecase_key)}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='height:0.5rem'></div><div class='compact-stat'><div class='label'>Conversation</div><div class='value'>{escape_text(st.session_state.conversation_id[-16:])}</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Models</div>', unsafe_allow_html=True)
    st.markdown("### Available Models")
    check_prov = st.selectbox("Provider", PROVIDERS, key="health_prov")
    if st.button("Fetch models"):
        models = get_models_for_provider(check_prov)
        st.json({"provider": check_prov, "models": models})
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════
def page_history():
    sidebar()
    render_markdown_block(
        "Chat History",
        f"Conversation timeline for {st.session_state.conversation_id[-18:]}",
        BRANDMARK_DATA_URI,
    )
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if st.session_state.messages:
        for i, msg in enumerate(st.session_state.messages):
            icon = "🧑" if msg["role"] == "user" else "🤖"
            with st.expander(f"{icon} {msg['role'].capitalize()} #{i+1}"):
                st.write(msg["content"])
                if msg.get("meta"):
                    st.json(msg["meta"])
    else:
        st.info("No messages in current conversation.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Fetch from backend", use_container_width=True):
            r = api_get(f"/chat/history/{st.session_state.conversation_id}", auth=True)
            if r and r.status_code == 200:
                st.json(r.json()) if r.json() else st.info("No history stored.")
            else:
                st.warning("Could not fetch history.")
    with col2:
        if st.button("Clear messages", use_container_width=True):
            st.session_state.messages = []
            st.success("Cleared!")
            st.rerun()
        if st.button("New conversation", use_container_width=True):
            st.session_state.messages        = []
            st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.session_state.namespace       = st.session_state.conversation_id
            st.session_state.has_documents   = False
            st.rerun()

# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
if not st.session_state.token:
    st.session_state.page = "login"

page = st.session_state.page
if   page == "login":   page_login()
elif page == "chat":    page_chat()
elif page == "upload":  page_upload()
elif page == "health":  page_health()
elif page == "history": page_history()
else: go("login")