# Usage Guide - Causal Rationale Extraction System

This guide provides step-by-step instructions on how to use the Causal Rationale Extraction System.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Data Preparation](#data-preparation)
4. [Running the System](#running-the-system)
5. [Using the API](#using-the-api)
6. [Python API Usage](#python-api-usage)
7. [Generating Query Dataset](#generating-query-dataset)
8. [Examples](#examples)

## Prerequisites

- Python 3.9 or higher
- pip package manager
- API keys for LLM providers (OpenAI, Anthropic, or Google Gemini)
- Transcript data in supported formats (JSON, CSV, or TXT)

## Installation

### 1. Clone or Navigate to Project Directory

```bash
cd "/mnt/ritesh/7 th Semester/INTER_IIT_PREP"
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Add your API keys:
```bash
GEMINI_API_KEY=AIzaSyDceW1Y6h66LooX7kwZnZLLiRD7ffJkalo
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-pro
VECTOR_DB_PATH=./data/processed/vector_db
```

## Data Preparation

### Step 1: Prepare Your Transcript Data

Place your transcript files in the `data/raw/` directory. Supported formats:

#### JSON Format
```json
{
  "transcript_id": "call_123",
  "turns": [
    {
      "turn_id": 1,
      "speaker": "agent",
      "text": "Hello, how can I help you?",
      "timestamp": 0.0
    },
    {
      "turn_id": 2,
      "speaker": "customer",
      "text": "I need help with my order",
      "timestamp": 2.5
    }
  ],
  "events": [
    {
      "event_type": "escalation",
      "event_label": "supervisor_request",
      "turn_id": 10
    }
  ],
  "metadata": {}
}
```

#### CSV Format
Create a CSV with columns: `transcript_id`, `turn_id`, `speaker`, `text`, `timestamp`, `event_type`, `event_label`

Example:
```csv
transcript_id,turn_id,speaker,text,timestamp,event_type,event_label
call_123,1,agent,Hello how can I help you?,0.0,,
call_123,2,customer,I need help with my order,2.5,,
call_123,10,customer,I want to speak to a supervisor,25.0,escalation,supervisor_request
```

### Step 2: Process Transcript Data

Process your transcripts to extract dialogue spans and index them:

```bash
python scripts/process_data.py \
  --input data/raw \
  --output data/processed \
  --pattern "*.json" \
  --index
```

This will:
- Load transcripts from `data/raw`
- Preprocess and normalize the data
- Extract dialogue spans (5 turns per span by default)
- Index spans to vector database for retrieval
- Save processed transcripts to `data/processed`

## Running the System

### Option 1: Using the API Server

#### Start the API Server

```bash
# From project root
python -m src.main

# Or using uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

#### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /query` - Process a query (Task 1 or Task 2)
- `POST /query/follow-up` - Process a follow-up query (Task 2)

### Option 2: Using Python API Directly

See [Python API Usage](#python-api-usage) section below.

## Using the API

### Task 1: Initial Query

Send a POST request to `/query`:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why are escalations happening on calls?",
    "conversation_id": "conv_123"
  }'
```

Or using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "Why are escalations happening on calls?",
        "conversation_id": "conv_123"
    }
)

result = response.json()
print(result['response'])
print(f"Evidence count: {result['metadata']['evidence_count']}")
```

### Task 2: Follow-Up Query

Send a POST request to `/query/follow-up`:

```bash
curl -X POST "http://localhost:8000/query/follow-up" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What patterns lead to these escalations?",
    "conversation_id": "conv_123"
  }'
```

Or using Python:

```python
response = requests.post(
    "http://localhost:8000/query/follow-up",
    json={
        "query": "What patterns lead to these escalations?",
        "conversation_id": "conv_123"
    }
)

result = response.json()
print(result['response'])
```

## Python API Usage

### Basic Usage

```python
from src.system import System

# Initialize system
system = System()

# Process a query (Task 1)
result = system.process_query(
    query="Why are escalations happening on calls?",
    conversation_id="conv_123"
)

print("Response:", result['response'])
print("Evidence count:", result['metadata']['evidence_count'])
print("Key factors:", result.get('key_factors', []))
```

### Follow-Up Queries (Task 2)

```python
# First query
result1 = system.process_query(
    query="Why are escalations happening on calls?",
    conversation_id="conv_123"
)

# Follow-up query (uses context from first query)
result2 = system.process_followup(
    query="What patterns lead to these escalations?",
    conversation_id="conv_123"
)

print("Follow-up response:", result2['explanation'])
print("Context used:", result2['context_used'])
```

### Advanced Usage

```python
from src.system import System

# Initialize with custom configuration
system = System(
    vector_db_path="./data/processed/vector_db",
    embedding_model="all-MiniLM-L6-v2",
    llm_provider="gemini",  # or "openai", "anthropic"
    llm_model="gemini-pro"  # or "gpt-4", "claude-3-opus-20240229"
)

# Process query
result = system.process_query(
    query="Why are refund requests increasing?",
    conversation_id="conv_456"
)

# Access detailed results
print("Full explanation:", result['full_explanation'])
print("Evidence spans:", len(result['evidence']))
print("Citations:", result['citations'])

# Access evidence details
for i, evidence in enumerate(result['evidence'][:5], 1):
    print(f"\nEvidence {i}:")
    print(f"  Text: {evidence['text'][:200]}...")
    print(f"  Score: {evidence['evidence_score']:.2f}")
    print(f"  Transcript: {evidence['metadata']['transcript_id']}")
```

## Generating Query Dataset

To generate a query dataset with system outputs:

```bash
python scripts/generate_dataset.py
```

This will:
- Generate 50-100 queries across different event types
- Process queries through the system
- Generate follow-up queries
- Save results to `data/queries/dataset.csv`

The generated dataset includes:
- Query IDs
- Query text
- Query categories (task, difficulty, use case)
- System outputs
- Evidence counts
- Remarks

## Examples

### Example 1: Simple Query

```python
from src.system import System

system = System()

# Query about escalations
result = system.process_query(
    query="Why are escalations happening on calls?",
    conversation_id="example_1"
)

print("=== Response ===")
print(result['response'])
print("\n=== Evidence ===")
for i, ev in enumerate(result['evidence'][:3], 1):
    print(f"{i}. {ev['text'][:150]}...")
```

### Example 2: Multi-Turn Conversation

```python
from src.system import System

system = System()
conv_id = "example_2"

# Initial query
q1 = "What causes refund requests?"
r1 = system.process_query(q1, conversation_id=conv_id)
print("Q1:", q1)
print("A1:", r1['response'][:200] + "...\n")

# Follow-up 1
q2 = "What patterns are common in these cases?"
r2 = system.process_followup(q2, conversation_id=conv_id)
print("Q2:", q2)
print("A2:", r2['explanation'][:200] + "...\n")

# Follow-up 2
q3 = "How can we prevent them?"
r3 = system.process_followup(q3, conversation_id=conv_id)
print("Q3:", q3)
print("A3:", r3['explanation'][:200] + "...")
```

### Example 3: Event-Specific Analysis

```python
from src.system import System

system = System()

# Different event types
queries = [
    "Why are escalations happening?",
    "What leads to refund requests?",
    "What causes customer churn?"
]

for query in queries:
    result = system.process_query(query, conversation_id="example_3")
    print(f"\nQuery: {query}")
    print(f"Response: {result['response'][:150]}...")
    print(f"Event type: {result['metadata'].get('event_type', 'unknown')}")
```

## Troubleshooting

### Issue: API Key Not Found

**Error**: `ValueError: Gemini API key not provided`

**Solution**: Make sure your `.env` file contains the API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

### Issue: No Transcripts Found

**Error**: `FileNotFoundError: Transcript file not found`

**Solution**: 
1. Check that transcript files are in `data/raw/`
2. Verify file format matches expected structure
3. Run data processing script first

### Issue: Vector Database Empty

**Error**: No results returned from queries

**Solution**: 
1. Process transcripts with `--index` flag
2. Check that vector database was created in `data/processed/vector_db`
3. Verify transcripts contain relevant content

### Issue: Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: 
1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.9+)

## Next Steps

1. **Process Your Data**: Use `scripts/process_data.py` to index your transcripts
2. **Test Queries**: Try different query types and event types
3. **Generate Dataset**: Create evaluation dataset with `scripts/generate_dataset.py`
4. **Evaluate**: Use evaluation framework to assess system performance
5. **Customize**: Adjust model parameters, weights, and thresholds as needed

## Additional Resources

- See `README.md` for system architecture details
- Check `report/main.tex` for technical documentation
- Review `presentation/main.tex` for system overview

