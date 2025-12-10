# GTFS Chat - Swedish Railway Information Assistant

A conversational AI application for exploring Swedish GTFS railway data through natural language queries.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Setup

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your API keys:
   # - TRAFIKLAB_API_KEY
   # - OPENROUTER_API_KEY
   # - OPENROUTER_MODEL (default: openrouter/quasar-alpha)
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup** (if not already done)
   ```bash
   cd backend
   source .venv/bin/activate
   python -m app.ingestion.gtfs_loader
   ```

### Running Development Servers

#### Option 1: Start Both Servers (Recommended)
```bash
./start.sh
```

This will start:
- **Backend API**: http://127.0.0.1:8000
- **Frontend**: http://127.0.0.1:8080
- **API Docs**: http://127.0.0.1:8000/docs

Press `Ctrl+C` to stop all servers.

#### Option 2: Start Servers Separately

**Backend only:**
```bash
cd backend
source .venv/bin/activate
set -a && source .env && set +a
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

#### Option 3: ADK Web Interface (for testing the agent)
```bash
./start-adk.sh
```

This starts the Google ADK web interface at http://127.0.0.1:8001 for interactive agent testing.

## 📁 Project Structure

```
gtfs-chat/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── agents/       # ADK agent definitions
│   └── tests/        # Backend tests
├── frontend/         # Vite/React frontend
│   └── src/          # Source code
├── data/             # GTFS data and database
└── start.sh          # Development startup script
```

## 🛠️ Development

### Backend
- FastAPI with SQLAlchemy ORM
- DuckDB for local development (PostgreSQL supported)
- Google ADK for AI agent capabilities
- LiteLLM with OpenRouter integration

### Frontend
- Vite + React + TypeScript
- Tailwind CSS + shadcn/ui components
- React Router for navigation

## 🔧 Available Tools

The AI agent has access to 4 tools:
1. **search_rail_stops** - Find railway stations by name
2. **get_departures** - Find trains between two stations
3. **get_next_departures** - Get upcoming departures from a station
4. **get_route_stops** - Get all stops on a specific trip

## 📝 API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat/adk` - Chat endpoint with ADK agent

## 🧪 Testing

```bash
# Backend tests
cd backend
source .venv/bin/activate
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

## 📄 License

Apache-2.0

