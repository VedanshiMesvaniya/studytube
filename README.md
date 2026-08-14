# StudyTube

Paste a YouTube link → fetches transcript → LLM summarizes it, pulls key
points, generates Q&A, a quiz, and flashcards. Falls back to Whisper audio
transcription automatically if a video has no captions.

## Project structure

```
studytube/
├── app.py                          # Streamlit UI (entry point)
├── src/
│   ├── config.py                   # reads API keys/models from .env or st.secrets
│   ├── services/
│   │   ├── transcript_service.py   # YouTube captions (primary source)
│   │   ├── audio_transcription.py  # Whisper fallback when no captions exist
│   │   └── llm_service.py          # summary / key points / Q&A / quiz / flashcards
│   └── utils/
│       └── helpers.py              # PDF export, chart generation
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY
```

The audio fallback needs `ffmpeg` on your system (used by `yt-dlp` to
extract audio):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: download from ffmpeg.org and add to PATH

Run it:
```bash
streamlit run app.py
```

## Models used (all free tier)

| Task | Model | Where |
|---|---|---|
| Transcript (primary) | existing YouTube captions | `youtube-transcript-api`, no key needed |
| Transcript (fallback, no captions) | `whisper-large-v3-turbo` | Groq API — free tier |
| Summary / notes / quiz / flashcards | `llama-3.1-8b-instant` | Groq API — free tier |

Get a free Groq API key at https://console.groq.com — one key covers both
the LLM and Whisper calls.
