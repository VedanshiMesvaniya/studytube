"""
StudyTube API — FastAPI backend.

This replaces the old Streamlit UI (app.py). All the notes-generation
logic (transcript fetching, Whisper/vision fallback, Groq LLM calls,
PDF export) lives untouched in src/services and src/utils — this file
just exposes it over HTTP so the React frontend (../frontend) can call
it.

Run with:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import io

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.config import CORS_ORIGINS
from src.services.transcript_service import SUPPORTED_LANGUAGES
from src.services.understanding_service import get_full_understanding
from src.services.llm_service import get_all_notes, parse_all_notes, get_visuals
from src.utils.helpers import truncate_text, generate_pdf
from src.utils.parsers import parse_quiz, parse_flashcards

app = FastAPI(title="StudyTube API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------- schemas --
class NotesRequest(BaseModel):
    url: str
    language: str = "Auto Detect"


class PdfRequest(BaseModel):
    url: str
    summary: str = ""
    keypoints: str = ""
    qa: str = ""
    quiz_text: str = ""
    flashcards_text: str = ""


# ------------------------------------------------------------------ routes --
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/languages")
def languages():
    """List of languages the transcript step can request captions in."""
    return {"languages": list(SUPPORTED_LANGUAGES.keys())}


@app.post("/api/notes")
def generate_notes(payload: NotesRequest):
    url = payload.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="Please paste a YouTube URL to get started.")
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(status_code=400, detail="That doesn't look like a YouTube link. Please check and try again.")

    lang_code = SUPPORTED_LANGUAGES.get(payload.language, None)

    text, status = get_full_understanding(url, language=lang_code)
    if not text:
        raise HTTPException(status_code=422, detail=status or "Could not extract anything usable from this video.")

    word_count = len(text.split())
    _, was_truncated = truncate_text(text)

    raw_notes, num_chunks = get_all_notes(text)
    notes = parse_all_notes(raw_notes)

    visuals = get_visuals(text)

    return {
        "url": url,
        "status": status,
        "word_count": word_count,
        "was_truncated": was_truncated,
        "summary": notes["summary"],
        "keypoints": notes["keypoints"],
        "qa": notes["qa"],
        "quiz_text": notes["quiz"],
        "flashcards_text": notes["flashcards"],
        "quiz_questions": parse_quiz(notes["quiz"]),
        "flashcard_pairs": parse_flashcards(notes["flashcards"]),
        "visuals": visuals,
    }


@app.post("/api/pdf")
def download_pdf(payload: PdfRequest):
    pdf_bytes = generate_pdf(
        payload.url,
        payload.summary,
        payload.keypoints,
        payload.qa,
        payload.quiz_text,
        payload.flashcards_text,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=studytube_notes.pdf"},
    )
