# GTFS Sweden Chat Backend (FastAPI)

## Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Requests + pandas for GTFS ingestion

## Setup
1. Create a virtual environment and install requirements:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `env.example` to `.env` (or export variables) and set:
   - `DATABASE_URL` (e.g., `postgresql+psycopg://postgres:postgres@localhost:5432/gtfs_chat`)
   - `TRAFIKLAB_API_KEY`
3. Run PostgreSQL locally and create the database.
4. Ingest GTFS Sweden 3 static feed:
   ```bash
   python -m app.ingestion.gtfs_loader
   ```
5. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## API
- `GET /api/health` – basic healthcheck
- `POST /api/chat` – conversational endpoint
  - request: `{ "message": "from Stockholm C to Göteborg after 14:00" }`
  - response: message plus optional table for departures

### Response envelope (frontend states)
- `messages`: array of `{ role, text, table?, warnings? }`
  - `table`: `{ title?, columns: [{ id, label }], rows: [{...}] }`
- `metadata`: optional object for extra context
- Examples:
  - Empty/error: `{ messages: [{ role: "assistant", text: "Please specify both origin and destination..." , warnings: ["Missing origin or destination."] }], metadata: {} }`
  - Table: `{ messages: [{ role: "assistant", text: "Departures from Stockholm C to Göteborg after 14:00", table: { title: "Departures", columns: [...], rows: [...] } }], metadata: {} }`

## Notes
- Query safety: row caps are enforced in SQL templates.
- Follow-up context is minimal for now; frontend can pass `session_id` to extend later.
- Ingestion truncates tables before reload for deterministic refreshes.

