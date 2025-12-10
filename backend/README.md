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
3. Local dev default uses DuckDB (file at `data/gtfs-sweden3/gtfs.duckdb`). Set `DATABASE_URL` accordingly; for Postgres, use your DSN instead.
4. Ingest GTFS Sweden 3 static feed:
   ```bash
   python -m app.ingestion.gtfs_loader
   ```
   - This also materializes rail-only tables (`routes_rail`, `trips_rail`, `stop_times_rail`, `stops_rail`, `shapes_rail`, `transfers_rail`) and a helper view with agency names (`routes_rail_with_agency`). Route types are filtered via a rail whitelist (100–109, 200/201/202/204/205, 900).
   - If you need full multi-modal data, call `ingest(include_rail=False)` from Python and skip the rail subset.
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

