# Talowiz - Lead AI Intern Mini Challenge Solution

A polished solution for the challenge requirements:
- Reads a PDF
- Uses Google Gemini 1.5 API
- Answers question(s) from PDF content

## Files

- `app.py` — main CLI tool
- `requirements.txt` — dependencies
- `.env.example` — env variable template
- `test_app.py` — lightweight unit tests for core helpers

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set your API key in `.env` (or export in shell):

```env
GEMINI_API_KEY=your_actual_api_key
```

## Run

```bash
python app.py --pdf /path/to/file.pdf --question "What is the main topic?"
```

Optional flags:

```bash
python app.py \
  --pdf /path/to/file.pdf \
  --question "Summarize eligibility criteria" \
  --model gemini-1.5-flash \
  --save-answer answer.txt \
  --env-file .env
```

## What was improved

- Better structure with helper functions (`build_prompt`, `chunk_text`, `load_env_file`)
- Handles long PDFs by chunking and merging partial answers
- Optional answer export (`--save-answer`)
- Optional `.env` loading when `python-dotenv` is available
- Added basic tests for deterministic helper logic

## Submission Checklist

- Push code to GitHub
- Record a Loom video showing:
  - how script works
  - where Gemini API is used
  - final output demo
