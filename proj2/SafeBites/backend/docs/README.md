# SafeBites Documentation

## 📚 Available Documentation

### 1. Chat Flow Architecture
**File**: [CHAT_FLOW.md](CHAT_FLOW.md)

Complete documentation of the LangGraph-based chat processing pipeline including:
- Step-by-step flow explanation
- Mermaid flowchart diagram
- Performance characteristics
- Code references
- Optimization details

### 2. Flowchart Generation

#### Graphviz Script
**File**: [generate_flowchart.py](generate_flowchart.py)

Python script to generate visual flowcharts using Graphviz:
```bash
pip install graphviz
python generate_flowchart.py
```

Outputs:
- `chat_flow.png` - High-resolution PNG image
- `chat_flow.svg` - Scalable vector graphic
- `chat_flow.pdf` - PDF document

#### DOT Source
**File**: [chat_flow.dot](chat_flow.dot)

Graphviz DOT source file for the flowchart. Can be edited directly or used with:
```bash
dot -Tpng chat_flow.dot -o chat_flow.png
```

---

## 🔄 Chat Flow Quick Reference

### Pipeline Overview

```
User Query
    ↓
1. Context Resolver
    ↓
2. Intent Classifier
    ↓
3. Query Part Generator
    ↓
4. Parallel Retrieval
   ├─ 4a. Menu Retriever (FAISS)
   ├─ 4b. Informative Retriever
   └─ 4c. User Preferences Retriever
    ↓
5. Compatibility Scorer (AI-powered, 7 dishes)
    ↓
6. Response Formatter
    ↓
Final Response
```

### Key Features

- ⚡ **Parallel Execution**: Steps 4a/4b/4c run concurrently
- 🤖 **AI-Powered**: GPT-4o-mini for scoring and responses
- 🔍 **Semantic Search**: FAISS vector embeddings
- 🎯 **Cross-Restaurant**: Search across all restaurants
- 🚀 **Optimized**: 7-dish limit, 35-40s response time
- 🛡️ **Safety First**: Allergen safety (40% weight)

---

## 📊 Viewing the Flowchart

### Option 1: Generate with Python
```bash
cd backend/docs
pip install graphviz
python generate_flowchart.py
open chat_flow.png
```

### Option 2: View Mermaid in Markdown
Open [CHAT_FLOW.md](CHAT_FLOW.md) in:
- GitHub (renders automatically)
- VS Code (with Mermaid extension)
- Any Markdown viewer with Mermaid support

### Option 3: Use DOT CLI
```bash
dot -Tpng chat_flow.dot -o chat_flow.png
dot -Tsvg chat_flow.dot -o chat_flow.svg
```

---

## 🎯 Performance Metrics

| Metric | Value |
|--------|-------|
| **Total Response Time** | 35-50 seconds |
| **Dishes Scored** | 7 (max) |
| **Parallel Retrievers** | 3 concurrent |
| **FAISS Threshold** | ≤2.0 (L2 distance) |
| **Top-K Results** | 20 dishes |
| **LLM Temperature** | 0 (deterministic) |
| **Performance Improvement** | 70% faster (vs 2+ min) |

---

## 🔗 Related Documentation

- **Test Documentation**: `../tests/README_TESTS.md`
- **E2E Tests**: `../tests/README_E2E_TESTS.md`
- **Test Coverage**: `../tests/TEST_COVERAGE_50.md`
- **Code**: `../app/flow/graph.py`

---

**Last Updated**: 2025-12-08
