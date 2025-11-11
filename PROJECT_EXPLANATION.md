# Project Explanation: Causal Rationale Extraction System

## What is This Project About?

This project is a **Causal Rationale Extraction and Synthesis System** designed to analyze large-scale customer service conversations (call transcripts) and answer questions about **why business events happen**.

### The Problem It Solves

Imagine a customer service center that handles thousands of calls daily. Some calls result in:
- **Escalations** (customer asks for a supervisor)
- **Refunds** (customer requests money back)
- **Churn** (customer cancels service)

Currently, systems can detect that these events occurred, but they can't explain **why** they happened. This project solves that by:

1. **Analyzing conversation transcripts** to find patterns
2. **Identifying causal relationships** between dialogue and events
3. **Answering questions** like "Why are escalations happening?" with evidence-based explanations
4. **Supporting follow-up conversations** for deeper analysis

---

## The Two Main Tasks

### Task 1: Evidence-Based Causal Explanations
When you ask: *"Why are escalations happening on calls?"*

The system:
- Searches through thousands of transcripts
- Finds dialogue spans that likely caused escalations
- Generates an explanation with evidence citations
- Shows you specific conversation segments that led to the event

### Task 2: Contextual Follow-Up Conversations
After getting an initial answer, you can ask follow-ups like:
- *"What patterns lead to these escalations?"*
- *"Which agent behaviors cause refunds?"*

The system remembers the previous conversation and provides contextual answers.

---

## How the Code Works: System Architecture

The system is built with **6 main components** that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                               │
│         "Why are escalations happening?"                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           1. DATA PROCESSING PIPELINE                       │
│  • Loads transcripts (JSON/CSV/TXT)                         │
│  • Preprocesses text (cleaning, normalization)             │
│  • Extracts dialogue spans (sliding windows of 5 turns)     │
│  • Indexes spans into vector database (ChromaDB)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           2. RETRIEVAL SYSTEM                              │
│  • Semantic Search: Finds relevant dialogue spans          │
│    using sentence transformers (all-MiniLM-L6-v2)           │
│  • Reranking: Refines results using cross-encoder           │
│    (ms-marco-MiniLM-L-6-v2)                                │
│  • Event-Specific Filtering: Focuses on relevant events     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           3. CAUSAL ANALYSIS                                │
│  • Pattern Detection: Finds temporal, sequential,            │
│    behavioral patterns                                      │
│  • Evidence Scoring: Ranks spans by causal relevance        │
│    (40% relevance + 30% temporal + 20% pattern + 10% sim) │
│  • Causal Span Extraction: Identifies spans that             │
│    likely caused the event                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           4. EXPLANATION GENERATION                         │
│  • LLM Integration: Uses Gemini/OpenAI/Claude               │
│  • Synthesizes evidence into coherent explanation           │
│  • Adds citations to specific dialogue spans                │
│  • Formats structured output                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           5. CONVERSATION MANAGEMENT                        │
│  • Context Tracking: Remembers previous queries              │
│  • Follow-Up Detection: Identifies follow-up questions     │
│  • Contextual Response: Uses conversation history           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           6. QUERY PROCESSING                               │
│  • Task 1 Processor: Handles initial queries                │
│  • Task 2 Processor: Handles follow-up queries             │
│  • Query Parser: Extracts event types, intent               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                            │
│  • Explanation with evidence                                 │
│  • List of relevant dialogue spans                           │
│  • Metadata (evidence count, confidence scores)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Breakdown

### 1. Data Processing Pipeline (`src/data_processing/`)

**What it does:**
- Takes raw transcript files and prepares them for analysis
- Converts conversations into searchable chunks

**Key Files:**
- `transcript_loader.py`: Loads transcripts from JSON/CSV/TXT files
- `preprocessor.py`: Cleans text, normalizes speaker labels, segments turns
- `pipeline.py`: Orchestrates the entire data processing workflow
- `vector_store.py`: Manages ChromaDB vector database for fast retrieval

**How it works:**
1. Loads transcript: `{"transcript_id": "call_123", "turns": [...], "events": [...]}`
2. Preprocesses: Normalizes speakers, cleans text
3. Extracts spans: Creates sliding windows of 5 turns each
   - Example: Turns 1-5, 2-6, 3-7, etc.
4. Indexes to vector DB: Stores each span with embeddings for fast search

**Example:**
```python
# Input: Transcript with 20 turns
# Output: ~16 dialogue spans (each 5 turns, sliding window)
# Each span is indexed in ChromaDB with:
# - Text content
# - Turn IDs
# - Speaker information
# - Event associations (if any)
```

---

### 2. Retrieval System (`src/retrieval/`)

