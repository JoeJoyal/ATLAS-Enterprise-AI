-- ============================================================
-- ATLAS-Enterprice-AI
-- PostgreSQL Database Schema
-- ============================================================
-- UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- 1. DOCUMENTS TABLE
-- Stores uploaded document metadata.
-- Actual document files are stored in AWS S3.
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500),
    file_type VARCHAR(100),
    file_size BIGINT NOT NULL DEFAULT 0,
    s3_bucket VARCHAR(255),
    s3_key TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'uploaded'
        CHECK (
            status IN (
                'uploaded',
                'processing',
                'indexed',
                'failed',
                'deleted'
            )
        ),

    pinecone_namespace VARCHAR(255),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    uploaded_by VARCHAR(255),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT documents_file_size_check
        CHECK (file_size >= 0)
);

-- ============================================================
-- 2. CHAT SESSIONS TABLE
-- Stores conversation/session-level information.
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_session (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),

    status VARCHAR(30) NOT NULL DEFAULT 'active'
        CHECK (
            status IN (
                'active',
                'completed',
                'archived'
            )
        ),
    
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. CHAT MESSAGES TABLE
-- Stores user questions and AI-generated responses.
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_messages (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES chat_sessions(id)
        ON DELETE CASCADE,

    role VARCHAR(30) NOT NULL
        CHECK (
            role IN (
                'system',
                'user',
                'assistant',
                'tool'
            )
        ),

    content TEXT NOT NULL,
    model_name VARCHAR(255),
    token_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    retrieved_documents JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 4. HITL APPROVALS TABLE
-- Stores Human-in-the-Loop approval requests.
-- ============================================================
CREATE TABLE IF NOT EXISTS hitl_approvals (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID
        REFERENCES chat_sessions(id)
        ON DELETE SET NULL,

    message_id UUID
        REFERENCES chat_message(id)
        ON DELETE SET NULL,

    requested_by VARCHAR(255) NOT NULL,
    approved_by VARCHAR(255),
    action_type VARCHAR(100) NOT NULL,
    action_payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    status VARCHAR(30) NOT NULL DEFAULT 'pending'
        CHECK (
            status IN (
                'pending',
                'approved',
                'rejected',
                'cancelled',
                'expired'
            )
        ),
    
    approval_comment TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

-- ============================================================
-- 5. FEEDBACK TABLE
-- Stores user feedback about AI responses.
-- ============================================================
CREATE TABLE IF NOT EXISTS feedback (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID
        REFERENCES chat_sessions(id)
        ON DELETE SET NULL,

    message_id UUID
        REFERENCES chat_messages(id)
        ON DELETE SET NULL,

    user_id VARCHAR(255) NOT NULL,

    rating SMALLINT
        CHECK (
            rating IS NULL OR rating BETWEEN 1 AND 5
        ),
    
    feedback_type VARCHAR(50),
    comments TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 6. AUDIT EVENTS TABLE
-- Stores important application activity and security events.
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_events (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id VARCHAR(255),
    actor_type VARCHAR(50),
    event_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    status VARCHAR(30),
    ip_address INET,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 7. INDEXES
-- Improve frequently used database queries.
-- ============================================================

-- Documents
CREATE INDEX IF NOT EXISTS idx_documents_status
    ON documents(status);

CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by
    ON documents(uploaded_by);

CREATE INDEX IF NOT EXISTS idx_documents_created_at
    ON documents(created_at DESC);


-- Chat sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id
    ON chat_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at
    ON chat_sessions(updated_at DESC);

-- Chat messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
    ON chat_messages(session_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at
    ON chat_messages(created_at DESC);

-- HITL approvals
CREATE INDEX IF NOT EXISTS idx_hitl_status
    ON hitl_approvals(status);

CREATE INDEX IF NOT EXISTS idx_hitl_requested_by
    ON hitl_approvals(requested_by);

CREATE INDEX IF NOT EXISTS idx_hitl_session_id
    ON hitl_approvals(session_id);


-- Feedback
CREATE INDEX IF NOT EXISTS idx_feedback_message_id
    ON feedback(message_id);

CREATE INDEX IF NOT EXISTS idx_feedback_user_id
    ON feedback(user_id);


-- Audit events
CREATE INDEX IF NOT EXISTS idx_audit_actor_id
    ON audit_events(actor_id);

CREATE INDEX IF NOT EXISTS idx_audit_event_type
    ON audit_events(event_type);

CREATE INDEX IF NOT EXISTS idx_audit_created_at
    ON audit_events(created_at DESC);