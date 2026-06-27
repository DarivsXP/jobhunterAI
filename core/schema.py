"""
Database schema definitions.
"""

JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    source TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    fingerprint TEXT UNIQUE NOT NULL,
    description TEXT,
    salary TEXT,
    country TEXT,
    posted_at TEXT,
    score INTEGER DEFAULT 0,
    priority TEXT DEFAULT 'LOW',
    interview_probability INTEGER DEFAULT 0,
    matched_skills_json TEXT DEFAULT '[]',
    missing_skills_json TEXT DEFAULT '[]',
    ai_recommendation TEXT DEFAULT '',
    ai_reasoning TEXT DEFAULT '',
    application_status TEXT DEFAULT 'new',
    applied INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
