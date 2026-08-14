# Architecture

## Overview

StudyTube is code-split into a frontend and a backend, but by default they
run as a **single process on a single port**: `npm run build` produces
static files (`frontend/dist`), and the FastAPI backend serves both those
static files *and* the `/api/*` JSON endpoints from the same `uvicorn`
process.

```
                 http://localhost:8000
        ┌───────────────────────────────────┐
        │        backend (FastAPI)          │
        │                                    │
        │  /api/health, /api/languages,      │
        │  /api/notes, /api/pdf   ─────┐     │
        │                              │     │
        │  /  (everything else)  ──▶ frontend/dist  │
        │     (StaticFiles mount, built by Vite)     │
        └───────────────┬─────────────┴─────┘
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
  YouTube captions   Groq (Whisper,   Groq (LLM,
  (youtube-           vision model)   notes/quiz/
  transcript-api)     via yt-dlp +    flashcards/
                       ffmpeg          visuals JSON)
```

The code itself is still cleanly split — `frontend/` (React/Vite, browser
code) and `backend/` (FastAPI, Python) are independent projects with their
own dependencies — but at runtime `backend/main.py` mounts
`frontend/dist` as static files (see "Serving the frontend" below), so
there's exactly one server to start and one port to open. This is a clean
split rather than a monolith source tree because the heavy lifting
(yt-dlp, ffmpeg, the Groq SDK, PDF generation) is Python-specific and was
already written and working — porting it to JavaScript would mean
rewriting battle-tested logic for no benefit. Wrapping it in a small
FastAPI layer instead let the whole `src/services` and `src/utils` tree
move over almost untouched, while the *deployed* app is still one process.

An optional two-process dev workflow (`npm run dev` on :5173 talking to
`uvicorn --reload` on :8000) is still available for hot-reloading during
active frontend development — see README.md section 5 — but it's opt-in,
not the default.

---

## Backend (`backend/`)

**Framework:** FastAPI + Uvicorn.

**Responsibility:** own all external calls (YouTube, Groq, ffmpeg/yt-dlp)
and all business logic. The frontend never talks to Groq or YouTube
directly — it only ever calls this API.

### Request pipeline (`POST /api/notes`)

1. **`transcript_service.get_transcript`** — tries to fetch existing
   YouTube captions in the requested language (or auto-detect). This is
   free and instant when available.
2. If captions are missing or too short (`understanding_service`, threshold
   `MIN_WORDS_CONSIDERED_SUBSTANTIAL = 40`), falls back to
   **`audio_transcription.transcribe_video_audio`** — downloads compressed
   mono audio with `yt-dlp` and transcribes it with Groq's hosted Whisper.
3. If the audio transcript is *also* thin (silent/visual-heavy videos —
   screen recordings, slide decks with only music), falls back to
   **`visual_transcription.get_visual_transcript`** — downloads a low-res
   copy of the video, extracts one frame every 20 seconds (`ffmpeg`, capped
   at 15 frames), and asks Groq's vision model to describe on-screen
   text/code/diagrams for each frame, producing a timestamped "visual
   transcript."
4. Steps 2 and 3 can combine (e.g. a mostly-silent coding video with
   occasional narration gets both the spoken transcript and the visual
   descriptions merged).
5. Whatever text results is compressed if very long
   (`llm_service.compress_transcript` — chunks + per-chunk summarization,
   only kicks in above ~2000 words) and sent to the Groq LLM **once** with a
   single structured prompt that returns summary, key points, Q&A, quiz,
   and flashcards together (`get_all_notes` / `parse_all_notes`), then a
   **second** call asks the LLM to return JSON describing any
   flowchart/chart/mind-map worth visualizing (`get_visuals`).
6. Raw quiz/flashcard text is parsed into structured JSON
   (`utils/parsers.py`) so the frontend doesn't have to parse text — quiz
   questions arrive as `{question, options: {A,B,C,D}, answer}` and
   flashcards as `{front, back}` pairs.
7. Everything is returned as one JSON object.

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness check |
| GET | `/api/languages` | List of caption languages the UI can offer |
| POST | `/api/notes` | Full pipeline: `{url, language}` → summary/keypoints/qa/quiz/flashcards/visuals |
| POST | `/api/pdf` | Renders the same five text sections into a downloadable PDF |

Auto-generated interactive docs are available at `/docs` (Swagger UI) and
`/redoc` while the server is running — useful for testing endpoints without
the frontend.

### Serving the frontend

At the bottom of `backend/main.py`, after every `/api/*` route has already
been registered, the app does:

```python
app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
```

Starlette (which FastAPI is built on) matches routes in registration
order, so any request to `/api/...` is already handled by the routes above
before the router ever reaches this mount — the mount only ever catches
requests for the UI (`/`, `/assets/...`, etc.), never the API. `html=True`
makes it serve `index.html` for `/` automatically. If `frontend/dist`
doesn't exist yet (i.e. `npm run build` hasn't been run), the app falls
back to a small JSON message at `/` telling you to build it, instead of
crashing on startup.

Because the browser loads the page from the same origin
(`http://localhost:8000`) that serves the API, the frontend's API client
(`frontend/src/api/client.js`) defaults to relative URLs in a production
build — no CORS, no separate origin to configure. It only falls back to
`http://localhost:8000` explicitly when running under Vite's own dev
server (`import.meta.env.DEV`), which is a different origin (`:5173`) by
nature.

### Why charts moved out of the backend

