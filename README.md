# CampusMate AI

CampusMate AI is an AI-powered study assistant project scaffold.

## Tech Stack

- Python
- React
- Vite
- OpenAI Python SDK
- `python-dotenv`
- JSON for later local history/statistics storage

## Folder Structure

```text
CampusMate-AI/
├── backend/
├── frontend/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## OpenAI Model

Future OpenAI integration for this project will use only `gpt-4o-mini`.

## Security Note

Put your real API key in `.env` and never commit that file to Git.

## Setup

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the React Vite development server:

```bash
cd frontend
npm install
npm run dev
```

