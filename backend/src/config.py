"""
Central place to read configuration (API keys, proxy creds) from a local
.env file (or real environment variables in production). Every other
module should pull settings from here instead of reading os.getenv
directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


GROQ_API_KEY = _get("GROQ_API_KEY")
PROXY_USERNAME = _get("PROXY_USERNAME")
PROXY_PASSWORD = _get("PROXY_PASSWORD")

# Models (centralized so you can swap them in one place)
LLM_MODEL = _get("LLM_MODEL", "llama-3.1-8b-instant")
WHISPER_MODEL = _get("WHISPER_MODEL", "whisper-large-v3-turbo")

# Frontend origin(s) allowed to call this API (comma-separated). Used for
# CORS. Defaults cover the Vite dev server.
CORS_ORIGINS = [o.strip() for o in _get(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if o.strip()]
