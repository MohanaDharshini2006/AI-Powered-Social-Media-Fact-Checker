# Quick Start Guide

## Running the Application

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend
```bash
python backend.py
```
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Serve the Frontend
In a new terminal, navigate to the project folder:
```bash
# Option A: Python HTTP server
python -m http.server 8080

# Option B: Node.js HTTP server
npx http-server

# Option C: Just open index.html in browser
open index.html
```

### Step 4: Access the App
- If using HTTP server: http://localhost:8080
- If opening directly: Open the index.html file in your browser

## Test Data

Copy and paste this into the "Enter Text" field to test:

```
Elon Musk is the CEO of Tesla. He also founded SpaceX. Steve Jobs co-founded Apple with Steve Wozniak.
Sundar Pichai leads Google, a company headquartered in Mountain View, California. Barack Obama was born in Hawaii and served as the 44th President of the United States.
Bill Gates founded Microsoft and donated billions through the Bill & Melinda Gates Foundation. Mark Zuckerberg created Facebook during his time at Harvard University.
Marie Curie discovered radium and polonium. Albert Einstein developed the theory of relativity in 1905.
Tim Berners-Lee invented the World Wide Web. Nikola Tesla worked with Thomas Edison before they had a falling out.
```

## Test Statements

After building the KG, try these statements:

✅ "Elon Musk is the CEO of Tesla"
✅ "Steve Jobs founded Apple"
❓ "Elon Musk invented the World Wide Web"
✅ "Albert Einstein developed the theory of relativity"

## Troubleshooting

**Port 8000 in use?**
```bash
python backend.py --port 8001
# Update API_URL in index.html to http://localhost:8001
```

**Module not found?**
```bash
pip install --upgrade -r requirements.txt
```

**Slow/Hanging?**
- First load downloads REBEL model (~2GB)
- Be patient - it may take 5-10 minutes on first run
- GPU acceleration recommended for faster processing
