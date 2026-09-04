# 📚 Knowledge Graph Fact Checker Web App

A comprehensive web application that extracts knowledge graphs from text using the REBEL model and provides real-time fact-checking capabilities.

## Features

✅ **Knowledge Graph Building**
- Automatically extracts relationships (triplets) from input text
- Uses the REBEL-large transformer model for high-quality extraction
- Supports long documents by processing sentence by sentence

✅ **Fact Checking**
- Verifies user statements against the built knowledge graph
- Provides confidence scores (0-1)
- Shows supporting triplets and detailed explanations
- Three-level results: SUPPORTED, UNKNOWN, CONTRADICTED

✅ **Interactive Web Interface**
- Beautiful, responsive frontend built with vanilla HTML/CSS/JS
- Real-time statistics and visualization
- Tab-based view for statistics and all extracted triples
- Mobile-friendly design

✅ **RESTful API**
- FastAPI backend with CORS support
- Multiple endpoints for KG building, fact-checking, and stats
- Health check endpoint

## Project Structure

```
fact_checker/
├── backend.py          # FastAPI backend with REBEL model integration
├── index.html          # Interactive frontend
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Backend

```bash
python backend.py
```

The API will start at `http://localhost:8000`

### 3. Open the Frontend

Open `index.html` in your web browser or serve it with a simple HTTP server:

```bash
# Option 1: Using Python
python -m http.server 8080

# Option 2: Using Node.js
npx http-server

# Option 3: Direct file access
# Simply open index.html in your browser
```

Visit `http://localhost:8080` (or your chosen port) to access the web app.

## How to Use

### Step 1: Build Knowledge Graph
1. Paste your text in the "Enter Text" field
2. Click "🔨 Build Knowledge Graph"
3. The system will extract relationships and display statistics

### Step 2: Fact Check Statements
1. Enter a statement in the "Enter Statement to Verify" field
2. Click "✅ Check Statement"
3. View the result with confidence score and supporting evidence

### Step 3: View Statistics
- **Stats Tab**: Shows node count, edge count, and total triples
- **All Triples Tab**: Lists all extracted relationships

## API Endpoints

### 1. Build Knowledge Graph
```
POST /api/build-kg
Content-Type: application/json

{
  "text": "Your text here..."
}

Response:
{
  "status": "success",
  "message": "Knowledge graph built with X triples",
  "triples_count": 100,
  "nodes_count": 150,
  "edges_count": 100
}
```

### 2. Fact Check Statement
```
POST /api/fact-check
Content-Type: application/json

{
  "statement": "Elon Musk is the CEO of Tesla"
}

Response:
{
  "statement": "Elon Musk is the CEO of Tesla",
  "result": "SUPPORTED",
  "confidence": 0.95,
  "supporting_triples": [
    ["Elon Musk", "CEO", "Tesla"]
  ],
  "explanation": "This statement is strongly supported by the knowledge graph."
}
```

### 3. Get KG Statistics
```
GET /api/kg-stats

Response:
{
  "nodes": 150,
  "edges": 100,
  "triples": 100,
  "triples_sample": [...]
}
```

### 4. Get All Triples
```
GET /api/triples

Response:
{
  "triples": [
    ["Elon Musk", "CEO", "Tesla"],
    ["Tesla", "headquartered_in", "California"]
  ]
}
```

### 5. Health Check
```
GET /health

Response:
{
  "status": "ok",
  "model": "REBEL",
  "device": "cuda" or "cpu"
}
```

## How Fact Checking Works

The fact-checking system uses a multi-step approach:

1. **Statement Processing**: Uses REBEL model to extract relationships from the user's statement
2. **Similarity Matching**: Compares extracted relationships with knowledge graph using:
   - Exact matching (score: 1.0)
   - Substring matching (score: 0.8)
   - Word overlap analysis (score: 0-1)
3. **Confidence Scoring**: Calculates weighted scores:
   - Subject similarity: 30%
   - Relation similarity: 40%
   - Object similarity: 30%
4. **Result Classification**:
   - **SUPPORTED**: Confidence ≥ 0.85 or above threshold (0.6)
   - **UNKNOWN**: Confidence between 0.3 and threshold
   - **CONTRADICTED**: No supporting evidence

## Example Usage

```python
# Sample text with relationships
text = """
Elon Musk is the CEO of Tesla. He also founded SpaceX.
Steve Jobs co-founded Apple with Steve Wozniak.
Sundar Pichai leads Google.
"""

# The system will extract:
# - (Elon Musk, CEO, Tesla)
# - (Elon Musk, founded, SpaceX)
# - (Steve Jobs, co-founded, Apple)
# - (Steve Wozniak, co-founded, Apple)
# - (Sundar Pichai, leads, Google)

# Then verify statements like:
# "Is Elon Musk the CEO of Tesla?" → SUPPORTED (confidence: 0.95)
# "Did Steve Jobs found Apple?" → SUPPORTED (confidence: 0.90)
# "Is Elon Musk the CEO of Google?" → UNKNOWN (confidence: 0.15)
```

## Performance Notes

- **First Run**: Will download the REBEL model (~2GB) on first use
- **GPU Support**: Uses CUDA if available, falls back to CPU
- **Processing Time**: ~5-10 seconds per paragraph (varies by hardware)
- **Batch Processing**: Handles long documents by processing sentences individually

## Requirements

- Python 3.8+
- PyTorch (with CUDA support optional)
- Transformers library (REBEL model)
- FastAPI & Uvicorn
- NetworkX

## Troubleshooting

### CORS Issues
If you get CORS errors, ensure the backend is running with CORS enabled (it's enabled by default).

### Model Not Loading
First run downloads the REBEL model. Ensure you have ~2GB free disk space and internet connection.

### Port Already in Use
If port 8000 is in use, modify the last line in `backend.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Slow Processing
- Use GPU if available (CUDA)
- Reduce input text length
- Increase `num_beams` parameter in generation for faster but less accurate results

## Future Enhancements

- [ ] Graph visualization with D3.js
- [ ] Entity linking and disambiguation
- [ ] Multi-language support
- [ ] Knowledge graph persistence (save/load)
- [ ] Advanced query interface
- [ ] Confidence calibration
- [ ] User authentication and history
- [ ] Batch fact-checking

## License

MIT License

## Author

Created for advanced knowledge graph fact-checking application
