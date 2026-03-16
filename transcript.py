import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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

def extract_video_id(url):
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
    video_id = extract_video_id(url)

    if not video_id:
        return None, "Invalid YouTube URL. Please check and try again."

    try:
        ytt = YouTubeTranscriptApi()

        if language:
            try:
                transcript_list = ytt.list(video_id)
                available_codes = [t.language_code for t in transcript_list]

                if language in available_codes:
                    transcript_data = ytt.fetch(video_id, languages=[language])
                else:
                    # try auto-generated variant like hi-IN or zh-Hans
                    partial_match = [c for c in available_codes if c.startswith(language[:2])]
                    if partial_match:
                        transcript_data = ytt.fetch(video_id, languages=[partial_match[0]])
                    else:
                        # fallback to English then whatever is available
                        if 'en' in available_codes:
                            transcript_data = ytt.fetch(video_id, languages=['en'])
                        else:
                            transcript_data = ytt.fetch(video_id, languages=[available_codes[0]])

            except Exception:
                transcript_data = ytt.fetch(video_id)
        else:
            transcript_data = ytt.fetch(video_id)

        full_text = " ".join([entry.text for entry in transcript_data])
        return full_text, None

    except TranscriptsDisabled:
        return None, "This video has transcripts disabled."

    except NoTranscriptFound:
        return None, "No transcript found. Try a different language or check if the video has captions enabled."

    except Exception as e:
        return None, f"Something went wrong: {str(e)}"

def get_available_languages(url):
    video_id = extract_video_id(url)
    if not video_id:
        return []
    try:
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.list(video_id)
        langs = []
        for t in transcript_list:
            langs.append({
                'code': t.language_code,
                'name': t.language,
                'auto': t.is_generated
            })
        return langs
    except Exception:
        return []       