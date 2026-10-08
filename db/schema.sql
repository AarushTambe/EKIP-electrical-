-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,

    name TEXT NOT NULL,

    email TEXT UNIQUE,

    username TEXT UNIQUE,

    password_hash TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'student'
        CHECK (role IN ('student', 'admin')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- SUBJECTS
-- ============================================================

CREATE TABLE IF NOT EXISTS subjects (
    id BIGSERIAL PRIMARY KEY,

    name TEXT NOT NULL UNIQUE,

    code TEXT UNIQUE
);


-- ============================================================
-- DOCUMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,

    title TEXT NOT NULL,

    filename TEXT NOT NULL,

    subject_id BIGINT
        REFERENCES subjects(id)
        ON DELETE SET NULL,

    status TEXT NOT NULL DEFAULT 'approved'
        CHECK (
            status IN (
                'approved',
                'ingested',
                'failed'
            )
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    approved_at TIMESTAMPTZ
);


-- ============================================================
-- SUBMISSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS submissions (
    id BIGSERIAL PRIMARY KEY,

    submitted_by BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    title TEXT NOT NULL,

    subject_id BIGINT
        REFERENCES subjects(id)
        ON DELETE SET NULL,

    source_file TEXT NOT NULL,

    description TEXT,

    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (
            status IN (
                'pending',
                'approved',
                'rejected'
            )
        ),

    reviewed_by BIGINT
        REFERENCES users(id)
        ON DELETE SET NULL,

    review_reason TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    reviewed_at TIMESTAMPTZ
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_documents_subject_id
    ON documents(subject_id);

CREATE INDEX IF NOT EXISTS idx_documents_status
    ON documents(status);

CREATE INDEX IF NOT EXISTS idx_submissions_submitted_by
    ON submissions(submitted_by);

CREATE INDEX IF NOT EXISTS idx_submissions_subject_id
    ON submissions(subject_id);

CREATE INDEX IF NOT EXISTS idx_submissions_status
    ON submissions(status);

CREATE INDEX IF NOT EXISTS idx_submissions_reviewed_by
    ON submissions(reviewed_by);