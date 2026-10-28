import re
import os
import time
import requests

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


def get_transcript_from_supadata(
    video_url: str,
    preferred_language: str = "en",
) -> tuple[str, str]:
    api_key = os.getenv("SUPADATA_API_KEY")

    if not api_key:
        raise RuntimeError("SUPADATA_API_KEY Render Environment settings mein missing hai.")

    headers = {"x-api-key": api_key}
    params = {
        "url": video_url,
        "lang": preferred_language,
        "text": "true",
        "mode": "auto",
    }

    try:
        response = requests.get(
            "https://api.supadata.ai/v1/transcript",
            headers=headers,
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        # Long videos may return a job ID that needs polling.
        job_id = data.get("jobId")
        if job_id:
            for _ in range(90):
                time.sleep(2)
                job_response = requests.get(
                    f"https://api.supadata.ai/v1/transcript/{job_id}",
                    headers=headers,
                    timeout=30,
                )
                job_response.raise_for_status()
                data = job_response.json()

                if data.get("status") == "completed":
                    break
                if data.get("status") == "failed":
                    raise RuntimeError("Supadata can't process video transcript ")
            else:
                raise RuntimeError("Transcript in progress. Try again after some time")

        content = data.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )

        if not content.strip():
            raise RuntimeError("can;t find transcript for this video.")

        return content[:60000], data.get("lang", preferred_language)

    except requests.RequestException as error:
        detail = ""
        if getattr(error, "response", None) is not None:
            detail = error.response.text[:500]
        print(f"Supadata request error: {error} {detail}")
        raise RuntimeError(
            "Can;t find captions from Transcript service. Check API key aur service limits"
        ) from error