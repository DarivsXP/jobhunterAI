# JobHunterAI

AI-powered career assistant for finding, scoring, ranking, saving, and tracking remote jobs for a junior software developer profile.

## Current Capabilities

- Multi-source remote job intake
- Profile-driven normalization and prefiltering
- Resume-aware scoring and ranking
- Optional OpenAI recruiter enrichment
- Optional Telegram notifications
- SQLite persistence
- Local CLI dashboard and job tracker

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`.

## Commands

Run the job pipeline:

```bash
python app.py run
```

Show the local dashboard:

```bash
python app.py report --limit 10
```

List top saved jobs:

```bash
python app.py top --limit 10
python app.py top --status applied
```

Update application status:

```bash
python app.py status --job-id 12 --value applied
python app.py status --job-id 12 --value interviewing
```

## Environment Variables

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- `DATABASE_PATH`
- `LOG_LEVEL`
