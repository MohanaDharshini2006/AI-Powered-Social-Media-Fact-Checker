import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize FastAPI app
app = FastAPI(title="Fact Checker API", version="1.0.0")

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Lazy-load REBEL model
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = None
model = None
knowledge_graph = None
all_triples = []

logger.info(f"🖥️  Device: {device}")
logger.info("📦 Models will be loaded on first API call (lazy loading)")

# ✅ Function to load models on demand
def load_models():
    global tokenizer, model
    if tokenizer is None:
        logger.info("🔄 Loading REBEL model... (first call only, may take a few minutes)")
        tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
        model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large").to(device)
        logger.info("✅ REBEL model loaded successfully!")

# ✅ Pydantic models
class TextInput(BaseModel):
    text: str

class FactCheckInput(BaseModel):
    statement: str

class FactCheckResponse(BaseModel):
    statement: str
    result: str  # "SUPPORTED", "CONTRADICTED", "UNKNOWN"
    confidence: float
    supporting_triples: List[tuple]
    explanation: str

# ✅ Triple extractor
def extract_triplets(text):
    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation:
                triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation:
                triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject and relation and object_:
        triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
    return triplets

# ✅ Generate triples from long input text
def generate_triples(input_text):
    load_models()
    sentences = input_text.strip().split('.')
    triples = []

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        model_inputs = tokenizer(sent, max_length=512, padding=True, truncation=True, return_tensors='pt')
        model_inputs = {k: v.to(device) for k, v in model_inputs.items()}

        generated_tokens = model.generate(
            model_inputs["input_ids"],
            attention_mask=model_inputs["attention_mask"],
            max_length=256,
            num_beams=3,
            num_return_sequences=1
        )

        decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)
        for pred in decoded_preds:
            triplets = extract_triplets(pred)
            for t in triplets:
                triples.append((t['head'], t['type'], t['tail']))
    return triples

# ✅ Build Knowledge Graph
def build_kg(triples):
    G = nx.DiGraph()
    for subj, rel, obj in triples:
        G.add_node(subj, label='Entity')
        G.add_node(obj, label='Entity')
        G.add_edge(subj, obj, relation=rel)
    return G

# ✅ Similarity check using simple string matching
def calculate_similarity(str1, str2):
    str1_lower = str1.lower().strip()
    str2_lower = str2.lower().strip()
    
    # Exact match
    if str1_lower == str2_lower:
        return 1.0
    
    # Substring match
    if str1_lower in str2_lower or str2_lower in str1_lower:
        return 0.8
    
    # Word overlap
    words1 = set(str1_lower.split())
    words2 = set(str2_lower.split())
    if words1 and words2:
        overlap = len(words1 & words2) / len(words1 | words2)
        return overlap
    
    return 0.0

# ✅ Fact Checking Logic
def fact_check(statement: str, triples: List[tuple], threshold: float = 0.6):
    load_models()
    supporting_triples = []
    best_score = 0.0
    
    # Extract entities from statement using model
    model_inputs = tokenizer(statement, max_length=512, padding=True, truncation=True, return_tensors='pt')
    model_inputs = {k: v.to(device) for k, v in model_inputs.items()}
    
    generated_tokens = model.generate(
        model_inputs["input_ids"],
        attention_mask=model_inputs["attention_mask"],
        max_length=256,
        num_beams=3,
        num_return_sequences=1
    )
    
    decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)
    statement_triples = []
    for pred in decoded_preds:
        statement_triples.extend(extract_triplets(pred))
    
    # Check statement triples against knowledge graph
    if statement_triples:
        for stmt_triple in statement_triples:
            stmt_subj = stmt_triple['head']
            stmt_rel = stmt_triple['type']
            stmt_obj = stmt_triple['tail']
            
            for kb_subj, kb_rel, kb_obj in triples:
                # Calculate similarity scores
                subj_sim = calculate_similarity(stmt_subj, kb_subj)
                rel_sim = calculate_similarity(stmt_rel, kb_rel)
                obj_sim = calculate_similarity(stmt_obj, kb_obj)
                
                # Combined score (weighted)
                combined_score = (subj_sim * 0.3 + rel_sim * 0.4 + obj_sim * 0.3)
                
                if combined_score > best_score:
                    best_score = combined_score
                    
                if combined_score >= threshold:
                    supporting_triples.append((kb_subj, kb_rel, kb_obj))
    
    # Determine result
    if best_score >= 0.85:
        result = "SUPPORTED"
        explanation = "This statement is strongly supported by the knowledge graph."
    elif best_score >= threshold:
        result = "SUPPORTED"
        explanation = "This statement is supported by the knowledge graph with moderate confidence."
    elif best_score >= 0.3:
        result = "UNKNOWN"
        explanation = "Partial match found. The statement is partially supported by the knowledge graph."
    else:
        result = "UNKNOWN"
        explanation = "No matching information found in the knowledge graph."
    
    return {
        "result": result,
        "confidence": round(best_score, 3),
        "supporting_triples": supporting_triples[:5],  # Top 5 supporting triples
        "explanation": explanation
    }

# ✅ API Endpoints

@app.post("/api/build-kg")
async def build_knowledge_graph(data: TextInput):
    """Build knowledge graph from input text"""
    global knowledge_graph, all_triples
    try:
        all_triples = generate_triples(data.text)
        knowledge_graph = build_kg(all_triples)
        
        return {
            "status": "success",
            "message": f"Knowledge graph built with {len(all_triples)} triples",
            "triples_count": len(all_triples),
            "nodes_count": knowledge_graph.number_of_nodes(),
            "edges_count": knowledge_graph.number_of_edges()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/fact-check", response_model=FactCheckResponse)
async def fact_check_endpoint(data: FactCheckInput):
    """Check if a statement is supported by the knowledge graph"""
    global all_triples
    
    if not all_triples:
        raise HTTPException(status_code=400, detail="Knowledge graph not built. Please build KG first.")
    
    try:
        result = fact_check(data.statement, all_triples)
        return FactCheckResponse(
            statement=data.statement,
            result=result["result"],
            confidence=result["confidence"],
            supporting_triples=result["supporting_triples"],
            explanation=result["explanation"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/kg-stats")
async def get_kg_stats():
    """Get knowledge graph statistics"""
    global knowledge_graph, all_triples
    
    if not knowledge_graph:
        raise HTTPException(status_code=400, detail="Knowledge graph not built yet.")
    
    return {
        "nodes": knowledge_graph.number_of_nodes(),
        "edges": knowledge_graph.number_of_edges(),
        "triples": len(all_triples),
        "triples_sample": all_triples[:10]
    }

@app.get("/api/triples")
async def get_all_triples():
    """Get all extracted triples"""
    global all_triples
    
    if not all_triples:
        raise HTTPException(status_code=400, detail="No triples extracted yet.")
    
    return {"triples": all_triples}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "model": "REBEL", "device": device, "models_loaded": tokenizer is not None}

if __name__ == "__main__":
    print("🚀 Starting REBEL Fact Checker Backend...")
    print("📍 Backend will be available at http://localhost:8000")
    print("⏳ Loading REBEL model on first startup (this may take a few minutes)...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
