import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

from workflow import make_study_material
from youtube import get_video_id, get_transcript



BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="YouTube Study Buddy")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StudyRequest(BaseModel):
    video_url: str = Field(min_length=8)
    language: str = "en"
    quiz_count: int = Field(default=5, ge=3, le=10)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/study")
def study_video(request: StudyRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is missing. Add it to your .env file and restart the app.",
        )

    try:
        video_id = get_video_id(request.video_url)
        transcript, transcript_language = get_transcript(
            video_id,
            preferred_language=request.language,
        )
        result = make_study_material(
            transcript=transcript,
            quiz_count=request.quiz_count,
        )
        result["video_id"] = video_id
        result["transcript_language"] = transcript_language
        result["video_url"] = f"https://www.youtube.com/watch?v={video_id}"
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        # Keep technical details in the server console, not the browser.
        print(f"Study request failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the study guide. Check the server console.",
        ) from error