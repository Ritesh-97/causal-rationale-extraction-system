# Full-Scale Testing Instructions

## Quick Start

### Option 1: Automated Setup and Test (Recommended)

```bash
# Run the automated setup and test script
./scripts/setup_and_test.sh
```

This script will:
1. Check Python version
2. Create virtual environment (if needed)
3. Install all dependencies
4. Check for API keys
5. Run full-scale testing

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Set Up API Key

```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=AIzaSyDceW1Y6h66LooX7kwZnZLLiRD7ffJkalo
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-2.5-pro
VECTOR_DB_PATH=./data/processed/vector_db
EOF
```

#### Step 4: Run Full-Scale Test

```bash
python scripts/full_scale_test.py
```

## What the Test Does

The full-scale test script performs:

1. **Data Processing** (Step 1)
   - Loads dummy transcripts from `data/raw/dummy_transcripts.json`
   - Preprocesses and normalizes data
   - Extracts dialogue spans
   - Indexes spans to vector database
   - Expected: ~10,000 transcripts processed

2. **System Initialization** (Step 2)
   - Initializes all system components
   - Sets up retrieval pipeline
   - Configures LLM integration

3. **Basic Query Testing** (Step 3)
   - Tests 3 sample queries:
     - "Why are escalations happening on calls?"
     - "What causes refund requests?"
     - "What leads to customer churn?"
   - Verifies responses and evidence retrieval

4. **Follow-Up Query Testing** (Step 4)
   - Tests contextual follow-up conversations
   - Verifies context management
   - Tests multi-turn dialogue handling

5. **Query Dataset Generation** (Step 5)
   - Generates 30+ queries across event types
   - Includes follow-up queries
   - Saves to `data/queries/dataset.csv`

## Expected Output

```
======================================================================
  Full-Scale Testing - Causal Rationale Extraction System
======================================================================

[1/5] Processing and indexing transcript data...
✓ Processed 10000 transcripts
✓ Indexed dialogue spans to vector database
✓ Total dialogue spans: ~127,000
✓ Total events: ~2,000

[2/5] Initializing system...
✓ System initialized successfully

[3/5] Testing basic queries...
  Testing query 1: Why are escalations happening on calls?...
    ✓ Response length: 500 chars
    ✓ Evidence count: 10
  Testing query 2: What causes refund requests?...
    ✓ Response length: 450 chars
    ✓ Evidence count: 8
  Testing query 3: What leads to customer churn?...
    ✓ Response length: 480 chars
    ✓ Evidence count: 9

✓ Successfully processed 3/3 queries

[4/5] Testing follow-up queries...
  Initial query: Why are escalations happening on calls?
    ✓ Initial response generated
  Follow-up query: What patterns lead to these escalations?
    ✓ Follow-up response generated
    ✓ Context used: True

[5/5] Generating query dataset...
  Generating queries for event types: escalation, refund, churn
  ✓ Generated dataset with 60 queries
  ✓ Saved to: data/queries/dataset.csv
  ✓ Task 1 queries: 30
  ✓ Task 2 queries: 30
  ✓ Escalation queries: 20
  ✓ Refund queries: 20
  ✓ Churn queries: 20

======================================================================
  Testing Complete
======================================================================
Total time: 120.45 seconds (2.01 minutes)
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Install dependencies in virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: API Key Not Found

**Solution**: Create `.env` file with your API key:
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

### Issue: No Transcripts Found

**Solution**: Generate dummy data first:
```bash
python scripts/generate_dummy_data.py
```

### Issue: Vector Database Errors

**Solution**: Clear and rebuild vector database:
```bash
rm -rf data/processed/vector_db
python scripts/process_data.py --input data/raw --pattern "*.json" --index
```

## Testing Individual Components

### Test Data Processing Only

```bash
python scripts/process_data.py --input data/raw --pattern "dummy_transcripts.json" --index
```

### Test System with Single Query

```bash
python quick_start.py
```

### Test API Server

```bash
# Terminal 1: Start server
python -m src.main

# Terminal 2: Test endpoint
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why are escalations happening?", "conversation_id": "test"}'
```

## Performance Expectations

- **Data Processing**: ~2-5 minutes for 10,000 transcripts
- **Query Processing**: ~5-10 seconds per query (with LLM)
- **Dataset Generation**: ~10-20 minutes for 60 queries
- **Total Test Time**: ~15-30 minutes

## Next Steps After Testing

1. **Review Results**: Check `data/queries/dataset.csv` for generated queries
2. **Run Evaluations**: Use evaluation framework to assess performance
3. **Customize**: Adjust parameters, weights, and thresholds
4. **Deploy**: Start API server for production use

