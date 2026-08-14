"""
Fallback transcription for videos that have no YouTube captions.

Flow: download audio only (yt-dlp) -> send to Groq's hosted Whisper
endpoint -> get text back. Uses the same GROQ_API_KEY you already have
for the summarizer, so there's nothing new to sign up for.

Free tier notes (check Groq's console for current numbers):
- whisper-large-v3-turbo: fastest + cheapest, good enough for study notes
- whisper-large-v3: slightly more accurate, a bit slower
Groq's Whisper endpoint caps file size (~25MB), so long videos are
downloaded as compressed mono audio to stay under that.
"""
import os
import tempfile

from groq import Groq

from src.config import GROQ_API_KEY, WHISPER_MODEL

MAX_FILE_MB = 24  # stay safely under Groq's ~25MB limit


def _download_audio(video_url: str, out_dir: str) -> str:
    """Downloads compressed mono audio for a YouTube video. Requires yt-dlp
    (pip install yt-dlp) and ffmpeg installed on the host."""
    import yt_dlp

    out_template = os.path.join(out_dir, "audio.%(ext)s")
    ydl_opts = {
        "format": "worstaudio/worst",  # smallest file, fine for speech
        "outtmpl": out_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "64",
        }],
        "postprocessor_args": ["-ac", "1"],  # mono
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    audio_path = os.path.join(out_dir, "audio.mp3")
    if not os.path.exists(audio_path):
        raise RuntimeError("Audio download failed — no file produced.")

    size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        raise RuntimeError(
            f"Audio file is {size_mb:.1f}MB, over the {MAX_FILE_MB}MB limit "
            "for free transcription. Try a shorter video."
        )
    return audio_path


def transcribe_video_audio(video_url: str) -> tuple[str | None, str | None]:
    """
    Downloads a video's audio and transcribes it with Groq Whisper.
    Returns (transcript_text, error_message).
    """
    if not GROQ_API_KEY:
        return None, "GROQ_API_KEY is not set — cannot run audio fallback."

    client = Groq(api_key=GROQ_API_KEY)

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            audio_path = _download_audio(video_url, tmp_dir)
        except Exception as e:
            return None, f"Could not download audio: {e}"

        try:
            with open(audio_path, "rb") as f:
                result = client.audio.transcriptions.create(
                    file=f,
                    model=WHISPER_MODEL,
                    response_format="text",
                )
            # SDK returns a plain string when response_format="text"
            text = result if isinstance(result, str) else getattr(result, "text", "")
            if not text.strip():
                return None, "Transcription returned empty text."
            return text.strip(), None
        except Exception as e:
            return None, f"Transcription failed: {e}"
