# Causal Rationale Extraction and Synthesis System

A system for extracting causal rationales from conversational data to identify relationships between dialogue dynamics and business events (escalations, refunds, churn).

## Overview

This system processes large-scale conversational transcripts to:
- Answer natural-language queries about business events with evidence-based explanations (Task 1)
- Support contextual follow-up conversations (Task 2)

## Project Structure

```
.
├── docker/              # Docker configuration files
├── src/                 # Source code
│   ├── data_processing/ # Transcript ingestion and preprocessing
│   ├── retrieval/       # Semantic search and reranking
│   ├── causal_analysis/ # Causal pattern detection
│   ├── query_processing/# Query understanding
│   ├── explanation_generation/ # LLM-based explanation generation
│   ├── conversation_manager/  # Context tracking
│   └── evaluation/      # Evaluation metrics and baselines
├── data/                # Data directories
│   ├── raw/            # Raw transcripts
│   ├── processed/      # Processed data and vector DB
│   └── queries/        # Query datasets
├── models/             # Model files (if custom training)
├── notebooks/          # Jupyter notebooks for experimentation
├── tests/              # Unit tests
├── report/             # LaTeX technical report
└── presentation/       # Presentation materials
```

## Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. Clone the repository (if applicable)

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Docker Setup

1. Build the Docker image:
```bash
docker-compose -f docker/docker-compose.yml build
```

2. Run the container:
```bash
docker-compose -f docker/docker-compose.yml up
```

The API will be available at `http://localhost:8000`

## Usage

### Data Processing

1. Process transcript data:
```bash
python scripts/process_data.py --input data/raw --output data/processed --pattern "*.json" --index
```

This will:
- Load transcripts from `data/raw`
- Preprocess and extract dialogue spans
- Index spans to vector database (if `--index` flag is used)

### Query Dataset Generation

Generate a query dataset with system outputs:
```bash
python scripts/generate_dataset.py
```

This will:
- Generate 50-100 queries across different event types
- Process queries through the system
- Generate follow-up queries
- Save results to `data/queries/dataset.csv`

### API Endpoints

Start the API server:
```bash
python -m src.main
# or
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Available endpoints:
- `GET /` - API information
- `GET /health` - Health check
- `POST /query` - Process a query (Task 1 or Task 2)
- `POST /query/follow-up` - Process a follow-up query (Task 2)

### Example API Request

**Task 1 - Initial Query:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "Why are escalations happening on calls?",
        "conversation_id": "conv_123"
    }
)
print(response.json())
```

**Task 2 - Follow-up Query:**
```python
response = requests.post(
    "http://localhost:8000/query/follow-up",
    json={
        "query": "What patterns lead to these escalations?",
        "conversation_id": "conv_123"
    }
)
print(response.json())
```

### Python API Usage

```python
from src.system import System

# Initialize system
system = System()

# Process a query (Task 1)
result = system.process_query(
    query="Why are escalations happening on calls?",
    conversation_id="conv_123"
)

print(result['response'])
print(f"Evidence count: {result['metadata']['evidence_count']}")

# Process a follow-up (Task 2)
followup_result = system.process_followup(
    query="What patterns lead to these escalations?",
    conversation_id="conv_123"
)

print(followup_result['explanation'])
```

## System Architecture

### Core Components

1. **Data Processing Pipeline**
   - Transcript loading and parsing (JSON, CSV, TXT)
   - Preprocessing and normalization
   - Dialogue span extraction
   - Vector database indexing

2. **Retrieval System**
   - Semantic search using sentence transformers
   - Reranking with cross-encoders
   - Event-specific retrieval strategies
   - Context-aware retrieval

3. **Causal Analysis**
   - Pattern detection (temporal, sequential, behavioral)
   - Evidence scoring and ranking
   - Causal span extraction

4. **Explanation Generation**
   - LLM-based explanation synthesis
   - Evidence citation and linking
   - Structured output formatting

5. **Conversation Management**
   - Context tracking across turns
   - Follow-up question detection
   - Contextual response generation

6. **Evaluation Framework**
   - Query simulation and generation
   - Evaluation metrics
   - Baseline comparisons
   - Ablation studies

## Configuration

### Environment Variables

Create a `.env` file with:
```bash
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-pro
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002
VECTOR_DB_PATH=./data/processed/vector_db
```

### Model Configuration

The system supports multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google Gemini (gemini-pro, gemini-pro-vision)
- Open-source models (via transformers)

Default models can be configured in `.env` or when initializing the System class.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

## Evaluation

### Metrics

The system includes evaluation metrics for:
- Response quality (length, coherence, citations)
- Evidence quality (relevance, coverage, diversity)
- Causal explanation quality (causal language, completeness)
- Conversational coherence (context usage, references)

### Baselines

Three baseline methods are included:
- Keyword search
- Simple RAG (without reranking)
- Rule-based pattern matching

### Ablation Studies

The evaluation framework supports ablation studies by removing components:
- Retrieval
- Reranking
- Causal analysis
- LLM generation

## Dataset Format

### Transcript Format

**JSON:**
```json
{
  "transcript_id": "call_123",
  "turns": [
    {
      "turn_id": 1,
      "speaker": "agent",
      "text": "Hello, how can I help you?",
      "timestamp": 0.0
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

**CSV:**
Columns: `transcript_id`, `turn_id`, `speaker`, `text`, `timestamp`, `event_type`, `event_label`

### Query Dataset Format

The generated query dataset (CSV) includes:
- `Query_Id`: Unique identifier
- `Query`: Query text
- `Query_Category`: Categorization (task, difficulty, use_case)
- `System_Output`: System response
- `Remarks`: Additional notes
- `Task`: Task 1 or Task 2
- `Difficulty`: Simple, complex, or multi_hop
- `Use_Case`: Agent behavior, product feedback, etc.
- `Event_Type`: Escalation, refund, churn, etc.
- `Is_Followup`: Boolean
- `Evidence_Count`: Number of evidence spans

## License

See problem statement for IP rights and usage terms.

