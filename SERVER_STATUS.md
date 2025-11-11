# API Server Status

## ✅ Server Running

The Causal Rationale Extraction System API server is now running!

### Access Points

- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

### Available Endpoints

#### 1. POST /query
Process a natural language query about business events.

**Request:**
```json
{
  "query": "Why are escalations happening on calls?",
  "conversation_id": "optional_conversation_id",
  "context": []
}
```

**Response:**
```json
{
  "response": "Causal explanation...",
  "evidence": [...],
  "conversation_id": "...",
  "metadata": {...}
}
```

#### 2. POST /query/follow-up
Process a follow-up query with context from previous conversation.

**Request:**
```json
{
  "query": "What patterns lead to these escalations?",
  "conversation_id": "required_conversation_id",
  "context": []
}
```

#### 3. GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### Test the API

#### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Process a query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why are escalations happening on calls?",
    "conversation_id": "test_001"
  }'

# Follow-up query
curl -X POST "http://localhost:8000/query/follow-up" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What patterns lead to these escalations?",
    "conversation_id": "test_001"
  }'
```

#### Using Python:

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Process query
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "Why are escalations happening on calls?",
        "conversation_id": "test_001"
    }
)
print(response.json())
```

### Server Management

#### Start Server:
```bash
cd "/mnt/ritesh/7 th Semester/INTER_IIT_PREP"
source venv/bin/activate
export GEMINI_API_KEY=AIzaSyDceW1Y6h66LooX7kwZnZLLiRD7ffJkalo
python3 test_server_startup.py
```

Or use the startup script:
```bash
./scripts/start_server.sh
```

#### Stop Server:
```bash
pkill -f "uvicorn.*main:app"
# or
pkill -f test_server_startup
```

#### Check Server Status:
```bash
curl http://localhost:8000/health
```

### Configuration

- **Host**: 0.0.0.0 (accessible from all interfaces)
- **Port**: 8000
- **LLM Provider**: Gemini (configured via environment variables)
- **Vector DB**: ./data/processed/vector_db

### Notes

- The server uses lazy loading - the system initializes on first request
- API documentation is available at /docs (Swagger UI)
- The server supports hot reload if started with --reload flag
- All endpoints return JSON responses

