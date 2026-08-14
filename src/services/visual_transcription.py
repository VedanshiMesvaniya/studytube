"""
Visual understanding for videos with little or no spoken audio
(silent screen recordings, code walkthroughs, slide decks with music
only, etc).

Flow: download a low-res copy of the video (yt-dlp) -> pull one frame
every FRAME_INTERVAL_SEC seconds (ffmpeg) -> send each frame to Groq's
free vision model (Llama 4 Scout) and ask it to read/describe on-screen
text, code, diagrams -> stitch the per-frame notes into a timestamped
"visual transcript" that can be fed into the same notes pipeline as a
normal transcript.

Uses the same GROQ_API_KEY as the rest of the app.
"""
import base64
import os
import subprocess
import tempfile

from groq import Groq

from src.config import GROQ_API_KEY

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
FRAME_INTERVAL_SEC = 20      # take a frame every 20s of video
MAX_FRAMES = 15              # hard cap so this stays fast + free-tier friendly

FRAME_PROMPT = (
    "This is a frame from a screen-recording / tutorial video with little "
    "or no narration. In 2-3 sentences, describe exactly what is on screen: "
    "read out any visible text, code, titles, diagrams, or UI actions. "
    "If nothing meaningful is visible (e.g. a blank transition), say 'no "
    "new content'. Do not add commentary or guesses beyond what's visible."
)


def _download_low_res_video(video_url: str, out_dir: str) -> str:
    import yt_dlp

    out_template = os.path.join(out_dir, "video.%(ext)s")
    ydl_opts = {
        # smallest mp4 stream available — we only need readable frames,
        # not full quality
        "format": "worst[ext=mp4]/worst",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    for f in os.listdir(out_dir):
        if f.startswith("video."):
            return os.path.join(out_dir, f)
    raise RuntimeError("Video download failed — no file produced.")


def _extract_frames(video_path: str, out_dir: str) -> list[tuple[int, str]]:
    """Returns a list of (timestamp_seconds, frame_path), capped at MAX_FRAMES."""
    frame_pattern = os.path.join(out_dir, "frame_%04d.jpg")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps=1/{FRAME_INTERVAL_SEC}",
        "-vsync", "vfr",
        "-q:v", "4",
        frame_pattern,
        "-y", "-loglevel", "error",
    ]
    subprocess.run(cmd, check=True)

    frames = sorted(f for f in os.listdir(out_dir) if f.startswith("frame_"))
    frames = frames[:MAX_FRAMES]
    return [
        (i * FRAME_INTERVAL_SEC, os.path.join(out_dir, f))
        for i, f in enumerate(frames)
    ]


def _describe_frame(client: Groq, frame_path: str) -> str:
    with open(frame_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": FRAME_PROMPT},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}"
                }},
            ],
        }],
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def _format_timestamp(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"


def get_visual_transcript(video_url: str) -> tuple[str | None, str | None]:
    """
    Extracts frames from the video and builds a timestamped description
    of on-screen content. Returns (visual_transcript_text, error_message).
    """
    if not GROQ_API_KEY:
        return None, "GROQ_API_KEY is not set — cannot run visual understanding."

    client = Groq(api_key=GROQ_API_KEY)

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            video_path = _download_low_res_video(video_url, tmp_dir)
        except Exception as e:
            return None, f"Could not download video: {e}"

        try:
            frames = _extract_frames(video_path, tmp_dir)
        except Exception as e:
            return None, f"Could not extract frames: {e}"

        if not frames:
            return None, "No frames could be extracted from this video."

        lines = []
        for ts, frame_path in frames:
            try:
                description = _describe_frame(client, frame_path)
            except Exception as e:
                description = f"(frame analysis failed: {e})"
            if description and "no new content" not in description.lower():
                lines.append(f"[{_format_timestamp(ts)}] {description}")

        if not lines:
            return None, "No meaningful visual content was detected."

        return "\n".join(lines), None
