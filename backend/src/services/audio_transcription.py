"""
Fallback transcription for videos that have no YouTube captions.

Flow: download audio only (yt-dlp) -> convert to 16kHz mono WAV (ffmpeg,
required by Riva) -> send to NVIDIA's hosted Parakeet ASR over gRPC
-> get text back.

Provider: NVIDIA Riva ASR (Parakeet), hosted free via NVCF on
grpc.nvcf.nvidia.com. This is NOT the same REST endpoint used for chat/
vision (integrate.api.nvidia.com) — Riva speech models are served over
gRPC, so this uses the official `nvidia-riva-client` package instead of
the OpenAI SDK.

Get a free API key (starts with "nvapi-") at https://build.nvidia.com
"""
import os
import subprocess
import tempfile

from src.config import NVIDIA_API_KEY, RIVA_SERVER, RIVA_ASR_FUNCTION_ID


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
            "preferredcodec": "wav",
            "preferredquality": "64",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    audio_path = os.path.join(out_dir, "audio.wav")
    if not os.path.exists(audio_path):
        raise RuntimeError("Audio download failed — no file produced.")
    return audio_path


def _to_riva_wav(src_path: str, out_dir: str) -> str:
    """Riva expects 16-bit mono LINEAR_PCM WAV at 16kHz — re-encode to be safe."""
    out_path = os.path.join(out_dir, "audio_16k_mono.wav")
    cmd = [
        "ffmpeg", "-i", src_path,
        "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
        out_path, "-y", "-loglevel", "error",
    ]
    subprocess.run(cmd, check=True)
    return out_path


def transcribe_video_audio(video_url: str) -> tuple[str | None, str | None]:
    """
    Downloads a video's audio and transcribes it with NVIDIA's hosted
    Parakeet ASR (Riva, gRPC). Returns (transcript_text, error_message).
    """
    if not NVIDIA_API_KEY:
        return None, "NVIDIA_API_KEY is not set — cannot run audio fallback."

    try:
        import riva.client
    except ImportError:
        return None, "nvidia-riva-client is not installed (pip install nvidia-riva-client)."

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            raw_audio_path = _download_audio(video_url, tmp_dir)
            wav_path = _to_riva_wav(raw_audio_path, tmp_dir)
        except Exception as e:
            return None, f"Could not download/prepare audio: {e}"

        try:
            auth = riva.client.Auth(
                uri=RIVA_SERVER,
                use_ssl=True,
                metadata_args=[
                    ["function-id", RIVA_ASR_FUNCTION_ID],
                    ["authorization", f"Bearer {NVIDIA_API_KEY}"],
                ],
            )
            asr_service = riva.client.ASRService(auth)
            config = riva.client.RecognitionConfig(
                language_code="en-US",
                max_alternatives=1,
                enable_automatic_punctuation=True,
            )

            with open(wav_path, "rb") as f:
                audio_bytes = f.read()

            response = asr_service.offline_recognize(audio_bytes, config)
            text = " ".join(
                result.alternatives[0].transcript
                for result in response.results
                if result.alternatives
            ).strip()

            if not text:
                return None, "Transcription returned empty text."
            return text, None
        except Exception as e:
            return None, f"Transcription failed: {e}"
