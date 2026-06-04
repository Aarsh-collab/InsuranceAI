# InsuranceAI

InsuranceAI is an AI workflow assistant for life insurance intake, preliminary quote guidance, document review, and broker handoff.

The project is built around a simple idea: consumers should be able to answer questions naturally, understand what they are looking at, and choose when to involve a licensed broker. Brokers should get cleaner lead context instead of messy chat transcripts and half-filled forms.

This is an MVP, not a carrier quoting engine or a replacement for licensed advice. Estimates are preliminary, document review is informational, and final recommendations belong with a licensed professional.

## What It Does

- Conversational life insurance intake
- Preliminary monthly premium estimate using a local ML model
- Broker handoff with name, email, phone, and preferred meeting time
- Admin dashboard for reviewing leads, sessions, quotes, summaries, chat history, and DEC page data
- Life insurance DEC page upload, parsing, and Q&A
- Site-based lead separation for demo vs broker deployments
- Basic admin token auth
- Rate limiting on account creation, sessions, chat, and document upload
- Demo frontend and embeddable widget route

## Product Scope

Current supported product:

- Life insurance

Shown as future scope, but not implemented:

- Auto
- Home
- Renters
- Health

The assistant should not pretend those products are supported yet.

## Tech Stack

Backend:

- FastAPI
- SQLAlchemy
- SQLite locally
- OpenAI via LangChain
- PyMuPDF for PDF text extraction
- SlowAPI for rate limiting
- SendGrid for broker notification email
- scikit-learn/joblib for the local life quote model

Frontend:

- React
- Vite
- Tailwind CSS
- React Router

## Project Structure

```text
InsuranceAI/
  backend/
    core/                 # auth, config, rate limiting
    db/                   # database setup and SQLAlchemy models
    routers/              # public, chat, DEC page, and admin routes
    services/             # AI services, parser, matching, summarizer
    tests/                # manual flow and seed scripts
    utils/                # state schemas and helper logic
  frontend/
    src/
      components/admin/   # admin dashboard UI
      components/assistants/ # widget/sidebar assistant UI
      hooks/              # assistant chat engine
      services/           # frontend API clients
  docs/
    mvp-polish-log.md
```

## Environment Variables

Create a local `.env` from `.env.example`.

Required backend values:

```env
DATABASE_URL=sqlite:///./usersData.db
OPENAI_API_KEY=your-openai-api-key

ADMIN_TOKEN=overall-admin-token
SITE_ADMIN=site-specific-admin-token
SITE_ID=friend_dad_site

SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL_ADDRESS=broker-notifications@example.com
TO_EMAIL_ADDRESS=broker@example.com

ALLOWED_ORIGINS=http://localhost:5173
```

Never commit `.env`, local database files, API keys, model artifacts, or uploaded documents.

## Local Setup

### Backend

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the backend:

```bash
cd backend
uvicorn main:app --reload
```

Backend health check:

```bash
curl http://localhost:8000/health
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend should run at:

```text
http://localhost:5173
```

## Main Routes

Public demo:

```text
/
```

Embeddable widget:

```text
/widget?site_id=friend_dad_site&brand=ABCInsurance
```

Admin dashboard:

```text
/admin/login
/admin
/admin/leads
/admin/leads/:sessionId
```

Backend docs:

```text
http://localhost:8000/docs
```

## Manual Test Flows

The project includes manual end-to-end flow scripts that exercise the AI conversation through the real backend.

List available scenarios:

```bash
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py --list
```

Core scenarios:

```bash
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py clean
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py broker_handoff
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py quote_explanation
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py privacy
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py messy
```

Run the full deep routing suite and save a timestamped transcript:

```bash
ADMIN_TOKEN=test-admin-token uv run backend/tests/manual_life_flow.py --all --sleep 2 --log-default
```

Seed one demo lead and one broker-site lead:

```bash
ADMIN_TOKEN=test-admin-token \
SITE_ADMIN=friend-dad-test-token \
uv run backend/tests/seed_two_site_leads.py
```

## Rate Limiting

Current MVP limits:

```text
POST /accounts                    10/minute
POST /accounts/{account_id}/sessions 20/minute
POST /chat/router                 15/minute
POST /dec-page/upload             5/minute
```

These are intended to stop obvious spam and accidental abuse during private deployment. Production deployments should eventually use Redis-backed rate limiting if the backend runs across multiple instances.

## DEC Page Upload Notes

The current PDF flow works best with text-based PDFs. Image-only scanned PDFs may fail because they need OCR.

Supported behavior today:

- Parse text-based life insurance DEC pages
- Answer questions about life insurance document fields
- Refuse unsupported non-life documents cleanly

Future improvement:

- OCR fallback for scanned/image PDFs

## Deployment Notes

Before deploying:

- Use strong `ADMIN_TOKEN` and `SITE_ADMIN` values
- Set `OPENAI_API_KEY` in the deployment environment
- Use a fresh production database
- Set `ALLOWED_ORIGINS` to real frontend/admin/widget domains
- Do not deploy local `.env`, `.db`, `node_modules`, `dist`, uploaded PDFs, or ML artifacts
- Confirm site-based admin filtering works

The large local ML model and generated training data are intentionally ignored by Git:

```text
backend/models/
backend/ML/life_insurance_data.csv
```

If the backend depends on the model file in production, it should be provided through deployment storage, model registry, artifact upload, or regenerated during setup.

## Status

This is an active MVP. The core life insurance workflow, admin dashboard, DEC Q&A, OpenAI-backed routing, and broker handoff are working locally. The next major milestone is private deployment on a real broker website and a controlled demo environment.

## Disclaimer

InsuranceAI provides preliminary estimates and educational explanations. It does not provide legal, financial, tax, or insurance advice. Final coverage decisions and policy recommendations should be reviewed by a licensed insurance professional.
