"""
Central place to read configuration (API keys, proxy creds) from either
Streamlit secrets (when deployed on Streamlit Cloud) or a local .env file.
Every other module should pull settings from here instead of reading
os.getenv / st.secrets directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


GROQ_API_KEY = _get("GROQ_API_KEY")
PROXY_USERNAME = _get("PROXY_USERNAME")
PROXY_PASSWORD = _get("PROXY_PASSWORD")

# Models (centralized so you can swap them in one place)
LLM_MODEL = _get("LLM_MODEL", "llama-3.1-8b-instant")
WHISPER_MODEL = _get("WHISPER_MODEL", "whisper-large-v3-turbo")