The original Streamlit app rendered charts with `matplotlib` server-side
and shipped a PNG. The React frontend renders charts with **Recharts**
instead, directly in the browser, from the same `chart_labels` /
`chart_values` / `chart_type` JSON the LLM already returns in the
`/api/notes` response. This means no image round-trip, charts scale/respond
properly, and `matplotlib` is no longer a backend dependency at all.
Flowcharts and mind-maps are rendered client-side too, with **Mermaid.js**,
from the same `flowchart_mermaid` / `mindmap_nodes` strings the LLM already
produced — the backend never needed to render them, so nothing changed
there except the JSON was always the real source of truth.

---

## Frontend (`frontend/`)

**Framework:** React 18 + Vite. No router — it's a single view (mirrors the
original single-page Streamlit app), so a router would add complexity
without benefit.

### State (all in `App.jsx`, lifted only as far as needed)

- `theme` — `'academic-dark' | 'academic-light'`, persisted to
  `localStorage`, applied via `data-theme` on `<html>`.
- `url`, `language` — controlled form inputs.
- `loading`, `error`, `statusMessage` — request lifecycle for the
  `/api/notes` call.
- `results` — the JSON payload from `/api/notes`, passed down to
  `ResultsPanel`.

Quiz answer state and flashcard flip state live inside `QuizTab.jsx` /
`FlashcardsTab.jsx` respectively — they don't need to be visible to
anything else, so they're not lifted to `App.jsx`.

### Component tree

```
App
├── ThemeToggle
├── Hero
├── SearchForm
└── ResultsPanel               (shown once results !== null)
    ├── tab navigation (Summary / Key Points / Q&A / Quiz / Flashcards / Visuals)
    ├── QuizTab                (own answer/submitted state)
    ├── FlashcardsTab          (own flipped-card state)
    ├── VisualsTab
    │   ├── MermaidDiagram     (flowchart)
    │   ├── ChartBlock         (Recharts bar/line/pie)
    │   └── MermaidDiagram     (mind-map)
    └── "Download Notes as PDF" button → POST /api/pdf → triggers browser download
```

### Styling

No CSS framework — plain CSS with variables, matching how the original
Streamlit app was styled (utility classes like `.hero-title`,
`.section-badge`, `.quiz-q`, `.fc`/`.fc-inner`/`.fc-front`/`.fc-back` for
flip cards, etc., carried over 1:1 in spirit).

- `styles/themes.css` — the two theme variable sets (`academic-dark`,
  `academic-light`), applied via `:root[data-theme='...']`.
- `styles/base.css` — resets, font loading, scrollbar theming.
- `styles/App.css` — every component's actual layout/appearance, built
  entirely from the theme variables (no hard-coded colors), so switching
  themes never requires touching component CSS.

### API client (`api/client.js`)

Thin `axios` wrapper around the three backend endpoints
(`fetchLanguages`, `generateNotes`, `downloadNotesPdf`) plus
`extractErrorMessage` for turning FastAPI's `{"detail": "..."}` error
shape into a plain string the UI can show directly. Base URL comes from
`VITE_API_BASE_URL` (falls back to `http://localhost:8000`), so pointing
the frontend at a deployed backend is a one-line env change, not a code
change.

---

## Data contracts

### `POST /api/notes` request

```json
{ "url": "https://youtube.com/watch?v=...", "language": "Auto Detect" }
```

### `POST /api/notes` response

```json
{
  "url": "...",
  "status": "Used existing YouTube captions.",
  "word_count": 1532,
  "was_truncated": false,
  "summary": "...",
  "keypoints": "- point one\n- point two...",
  "qa": "Q: ...\nA: ...",
  "quiz_text": "Q1: ...\nA) ...\nAnswer: A",
  "flashcards_text": "FRONT: ...\nBACK: ...",
  "quiz_questions": [
    { "question": "...", "options": { "A": "...", "B": "...", "C": "...", "D": "..." }, "answer": "A" }
  ],
  "flashcard_pairs": [ { "front": "...", "back": "..." } ],
  "visuals": {
    "has_flowchart": true, "flowchart_title": "...", "flowchart_mermaid": "flowchart TD\n...",
    "has_chart": true, "chart_type": "bar", "chart_title": "...", "chart_labels": [...], "chart_values": [...],
    "has_mindmap": true, "mindmap_title": "...", "mindmap_nodes": ["...", "..."]
  }
}
```

### `POST /api/pdf` request

```json
{
  "url": "...", "summary": "...", "keypoints": "...",
  "qa": "...", "quiz_text": "...", "flashcards_text": "..."
}
```
Response: `application/pdf` binary stream (`Content-Disposition: attachment`).

---

## Things deliberately kept identical to the original app

- Feature set: transcript/audio/visual understanding cascade, summary, key
  points, Q&A, scored quiz, flip flashcards, auto-detected
  visuals, PDF export.
- Model choices and prompts (`llm_service.py` is unchanged).
- Fallback thresholds (`MIN_WORDS_CONSIDERED_SUBSTANTIAL`, frame interval,
  max frames, max file size for audio).
- Config resolution order (`.env` file, `CORS_ORIGINS`/models overridable
  without code changes).

## Things that changed on purpose

- Streamlit UI → React SPA talking to a FastAPI JSON API.
- Two fixed themes (`academic-dark` / `academic-light`) replace the old
  purple/violet dark-light-system three-way toggle.
- Charts/diagrams render client-side (Recharts + Mermaid.js) instead of
  server-side PNGs (matplotlib) — same underlying LLM-detected data, just
  rendered where it's cheaper and more interactive to render.
- Quiz/flashcard text parsing moved from `app.py` into
  `backend/src/utils/parsers.py` so the API can return structured JSON
  instead of the frontend having to parse raw LLM text.
