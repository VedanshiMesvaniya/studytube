import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import os

SUPPORTED_LANGUAGES = {
    'Auto Detect': None,
    'English': 'en',
    'Hindi': 'hi',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Chinese (Simplified)': 'zh-Hans',
    'Arabic': 'ar',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Italian': 'it',
}

def get_ytt():
    try:
        import streamlit as st
        proxy_user = st.secrets.get("PROXY_USERNAME", "")
        proxy_pass = st.secrets.get("PROXY_PASSWORD", "")
    except Exception:
        proxy_user = os.getenv("PROXY_USERNAME", "")
        proxy_pass = os.getenv("PROXY_PASSWORD", "")

    if proxy_user and proxy_pass:
        proxy_config = WebshareProxyConfig(
            proxy_username=proxy_user,
            proxy_password=proxy_pass,
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()

def extract_video_id(url):
    url = url.strip().strip('_').strip('*').strip('`').strip()
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
        r"live/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(url, language=None):
    url = url.strip().strip('_').strip('*').strip('`').strip()
    video_id = extract_video_id(url)

    if not video_id:
        return None, "Invalid YouTube URL. Please check and try again."

    try:
        ytt = get_ytt()
        transcript_list = ytt.list(video_id)

        if language:
            transcript_data = None

            for t in transcript_list:
                if t.language_code == language and not t.is_generated:
                    transcript_data = t.fetch()
                    break

            if transcript_data is None:
                for t in transcript_list:
                    if t.language_code == language:
                        transcript_data = t.fetch()
                        break

            if transcript_data is None:
                for t in transcript_list:
                    if t.language_code.startswith(language):
                        transcript_data = t.fetch()
                        break

            if transcript_data is None:
                available = [t.language_code for t in transcript_list]
                fallback = list(transcript_list)[0]
                transcript_data = fallback.fetch()
                lang_name = [k for k, v in SUPPORTED_LANGUAGES.items() if v == language]
                lang_label = lang_name[0] if lang_name else language
                full_text = " ".join([entry.text for entry in transcript_data])
                return full_text, f"No {lang_label} transcript found. Using: {fallback.language}. Available: {', '.join(available)}"
        else:
            transcript_data = ytt.fetch(video_id)

        full_text = " ".join([entry.text for entry in transcript_data])
        return full_text, None

    except TranscriptsDisabled:
        return None, "This video has transcripts disabled."
    except NoTranscriptFound:
        return None, "No transcript found. Try a different language or check if the video has captions."
    except Exception as e:
        return None, f"Something went wrong: {str(e)}"
```

---

## Step 3 — Add proxy secrets to Streamlit

Go to your app → **Settings** → **Secrets** → add:
```
GROQ_API_KEY = "gsk_your_key_here"
PROXY_USERNAME = "your_webshare_username"
PROXY_PASSWORD = "your_webshare_password"
