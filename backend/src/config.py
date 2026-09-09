"""
Central place to read configuration (API keys, proxy creds) from a local
.env file (or real environment variables in production). Every other
module should pull settings from here instead of reading os.getenv
directly.

Provider: NVIDIA (build.nvidia.com / NIM), OpenAI-compatible endpoint.
Get a free API key (starts with "nvapi-") at https://build.nvidia.com
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


NVIDIA_API_KEY = _get("NVIDIA_API_KEY")
NVIDIA_BASE_URL = _get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

PROXY_USERNAME = _get("PROXY_USERNAME")
PROXY_PASSWORD = _get("PROXY_PASSWORD")

# Models (centralized so you can swap them in one place).
# Verified working/non-deprecated on build.nvidia.com as of Sept 2026 —
# check https://build.nvidia.com/models before changing these, NVIDIA
# retires older NIMs regularly (e.g. nvidia/llama-3.1-nemotron-70b-instruct
# is already marked Deprecated there).
LLM_MODEL = _get("LLM_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1")
VISION_MODEL = _get("VISION_MODEL", "nvidia/llama-3.1-nemotron-nano-vl-8b-v1")

# Speech-to-text (Riva Parakeet ASR) — hosted over gRPC, not the REST
# endpoint above. function-id identifies which hosted model NVIDIA routes
# your gRPC call to.
RIVA_SERVER = _get("RIVA_SERVER", "grpc.nvcf.nvidia.com:443")
RIVA_ASR_FUNCTION_ID = _get("RIVA_ASR_FUNCTION_ID", "1598d209-5e27-4d3c-8079-4751568b1081")

# Frontend origin(s) allowed to call this API (comma-separated). Used for
# CORS. Defaults cover the Vite dev server.
CORS_ORIGINS = [o.strip() for o in _get(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if o.strip()]
