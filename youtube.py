import re

from youtube_transcript_api import YouTubeTranscriptApi


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def get_video_id(video_url: str) -> str:
    """Accept common YouTube URL formats or a plain 11-character video ID."""
    value = video_url.strip()

    if VIDEO_ID_PATTERN.fullmatch(value):
        return value

    patterns = [
        r"(?:youtube\.com/watch\?.*v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/(?:embed|shorts)/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)

    raise ValueError(
        "That doesn’t look like a YouTube link. Paste a watch, Shorts, or youtu.be URL."
    )


def get_transcript(video_id: str, preferred_language: str = "en") -> tuple[str, str]:
    """Fetch available captions and return their text and language code."""
    try:
        fetched = YouTubeTranscriptApi().fetch(
            video_id,
            languages=[preferred_language, "en"],
        )
        transcript = " ".join(
            snippet.text.replace("\n", " ").strip()
            for snippet in fetched
            if snippet.text.strip()
        )
        if not transcript:
            raise RuntimeError("The video has captions, but their transcript is empty.")

        # Keep requests within reasonable model limits.
        transcript = transcript[:60_000]
        return transcript, fetched.language_code

    except RuntimeError:
        raise
    except Exception as error:
        print(f"YouTube transcript error for {video_id}: {type(error).__name__}: {error}")
        raise RuntimeError(
            f"Couldn’t load captions ({type(error).__name__}). "
            "Check Render logs for details."
        ) from error