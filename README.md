# CampusMate AI

## Overview

CampusMate AI is an AI-powered study assistant for students. It helps with asking questions, explaining topics, summarizing text, generating quizzes, taking quizzes, and reviewing study history and statistics.

## Student

Viona Lushta

## Features

- Ask AI
- Explain Topic
- Summarize Text
- Generate Quiz
- Take Quiz
- History
- Statistics

## Technologies

- Python
- OpenAI API
- `gpt-4o-mini`
- JSON
- React
- Vite
- React Router

## Project Structure

- `backend/` - Python services, HTTP API, tests, and local persistence logic
- `frontend/` - React/Vite frontend application
- `backend/data/` - Local JSON storage for history and statistics
- `backend/test*.py` - Backend test suite

## Setup

1. Create and activate a Python virtual environment.

   ```bash
   python -m venv .venv
   ```

2. Install Python dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Create a local `.env` file in the repository root with your OpenAI key.

   ```bash
   OPENAI_API_KEY=your_key_here
   ```

4. Install frontend dependencies.

   ```bash
   cd frontend
   npm install
   ```

## Backend Run Instructions

Run the backend HTTP server:

```bash
python -m backend.main --host 127.0.0.1 --port 8000
```

## Frontend Run Instructions

Run the frontend development server:

```bash
cd frontend
npm run dev
```

If port 4173 is already in use, Vite will choose another available local port automatically.

## Testing

Run the backend test suite:

```bash
python -m unittest discover -s backend -p "test*.py"
```

Build the frontend for production:

```bash
cd frontend
npm run build
```

## Security

- `.env` is ignored by Git and must never be committed.
- API keys must stay in the local `.env` file.
- Do not place OpenAI credentials in the frontend.
- The frontend talks only to the local Python backend.
