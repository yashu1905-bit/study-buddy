# Study Buddy

Turn a YouTube video into a short study guide and quiz. Paste a video link to fetch its captions, then Study Buddy uses Groq to create key takeaways and multiple-choice questions.

## Features

- Fetches YouTube captions through the Supadata API
- Creates a concise summary and multiple-choice quiz with Groq
- Uses LangChain and LangGraph for the AI workflow
- Includes a responsive web interface
- Can run locally or be deployed as a Docker web service

## Tech stack

- **Backend:** Python, FastAPI
- **AI workflow:** LangChain, LangGraph
- **Language model:** Groq
- **YouTube captions:** Supadata
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Docker and Render

## Requirements

- Python 3.11 or newer
- A [Groq API key](https://console.groq.com/keys)
- A [Supadata API key](https://dash.supadata.ai/)

The Groq and Supadata keys are separate. Groq generates the study material; Supadata fetches the video transcript.

## Run locally on Windows

Open PowerShell in the project folder.

### 1. Create and activate a virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
If PowerShell prevents activation, allow it for the current terminal window:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
3. Set environment variables
Copy the example file:
Copy-Item .env.example .env
Open .env and add your own keys and the Groq model ID available to your account:
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_available_groq_model_id
SUPADATA_API_KEY=your_supadata_api_key
Do not add quotes around the values. Do not commit .env to GitHub.
4. Start the app
uvicorn app:app --reload
Open http://127.0.0.1:8000 in your browser.
How to use it
1. Paste a public YouTube video link.
2. Select the caption language.
3. Click Build my study guide.
4. Review the summary and answer the quiz.
The video needs to have captions available through the transcript provider. Transcript availability can vary by video and provider limits.
Environment variables
Variable	Purpose
GROQ_API_KEY	Secret key used to call Groq
GROQ_MODEL	Groq model ID used to generate the summary and quiz
SUPADATA_API_KEY	Secret key used to retrieve video transcripts


Keep all API keys in environment variables. Never place them in frontend JavaScript, README files, screenshots, or Git commits.
API endpoints
GET /api/health
Returns a simple backend health response:
{
  "status": "ok"
}
POST /api/study
Creates a summary and quiz. Example request:
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "en",
  "quiz_count": 5
}
quiz_count must be between 3 and 10.
Deploying
The repository includes a Dockerfile and render.yaml for Render.
1. Push the project to GitHub.
2. In Render, create a Blueprint using the repository.
3. Add GROQ_API_KEY, GROQ_MODEL, and SUPADATA_API_KEY under the service's Environment settings.
4. Deploy the service and open the public URL shown by Render.
Do not put secret values in render.yaml. Add them through Render's Environment settings.
Project structure
.
├── app.py
├── workflow.py
├── youtube.py
├── requirements.txt
├── Dockerfile
├── render.yaml
├── .env.example
├── .gitignore
└── static/
    ├── index.html
    ├── styles.css
    └── app.js
Troubleshooting
- GROQ_API_KEY missing: Check that .env exists locally or that the variable is set in Render.
- Groq model error: Set GROQ_MODEL to a model ID currently available in your Groq account.
- Transcript error: Check that the video is public, captions are available, and SUPADATA_API_KEY is set correctly.
- Port or startup issue: Run the app from the project folder and check the server logs.
