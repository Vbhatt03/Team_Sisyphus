-- This script will be executed when the PostgreSQL container starts.
-- It enables the pgvector extension and creates the necessary tables.

CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for storing landmark judgments
CREATE TABLE judgments (
    id SERIAL PRIMARY KEY,
    case_title VARCHAR(255) NOT NULL,
    citation VARCHAR(255),
    court VARCHAR(100),
    year INT,
    tags TEXT[],
    summary TEXT,
    key_takeaway TEXT NOT NULL,
    embedding vector(384) -- Dimension for 'all-MiniLM-L6-v2' model
);

-- Create table for storing case files
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(100) UNIQUE NOT NULL,
    fir_details JSONB, -- Store structured FIR data
    incident_date TIMESTAMPTZ,
    fir_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create table for proactive alerts
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link_to_judgment_id INTEGER REFERENCES judgments(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

