# Study Buddy

**Turn a YouTube video into a study guide.**

Study Buddy takes a YouTube video link, fetches its captions, and uses Groq to create a concise summary and a multiple-choice quiz. It is built with FastAPI, LangChain, and LangGraph, with a responsive frontend served by the same Python app.

---

## How it works

```text
YouTube video link
        │
        ▼
FastAPI receives the request
        │
        ▼
Supadata fetches the video's captions
        │
        ▼
LangGraph starts the study-guide workflow
        │
        ▼
LangChain sends the transcript to Groq
        │
        ▼
Groq returns a title, summary, and quiz
        │
        ▼
The browser displays the study guide
```

1. **You enter a link.** The frontend sends the video URL, preferred caption language, and quiz size to `POST /api/study`.
2. **The backend checks the request.** FastAPI validates the input and extracts the YouTube video ID.
3. **The transcript is retrieved.** `youtube.py` requests captions from Supadata. Using a hosted transcript service avoids relying on the Render server's own connection to YouTube captions.
4. **The AI workflow runs.** `workflow.py` passes the transcript to a LangGraph workflow. LangChain connects that workflow to the selected Groq model.
5. **The study guide is returned.** The model creates a title, summary points, and multiple-choice questions with correct answers and explanations.
6. **You review and take the quiz.** The frontend renders the results and checks your selected answers in the browser.

Study Buddy processes captions, not the video itself. A video must have captions that Supadata can retrieve.

---

## What you get

- A short title and key takeaways from the video
- A multiple-choice quiz based on the transcript
- Correct answers and explanations
- Caption-language selection
- A responsive interface for desktop and mobile
- A single FastAPI server for both the frontend and API

---

## Built with

| Technology | Used for |
| --- | --- |
| Python | Application backend |
| FastAPI | Web server and API endpoints |
| LangGraph | Organizes the study-guide generation workflow |
| LangChain | Connects the workflow to Groq |
| Groq | Generates the summary and quiz |
| Supadata | Retrieves YouTube captions |
| HTML, CSS, JavaScript | Frontend |
| Docker | Packages the app for hosting |
| Render | Deployment platform |

---

## Project layout

```text
youtube-study-buddy/
├── app.py                 # FastAPI app, request handling, and static-file serving
├── workflow.py            # Groq model setup and LangGraph workflow
├── youtube.py             # YouTube URL parsing and Supadata transcript request
├── requirements.txt       # Python packages
├── Dockerfile             # Container configuration
├── render.yaml            # Render Blueprint configuration
├── .env.example           # Local environment-variable template
├── .gitignore             # Keeps local secrets and generated files out of Git
└── static/
    ├── index.html         # Page structure
    ├── styles.css         # Visual design and responsive layout
    └── app.js             # Form submission, results, and quiz interactions
```

---

## Before you start

You need:

- Windows 10 or later
- Python 3.11 or later
- Git
- A Groq API key
- A Supadata API key

Create your keys here:

- Groq: [console.groq.com/keys](https://console.groq.com/keys)
- Supadata: [dash.supadata.ai](https://dash.supadata.ai/)

The two keys are used for different services. Groq generates the study guide; Supadata retrieves the transcript.

---

## Run locally on Windows

Open PowerShell in the project folder—the folder containing `app.py`.

### 1. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

### 2. Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow it for this terminal window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install the packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create your local `.env` file

```powershell
Copy-Item .env.example .env
notepad .env
```

Add your own credentials to `.env`:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_available_groq_model_id
SUPADATA_API_KEY=your_supadata_api_key
```

Replace the example values with your real keys and a model ID available to your Groq account. Keep each setting on one line; do not add quotes or spaces around the values.

### 5. Start the app

```powershell
uvicorn app:app --reload
```

Open **http://127.0.0.1:8000** in your browser. The frontend is served by FastAPI, so you do not need to start a separate frontend server.

To stop the app, press **Ctrl+C** in PowerShell.

---

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes | Groq credential used to generate the study guide |
| `GROQ_MODEL` | Yes | Model ID available to your Groq account |
| `SUPADATA_API_KEY` | Yes | Supadata credential used to fetch captions |

The `.env` file is for local development. On Render, set these variables in the service's **Environment** settings instead.

---

## API

### `GET /api/health`

Checks that the backend is running.

Example response:

```json
{
  "status": "ok"
}
```

### `POST /api/study`

Creates a study guide from a video link.

Example request:

```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language": "en",
  "quiz_count": 5
}
```

`quiz_count` must be between 3 and 10. The `language` value is a preferred caption-language code, such as `en` or `hi`.

The response contains the video information, title, summary, quiz questions, correct-answer indexes, and explanations.

---

## Deploy to Render

The repository includes a `Dockerfile` and `render.yaml` for Render deployment.

1. Push the project to a GitHub repository.
2. In Render, choose **New → Blueprint** and connect that repository.
3. Review the service configuration from `render.yaml`.
4. In the Render service's **Environment** settings, add:
   - `GROQ_API_KEY`
   - `GROQ_MODEL`
   - `SUPADATA_API_KEY`
5. Deploy the service.
6. Open the public URL Render provides and try a public video with accessible captions.

Keep secret values out of `render.yaml` and GitHub. Add them through Render's Environment settings. If you change an environment variable, redeploy the service so the running app receives the new value.

---

## Troubleshooting

### The page opens, but generating a guide fails

Check the Render application logs after submitting the video. The request depends on both Supadata (transcript retrieval) and Groq (study-guide generation), so verify that all three environment variables are set.

### Groq says the model is unavailable

Set `GROQ_MODEL` to a model ID currently available to your Groq account.

### Supadata cannot retrieve captions

Check that the video is public, captions are available, and `SUPADATA_API_KEY` is set correctly. Transcript-provider usage limits may also affect requests.

### The local app says an API key is missing

Check that `.env` is in the project root beside `app.py`. Confirm the variable name is spelled correctly and restart Uvicorn after editing `.env`.

### The page appears without styling

Check that `static/styles.css` exists and that the browser can load:

```text
http://127.0.0.1:8000/static/styles.css
```

Then refresh the page.

---

## Security

- Never commit `.env`.
- Never put API keys in HTML, CSS, JavaScript, or the README.
- Store production keys in Render's Environment settings.
- If a key appears in a screenshot or log, revoke it and create a replacement.
- Keep `.env.example` limited to placeholder values.

---

## License

No license has been selected for this repository. Add a `LICENSE` file before inviting others to reuse or distribute the code.
