# Moon Dev Flow UI - Backend

FastAPI server for orchestrating AI trading agents with a flow-based UI.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure database
# Update .env with your PostgreSQL connection string
# Then run migrations (create database)
createdb moon_dev_flows

# Run server
python -m uvicorn src.api.app:app --reload
```

Server will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── app.py              # FastAPI application
│   │   ├── routers/            # API endpoint modules
│   │   ├── orchestrator/       # Flow execution logic
│   │   └── ws/                 # WebSocket handlers
│   ├── database/               # Database connection and models
│   ├── models/                 # Pydantic schemas
│   └── tests/                  # Unit tests
├── requirements.txt
├── .env                        # Local environment
└── README.md
```

## Development

See `.amp/WEEK_1_DAILY_TASKS.md` for detailed daily tasks.

## API Endpoints

All endpoints documented at http://localhost:8000/docs

### Flow Management
- `POST /api/flows` - Create flow
- `GET /api/flows` - List flows
- `GET /api/flows/{id}` - Get flow
- `PUT /api/flows/{id}` - Update flow
- `DELETE /api/flows/{id}` - Delete flow

### Execution
- `POST /api/execution/{flow_id}/run` - Start execution
- `GET /api/execution/{id}` - Get execution status
- `GET /api/execution/{id}/logs` - Get logs

### WebSocket
- `GET /ws/execution/{execution_id}` - Real-time execution updates
