import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field,model_validator


load_dotenv()

from workflow import make_study_material
from youtube import get_video_id, get_transcript, get_transcript_from_supadata



BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="YouTube Study Buddy")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class StudyRequest(BaseModel):
    video_url: str = ""
    transcript_text: str = Field(default="", max_length=150000)
    language: str = "en"
    quiz_count: int = Field(default=5, ge=3, le=10)

    @model_validator(mode="after")
    def require_url_or_transcript(self):
        if not self.video_url.strip() and not self.transcript_text.strip():
            raise ValueError("paste youtube link or copied transcript.")
        return self

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
            detail="GROQ_API_KEY missing . Add key in  Render Environment settings",
        )

    video_id = None

    try:
        if request.transcript_text.strip():
            transcript = request.transcript_text.strip()
            transcript_language = request.language
        else:
            video_id = get_video_id(request.video_url)
            transcript, transcript_language = get_transcript_from_supadata(
           f"https://www.youtube.com/watch?v={video_id}",
           preferred_language=request.language,
         )

        result = make_study_material(
            transcript=transcript[:60000],
            quiz_count=request.quiz_count,
        )

        result["video_id"] = video_id
        result["transcript_language"] = transcript_language
        result["video_url"] = (
            f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
        )
        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        print(f"Study request failed: {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=500,
            detail="Study guide can't be made .Check  Render logs .",
        ) from error