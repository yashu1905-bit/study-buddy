# Study Buddy

Study Buddy turns a YouTube video into a study guide with a concise summary and a multiple-choice quiz.

Paste a video link, choose a caption language, and Study Buddy retrieves the transcript, creates study material, and displays an interactive quiz.

## Features

- Accepts YouTube video links
- Retrieves captions through the Supadata API
- Generates a study guide with Groq
- Creates multiple-choice questions with answers and explanations
- Uses LangChain and LangGraph for the AI workflow
- Includes a responsive web interface
- Can run locally or be deployed using Docker

## How the app works

```text
YouTube link
     │
     ▼
FastAPI backend (app.py)
     │
     ├── Validates the request
     ├── Extracts the video ID
     └── Requests captions from Supadata
                │
                ▼
       LangGraph workflow (workflow.py)
                │
                ├── LangChain sends the transcript to Groq
                └── Groq creates a summary and quiz
                            │
                            ▼
                  FastAPI returns the result
                            │
                            ▼
                 Frontend displays the guide

```
Step 1: Enter a video link
The frontend is built with HTML, CSS, and JavaScript. The learner pastes a YouTube link, selects a caption language, and chooses how many quiz questions to generate.

The browser sends the request to the FastAPI backend. API keys stay on the server and are not sent to the browser.
Step 2: Retrieve the transcript
The backend validates the submitted link and extracts its YouTube video ID. The youtube.py module sends the video URL to Supadata and receives the available transcript text.

A cloud server may be blocked when it requests captions directly from YouTube. Supadata provides the transcript API used by this project. Transcript availability can still vary by video.
Step 3: Generate the study guide
The backend passes the transcript and requested quiz size to the LangGraph workflow in workflow.py.

The workflow:
1. Receives the transcript.
2. Uses LangChain to call the configured Groq model.
3. Asks the model to return a title, key points, and quiz questions.
4. Returns the generated material to FastAPI.
LangGraph currently runs a simple one-step graph for generating the study material. More steps, such as flashcards or difficulty levels, can be added later.
Step 4: Display and take the quiz
FastAPI sends the result back to the browser as JSON. The frontend displays the summary and quiz. After the learner selects answers, the page shows the score and explanations.
Tech stack
Technology	Purpose
Python	Backend programming language
FastAPI	Web server and API
LangChain	Connects the app to the Groq model
LangGraph	Defines and runs the AI workflow
Groq	Generates the summary and quiz
Supadata	Retrieves YouTube transcripts
HTML, CSS, JavaScript	Frontend
Docker	Packages the app for deployment
Render	Hosts the app online


Project structure
youtube-study-buddy/
├── app.py                 # FastAPI app, frontend serving, and API endpoint
├── workflow.py            # LangChain model and LangGraph workflow
├── youtube.py             # YouTube link parsing and transcript retrieval
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker setup
├── render.yaml            # Render Blueprint configuration
├── .env.example           # Placeholder environment-variable template
├── .gitignore             # Excludes secrets and generated files
└── static/
    ├── index.html         # Web page structure
    ├── styles.css         # Layout, colors, and responsive design
    └── app.js             # Form requests, results, and quiz behavior
Requirements
To run Study Buddy locally, you need:
- Python 3.11 or newer
- Git
- A Groq API key
- A Supadata API key
- An internet connection
Create API keys here:
- Groq: https://console.groq.com/keys
- Supadata: https://dash.supadata.ai/
The keys are separate:
- GROQ_API_KEY is used to generate the study material.
- SUPADATA_API_KEY is used to retrieve the transcript.
Run locally on Windows
Open PowerShell in the project folder.
1. Create a virtual environment
py -3.11 -m venv .venv
2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1
If PowerShell blocks activation, run this command in the same PowerShell window:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Then activate the environment:
.\.venv\Scripts\Activate.ps1
3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
4. Create your .env file
Copy the example environment file:
Copy-Item .env.example .env
Open .env:
notepad .env
Add your own API keys and a Groq model ID available to your account:
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_available_groq_model_id
SUPADATA_API_KEY=your_supadata_api_key
Save the file. Keep each value on one line. Do not add quotes or spaces around the values.
5. Start the server
uvicorn app:app --reload
Open the app in your browser:
http://127.0.0.1:8000
To stop the server, press Ctrl+C in PowerShell.
Environment variables
Variable	Required	Description
GROQ_API_KEY	Yes	Secret key used to access Groq
GROQ_MODEL	Yes	Groq model ID used to generate the study guide
SUPADATA_API_KEY	Yes	Secret key used to retrieve video transcripts


The local .env file should stay on your computer. Do not commit it to GitHub.
API endpoints
GET /
Serves the Study Buddy web page.
GET /api/health
Checks whether the backend is running.

Example response:
{
  "status": "ok"
}
POST /api/study
Creates the summary and quiz for a video.

Example request:
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "en",
  "quiz_count": 5
}
The quiz count must be between 3 and 10. The selected language is used as the preferred caption language.

The response contains the guide title, summary points, quiz questions, answer indexes, explanations, and video information.
Deployment
The repository includes a Dockerfile and render.yaml for deploying on Render.
1. Push the project to a GitHub repository.
2. In Render, create a Blueprint and connect the repository.
3. Check the service settings and make sure Render is using the repository’s Dockerfile.
4. Add these environment variables in the Render service’s Environment settings:
   - GROQ_API_KEY
   - GROQ_MODEL
   - SUPADATA_API_KEY
5. Deploy the service.
6. When Render reports that the service is live, open its public URL.
7. Test the app with a public YouTube video that has accessible captions.
Secret values belong in Render’s Environment settings. Do not put API keys in render.yaml or commit them to GitHub.
Troubleshooting
GROQ_API_KEY is missing
Check that the variable is present in your local .env file or in the Render service’s Environment settings. Restart or redeploy after changing environment variables.
Groq reports that a model is unavailable
Check the Groq Console and set GROQ_MODEL to a model ID available to your account.
Transcript retrieval fails
Check that:
- The video is public.
- Captions are available for the video.
- SUPADATA_API_KEY is set correctly.
- The API key has available usage or credits.
The page appears without styling
Check that the static folder contains index.html, styles.css, and app.js. Then refresh the page.
The app works locally but fails on Render
Check the Render application logs after submitting a video. Confirm that all three environment variables are set in the Render service.
Security
- Never commit .env.
- Never put API keys in HTML, CSS, or JavaScript.
- Add secret keys through Render’s Environment settings.
- If a key appears in a screenshot or log, revoke it and create a replacement.
- Keep .env.example limited to placeholders.
