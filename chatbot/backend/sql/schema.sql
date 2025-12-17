-- RAG Chatbot Database Schema
-- Database: Neon Serverless Postgres
-- Purpose: Store query logs, responses, and session tracking

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Queries table: stores user questions
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID,
    query_text TEXT NOT NULL,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('selected-text', 'book-wide')),
    context_text TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Add index on timestamp for time-range queries
CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp);

-- Add index on session_id for session queries
CREATE INDEX IF NOT EXISTS idx_queries_session_id ON queries(session_id);

-- Responses table: stores chatbot answers
CREATE TABLE IF NOT EXISTS responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    refused BOOLEAN DEFAULT FALSE,
    refusal_reason TEXT,
    latency_ms INTEGER CHECK (latency_ms >= 0),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Add index on query_id for join optimization
CREATE INDEX IF NOT EXISTS idx_responses_query_id ON responses(query_id);

-- Add index on refused for analytics
CREATE INDEX IF NOT EXISTS idx_responses_refused ON responses(refused);

-- Add index on timestamp
CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON responses(timestamp);

-- Sessions table: tracks multi-turn conversations (future use)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW()
);

-- Add index on user_id
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- Add index on last_active for cleanup queries
CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON sessions(last_active);

-- View: Query statistics
CREATE OR REPLACE VIEW query_stats AS
SELECT
    DATE(q.timestamp) AS query_date,
    q.mode,
    COUNT(*) AS total_queries,
    SUM(CASE WHEN r.refused THEN 1 ELSE 0 END) AS refused_count,
    AVG(r.latency_ms) AS avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY r.latency_ms) AS p95_latency_ms,
    AVG(r.confidence) AS avg_confidence
FROM queries q
LEFT JOIN responses r ON q.id = r.query_id
GROUP BY DATE(q.timestamp), q.mode;

-- View: Most queried chapters
CREATE OR REPLACE VIEW top_chapters AS
SELECT
    source->>'chapter' AS chapter,
    COUNT(*) AS query_count
FROM responses r,
     jsonb_array_elements(r.sources) AS source
WHERE NOT r.refused
GROUP BY source->>'chapter'
ORDER BY query_count DESC
LIMIT 20;

-- Function: Clean up old sessions (older than 90 days)
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM sessions
        WHERE last_active < NOW() - INTERVAL '90 days'
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE queries IS 'Stores user questions submitted to the chatbot';
COMMENT ON TABLE responses IS 'Stores chatbot-generated answers and metadata';
COMMENT ON TABLE sessions IS 'Tracks multi-turn conversation sessions (future use)';
COMMENT ON COLUMN queries.mode IS 'Retrieval mode: selected-text or book-wide';
COMMENT ON COLUMN queries.context_text IS 'User-selected text (required for selected-text mode)';
COMMENT ON COLUMN responses.sources IS 'JSONB array of source citations with passage_id, chapter, section, page, snippet';
COMMENT ON COLUMN responses.refused IS 'True if chatbot refused to answer due to insufficient context';
COMMENT ON COLUMN responses.refusal_reason IS 'Explanation for refusal (e.g., similarity below threshold)';
