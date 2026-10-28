# Study Buddy

Paste a YouTube link to create a short study guide and a multiple-choice quiz.

## Requirements

- Python 3.11 or newer
- An OpenAI API key
- A public YouTube video with captions

## Run on Windows

Open PowerShell in this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env