**What it does:**
- Finds the most relevant dialogue spans for a query
- Uses a two-stage approach: semantic search + reranking

**Key Files:**
- `semantic_search.py`: Uses sentence transformers to find similar spans
- `reranker.py`: Refines results using cross-encoder for better precision
- `retrieval_pipeline.py`: Orchestrates the retrieval process
- `span_extractor.py`: Extracts spans around events for causal analysis

**How it works:**
1. **Semantic Search (Stage 1):**
   - Converts query to embedding vector
   - Searches vector database for similar spans
   - Returns top 20 candidates

2. **Reranking (Stage 2):**
   - Uses cross-encoder to score query-span pairs
   - Reranks candidates for better precision
   - Returns top 10 most relevant spans

**Example:**
```python
Query: "Why are escalations happening?"
→ Semantic search finds 20 candidate spans
→ Reranker scores and ranks them
→ Returns top 10 most relevant spans with scores
```

---

### 3. Causal Analysis (`src/causal_analysis/`)

**What it does:**
- Identifies which dialogue spans likely caused events
- Scores evidence based on multiple factors
- Detects patterns (temporal, sequential, behavioral)

**Key Files:**
- `causal_analyzer.py`: Main causal analysis engine
- `pattern_detector.py`: Detects temporal/sequential patterns
- `evidence_scorer.py`: Scores and ranks evidence spans

**How it works:**
1. **Pattern Detection:**
   - **Temporal**: Spans that occur before events
   - **Sequential**: Consecutive causal relationships
   - **Behavioral**: Frustration cues, repetition, hesitation
   - **Event-Specific**: Known triggers for escalations/refunds/churn

2. **Evidence Scoring:**
   - **Relevance (40%)**: How relevant is the span to the query?
   - **Temporal (30%)**: How close is it to the event?
   - **Pattern (20%)**: Does it match known causal patterns?
   - **Similarity (10%)**: Semantic similarity to query

3. **Ranking:**
   - Combines all scores
   - Ranks spans by causal likelihood
   - Returns top-k most likely causal spans

**Example:**
```python
Event: Escalation at turn 15
Query: "Why did this escalation happen?"

Causal Analysis:
- Finds spans 5-14 (before event)
- Detects pattern: Customer frustration at turn 10
- Scores: Relevance=0.8, Temporal=0.9, Pattern=0.7
- Final score: 0.8*0.4 + 0.9*0.3 + 0.7*0.2 = 0.79
- Ranks as #1 causal span
```

---

### 4. Explanation Generation (`src/explanation_generation/`)

**What it does:**
- Synthesizes evidence into human-readable explanations
- Uses Large Language Models (LLMs) to generate coherent responses
- Adds citations to specific dialogue spans

**Key Files:**
- `explanation_generator.py`: Orchestrates explanation generation
- `llm_generator.py`: Interfaces with LLM providers (Gemini/OpenAI/Claude)

**How it works:**
1. Takes top-k causal spans from retrieval + causal analysis
2. Formats evidence for LLM
3. Generates prompt like:
   ```
   Query: "Why are escalations happening?"
   Evidence:
   - Span 1: Customer says "I want to speak to a manager" (turn 10)
   - Span 2: Agent repeats same response 3 times (turns 7-9)
   - Span 3: Customer expresses frustration (turn 8)
   
   Generate an explanation with citations.
   ```
4. LLM generates coherent explanation with evidence citations
5. Returns formatted response

**Example Output:**
```
Escalations are primarily caused by:
1. Agent response repetition (Span 2, turns 7-9): When agents 
   repeat the same response multiple times, customers become 
   frustrated and request supervisors.
2. Customer frustration cues (Span 3, turn 8): Expressions of 
   frustration often precede escalation requests.
3. Direct supervisor requests (Span 1, turn 10): Customers 
   explicitly requesting managers indicates breakdown in 
   agent-customer communication.
```

---

### 5. Conversation Management (`src/conversation_manager/`)

**What it does:**
- Tracks conversation context across multiple queries
- Enables follow-up questions
- Maintains conversation history

**Key Files:**
- `context_manager.py`: Stores and retrieves conversation context
- `followup_processor.py`: Processes follow-up queries with context

**How it works:**
1. **Initial Query:**
   - User asks: "Why are escalations happening?"
   - System processes and stores context

2. **Follow-Up Query:**
   - User asks: "What patterns lead to these escalations?"
   - System retrieves previous context
   - Uses context to refine retrieval and explanation
   - Generates contextual response

**Example:**
```python
Query 1: "Why are escalations happening?"
→ Context stored: {event_type: "escalation", evidence: [...]}

Query 2: "What patterns lead to these escalations?"
→ Uses context from Query 1
→ Focuses on patterns in escalation-related spans
→ Generates contextual explanation
```

