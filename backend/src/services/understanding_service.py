"""
Single entry point the UI should call to get "something to make notes
from", trying progressively more expensive free methods:

1. YouTube captions (instant, free, no key)
2. Audio -> Riva/Parakeet ASR transcription, for videos with speech but
   no captions (NVIDIA free tier)
3. Frame extraction -> NVIDIA vision model description, for videos with
   little/no speech (NVIDIA free tier)

Steps 2 and 3 are combined when relevant — e.g. a mostly-silent coding
video with occasional narration gets both the (short) spoken transcript
and the visual descriptions merged together.
"""
from src.services.transcript_service import get_transcript as _get_captions
from src.services.audio_transcription import transcribe_video_audio
from src.services.visual_transcription import get_visual_transcript

MIN_WORDS_CONSIDERED_SUBSTANTIAL = 40  # below this, treat audio as "not enough"


def get_full_understanding(url: str, language=None) -> tuple[str | None, str | None]:
    """
    Returns (text_to_summarize, status_message). status_message describes
    which method(s) were used, or the error if everything failed.
    """
    notes = []

    # 1. Captions first — cheapest and most accurate when they exist
    caption_text, caption_err = _get_captions(url, language)
    if caption_text and len(caption_text.split()) >= MIN_WORDS_CONSIDERED_SUBSTANTIAL:
        return caption_text, "Used existing YouTube captions."

    # 2. Captions missing/thin -> try audio transcription
    audio_text, audio_err = transcribe_video_audio(url)
    audio_word_count = len(audio_text.split()) if audio_text else 0

    if audio_text:
        notes.append(f"[SPOKEN AUDIO TRANSCRIPT]\n{audio_text}")

    # 3. If audio was thin or missing, video is likely silent/visual-heavy
    #    -> also analyze frames
    if audio_word_count < MIN_WORDS_CONSIDERED_SUBSTANTIAL:
        visual_text, visual_err = get_visual_transcript(url)
        if visual_text:
            notes.append(f"[VISUAL/ON-SCREEN CONTENT]\n{visual_text}")

    if not notes:
        return None, (
            "Could not extract anything usable: no captions "
            f"({caption_err}), no usable audio ({audio_err}), and no "
            "usable visual content."
        )

    combined = "\n\n".join(notes)
    if len(notes) == 2:
        source = "audio transcription + visual frame analysis (no captions were available)"
    elif audio_word_count >= MIN_WORDS_CONSIDERED_SUBSTANTIAL:
        source = "audio transcription (no captions were available)"
    else:
        source = "visual frame analysis (no captions or usable audio)"

    return combined, f"Used {source}."
