# Quickstart: RAG Chatbot Setup and Usage

**Date**: 2025-12-15
**Purpose**: Step-by-step guide to set up, index, and query the RAG chatbot

## Prerequisites

- Python 3.11+ installed
- Qdrant Cloud Free Tier account ([signup](https://cloud.qdrant.io/))
- Neon Serverless Postgres account ([signup](https://neon.tech/))
- OpenAI API key ([get key](https://platform.openai.com/api-keys))
- Book content in Markdown format (in `content/` directory)

## 1. Environment Setup

### 1.1 Clone Repository and Install Dependencies

```bash
# Clone the repository (or navigate to project root)
cd /path/to/rag-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 1.2 Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Neon Postgres Configuration (optional, for logging)
NEON_DATABASE_URL=postgres://user:password@ep-xxx.neon.tech/rag_chatbot?sslmode=require

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_LOGGING=false  # Set to true to log queries/responses to Neon
ADMIN_API_KEY=your_admin_api_key  # For /admin endpoints

# Chunking Configuration
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Retrieval Configuration
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
SIMILARITY_THRESHOLD=0.7
CONFIDENCE_THRESHOLD=0.6

# Performance Configuration
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT_SEC=30
```

### 1.3 Verify Dependencies

```bash
# Test Qdrant connection
python -c "from qdrant_client import QdrantClient; client = QdrantClient(url='$QDRANT_URL', api_key='$QDRANT_API_KEY'); print('Qdrant OK')"

# Test Neon connection (if logging enabled)
python -c "import psycopg2; conn = psycopg2.connect('$NEON_DATABASE_URL'); print('Neon OK'); conn.close()"

# Test OpenAI API
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('OpenAI OK')"
```

---

## 2. Database Setup (Neon Postgres)

### 2.1 Create Tables (if logging enabled)

Run the SQL schema:

```bash
psql $NEON_DATABASE_URL -f backend/sql/schema.sql
```

**schema.sql**:
```sql
CREATE TABLE IF NOT EXISTS queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID,
  query_text TEXT NOT NULL,
  mode VARCHAR(20) NOT NULL CHECK (mode IN ('selected-text', 'book-wide')),
  context_text TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_id UUID REFERENCES queries(id),
  answer_text TEXT NOT NULL,
  sources JSONB NOT NULL,
  confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
  refused BOOLEAN DEFAULT FALSE,
  refusal_reason TEXT,
  latency_ms INTEGER,
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  last_active TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_queries_timestamp ON queries(timestamp);
CREATE INDEX idx_responses_query_id ON responses(query_id);
CREATE INDEX idx_responses_refused ON responses(refused);
```

---

## 3. Index Book Content

### 3.1 Prepare Book Content

Ensure book content is in `content/` directory as Markdown files:

```
content/
├── chapter-1.md
├── chapter-2.md
├── chapter-3.md
└── ...
```

Each file should have proper Markdown headings:

```markdown
# Chapter 3: RAG Systems

## 3.1 Introduction to RAG

Retrieval-Augmented Generation (RAG) combines retrieval and generation...

## 3.2 Retrieval Strategies

The optimal chunk size for technical documentation is 500-1000 tokens...
```

### 3.2 Run Indexing Script

**Option 1: Via API** (recommended for production):

```bash
# Start the backend server
cd backend
uvicorn src.api.main:app --reload --port 8000

# In another terminal, trigger indexing
curl -X POST http://localhost:8000/v1/admin/index \
  -H "X-API-Key: your_admin_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "content/",
    "chunk_size": 800,
    "chunk_overlap": 100,
    "force_reindex": false
  }'
```

**Option 2: Via CLI script**:

```bash
# Run standalone indexing script
python backend/scripts/index_content.py \
  --source-path content/ \
  --chunk-size 800 \
  --chunk-overlap 100
```

### 3.3 Verify Indexing

```bash
# Check Qdrant collection
curl -X GET "https://your-cluster.qdrant.io/collections/book-chunks" \
  -H "api-key: your_qdrant_api_key"

# Expected response:
{
  "result": {
    "status": "green",
    "vectors_count": 9543,
    "indexed_vectors_count": 9543,
    ...
  }
}
```

---

## 4. Start the Backend Server

```bash
cd backend
uvicorn src.api.main:app --reload --port 8000
```

Verify server is running:

```bash
curl http://localhost:8000/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "dependencies": {
    "qdrant": "healthy",
    "neon_postgres": "healthy",
    "openai": "healthy"
  },
  "timestamp": "2025-12-15T14:30:00Z"
}
```

---

## 5. Query the Chatbot

### 5.1 Book-Wide Mode

Send a question and retrieve relevant chunks from the entire book:

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the optimal chunk size for RAG systems?",
    "mode": "book-wide"
  }'
```

**Response**:
```json
{
  "answer": "The optimal chunk size for technical documentation in RAG systems is 500-1000 tokens with 100-token overlap. This range preserves comprehension context while avoiding information dilution.",
  "sources": [
    {
      "passage_id": "ch3-sec2-p45",
      "chapter": "Chapter 3: RAG Systems",
      "section": "3.2 Retrieval Strategies",
      "page": 45,
      "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens..."
    }
  ],
  "refused": false,
  "confidence": 0.92,
  "latency_ms": 1450
}
```

### 5.2 Selected-Text Mode

Ask a question about a specific passage (no retrieval):

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain this chunking approach",
    "mode": "selected-text",
    "context": "The optimal chunk size for technical documentation is 500-1000 tokens with 100-token overlap. This preserves comprehension context while avoiding information dilution."
  }'
```

**Response**:
```json
{
  "answer": "This chunking approach uses 500-1000 token chunks with 100-token overlap. The 500-1000 token range ensures each chunk contains enough context for comprehension without diluting information. The 100-token overlap ensures important information at chunk boundaries is not lost.",
  "sources": [
    {
      "passage_id": "user-selection",
      "chapter": "User Selection",
      "section": "Selected Text",
      "page": null,
      "snippet": "The optimal chunk size for technical documentation is 500-1000 tokens..."
    }
  ],
  "refused": false,
  "confidence": 0.95,
  "latency_ms": 850
}
```

### 5.3 Refusal Example

Ask a question with insufficient context:

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the best programming language?",
    "mode": "book-wide"
  }'
```

**Response**:
```json
{
  "answer": "This information cannot be verified from the book content.",
  "sources": [],
  "refused": true,
  "refusal_reason": "Top-1 similarity (0.42) below threshold (0.7)",
  "confidence": 0.0,
  "latency_ms": 650
}
```

---

## 6. Frontend Integration (ChatKit UI in Docusaurus)

### 6.1 Install ChatKit SDK

```bash
cd frontend
npm install @openai/chatkit
```

### 6.2 Integrate ChatWidget Component

**frontend/src/components/ChatWidget.tsx**:

```typescript
import React from 'react';
import { ChatKit } from '@openai/chatkit';

const ChatWidget: React.FC = () => {
  const handleSendMessage = async (message: string, mode: 'book-wide' | 'selected-text', context?: string) => {
    const response = await fetch('http://localhost:8000/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message, mode, context }),
    });
    return response.json();
  };

  return (
    <ChatKit
      onSendMessage={handleSendMessage}
      placeholder="Ask a question about the book..."
    />
  );
};

export default ChatWidget;
```

### 6.3 Add Text Selection Capture

**frontend/src/hooks/useTextSelection.ts**:

```typescript
import { useState, useEffect } from 'react';

export const useTextSelection = () => {
  const [selectedText, setSelectedText] = useState<string | null>(null);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();
      setSelectedText(text || null);
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  return selectedText;
};
```

### 6.4 Embed in Docusaurus

**docusaurus.config.js**:

```javascript
module.exports = {
  themeConfig: {
    navbar: {
      items: [
        {
          type: 'custom-chatbot',
          position: 'right',
        },
      ],
    },
  },
  plugins: [
    './src/plugins/chatbot-plugin',
  ],
};
```

---

## 7. Testing

### 7.1 Run Unit Tests

```bash
cd backend
pytest tests/unit/ -v
```

### 7.2 Run Integration Tests

```bash
pytest tests/integration/ -v
```

### 7.3 Run Contract Tests

```bash
pytest tests/contract/ -v
```

---

## 8. Monitoring and Debugging

### 8.1 View Logs

**Application logs** (stdout):
```bash
tail -f backend/logs/app.log
```

**Query logs** (Neon Postgres, if enabled):
```sql
SELECT query_text, mode, timestamp FROM queries ORDER BY timestamp DESC LIMIT 10;
```

**Response logs** (Neon Postgres, if enabled):
```sql
SELECT answer_text, refused, confidence, latency_ms FROM responses ORDER BY timestamp DESC LIMIT 10;
```

### 8.2 Monitor Qdrant Usage

Check Free Tier limits:

```bash
curl -X GET "https://your-cluster.qdrant.io/collections/book-chunks" \
  -H "api-key: your_qdrant_api_key" \
  | jq '.result.vectors_count'

# Ensure < 1 million vectors
```

### 8.3 Monitor Performance

```bash
curl http://localhost:8000/v1/admin/stats \
  -H "X-API-Key: your_admin_api_key"
```

**Response**:
```json
{
  "total_queries": 1543,
  "refusal_count": 87,
  "refusal_rate": 0.056,
  "avg_latency_ms": 1320.5,
  "p95_latency_ms": 2450.0,
  "avg_confidence": 0.87
}
```

---

## 9. Troubleshooting

### 9.1 Qdrant Connection Errors

**Error**: `QdrantException: Connection refused`

**Solution**:
- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant Cloud cluster status
- Ensure firewall allows outbound HTTPS to Qdrant

### 9.2 High Refusal Rate

**Error**: Most queries are refused

**Solution**:
- Lower `SIMILARITY_THRESHOLD` (e.g., from 0.7 to 0.6)
- Lower `CONFIDENCE_THRESHOLD` (e.g., from 0.6 to 0.5)
- Verify book content is properly indexed
- Check if embeddings are correctly generated

### 9.3 Slow Query Performance

**Error**: Latency > 5 seconds

**Solution**:
- Check Qdrant HNSW index parameters (`m`, `ef_construct`)
- Reduce `TOP_K_RETRIEVAL` (e.g., from 10 to 5)
- Verify Qdrant cluster is not overloaded (Free Tier limits)
- Enable request caching for repeated queries

### 9.4 OpenAI Rate Limits

**Error**: `RateLimitError: Rate limit exceeded`

**Solution**:
- Implement exponential backoff retries
- Reduce concurrent requests (`MAX_CONCURRENT_REQUESTS`)
- Upgrade OpenAI tier if needed

---

## 10. Deployment (Production)

### 10.1 Backend Deployment

Deploy FastAPI backend to a cloud platform:

**Option 1: Render** (recommended for FastAPI):
```bash
# Create Render service
render create web --name rag-chatbot-backend \
  --env-file backend/.env \
  --build-command "pip install -r requirements.txt" \
  --start-command "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
```

**Option 2: Fly.io**:
```bash
fly launch --name rag-chatbot-backend
fly deploy
```

### 10.2 Frontend Deployment

Deploy Docusaurus book with ChatKit integration:

```bash
cd frontend
npm run build
npx docusaurus deploy
```

### 10.3 Update Environment Variables

Set production environment variables:
- `ENVIRONMENT=production`
- `QDRANT_URL=<production Qdrant cluster>`
- `NEON_DATABASE_URL=<production Neon database>`
- `ENABLE_LOGGING=true` (for production monitoring)

---

## Summary

This quickstart guide covered:
1. ✅ Environment setup (Python, Qdrant, Neon, OpenAI)
2. ✅ Database schema creation
3. ✅ Book content indexing
4. ✅ Backend server startup
5. ✅ Querying in book-wide and selected-text modes
6. ✅ Frontend integration with ChatKit
7. ✅ Testing and monitoring
8. ✅ Troubleshooting common issues
9. ✅ Production deployment

Next steps:
- Run `/sp.tasks` to generate actionable implementation tasks
- Implement backend services and API endpoints
- Integrate frontend ChatKit UI
- Run validation and grounding checks