---

### 6. Query Processing (`src/query_processing/`)

**What it does:**
- Parses and understands user queries
- Routes queries to appropriate processors (Task 1 or Task 2)
- Extracts intent, event types, and query characteristics

**Key Files:**
- `query_parser.py`: Parses queries to extract intent and event types
- `task1_processor.py`: Handles initial queries (Task 1)
- `task2_processor.py`: Handles follow-up queries (Task 2)

**How it works:**
1. **Query Parsing:**
   - Extracts event type (escalation/refund/churn)
   - Identifies query intent
   - Determines if it's a follow-up

2. **Task Routing:**
   - Task 1: Initial queries → Task1Processor
   - Task 2: Follow-up queries → Task2Processor

3. **Processing:**
   - Calls appropriate retrieval and explanation components
   - Formats response

---

## Complete Flow Example

Let's trace a complete example:

### Step 1: Data Processing (One-time setup)
```python
# Load 100 transcripts
transcripts = load_transcripts("data/raw/dummy_transcripts.json")

# Process each transcript
for transcript in transcripts:
    # Extract spans (5 turns each)
    spans = extract_spans(transcript, window_size=5)
    
    # Index to vector database
    vector_store.add_transcript_spans(
        transcript_id=transcript['transcript_id'],
        spans=spans,
        events=transcript['events']
    )
```

### Step 2: User Query
```python
query = "Why are escalations happening on calls?"
```

### Step 3: Retrieval
```python
# Semantic search finds 20 candidate spans
candidates = semantic_search(query, top_k=20)

# Rerank to top 10
top_spans = reranker.rerank(query, candidates, top_k=10)
```

### Step 4: Causal Analysis
```python
# Analyze causal patterns
causal_spans = causal_analyzer.analyze_causal_spans(
    spans=top_spans,
    query=query,
    event_type="escalation"
)

# Score and rank evidence
ranked_evidence = evidence_scorer.score_evidence(
    causal_spans,
    weights={
        'relevance': 0.4,
        'temporal': 0.3,
        'pattern': 0.2,
        'similarity': 0.1
    }
)
```

### Step 5: Explanation Generation
```python
# Generate explanation with LLM
explanation = llm_generator.generate_explanation(
    query=query,
    evidence=ranked_evidence[:5],  # Top 5 spans
    context=None
)
```

### Step 6: Response
```python
{
    "response": "Escalations are primarily caused by...",
    "evidence": [
        {
            "span_id": "call_001_span_5",
            "text": "Customer: I want to speak to a manager",
            "score": 0.89,
            "turn_ids": [8, 9, 10]
        },
        ...
    ],
    "metadata": {
        "evidence_count": 5,
        "confidence": 0.85
    }
}
```

---

## Key Technologies Used

1. **Vector Database**: ChromaDB for fast similarity search
2. **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
3. **Reranking**: Cross-encoder models (ms-marco-MiniLM-L-6-v2)
4. **LLMs**: Gemini/OpenAI/Claude for explanation generation
5. **Web Framework**: FastAPI for REST API
6. **Data Processing**: Pandas, NumPy for data manipulation

---

## Project Structure

```
src/
├── data_processing/      # Loads and preprocesses transcripts
├── retrieval/            # Semantic search and reranking
├── causal_analysis/      # Pattern detection and evidence scoring
├── explanation_generation/# LLM-based explanation synthesis
├── conversation_manager/ # Context tracking for follow-ups
├── query_processing/     # Query parsing and routing
├── evaluation/          # Testing and metrics
├── system.py            # Main system orchestrator
└── main.py              # FastAPI web server
```

---

## How to Use the System

### 1. Process Data
```bash
python scripts/process_data.py --input data/raw --pattern "*.json" --index
```

### 2. Start API Server
```bash
python -m src.main
```

### 3. Query the System
```python
from src.system import System

system = System()

# Task 1: Initial query
result = system.process_query(
    query="Why are escalations happening?",
    conversation_id="conv_123"
)

# Task 2: Follow-up query
followup = system.process_followup(
    query="What patterns lead to these escalations?",
    conversation_id="conv_123"
)
```

---

## Summary

This project is a **sophisticated question-answering system** that:

1. **Processes** large-scale conversation transcripts
2. **Indexes** dialogue spans in a vector database
3. **Retrieves** relevant spans for queries
4. **Analyzes** causal relationships between dialogue and events
5. **Generates** evidence-based explanations using LLMs
6. **Supports** contextual follow-up conversations

It's designed to help businesses understand **why** customer service events happen by analyzing the actual conversations that led to those events, providing actionable insights for improving customer service operations.

