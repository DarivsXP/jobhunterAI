"""
Database schema definitions.
"""

JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    company TEXT,

    source TEXT,

    url TEXT,

    fingerprint TEXT UNIQUE,

    score INTEGER DEFAULT 0,

    priority TEXT,

    posted_at TEXT,

    description TEXT,

    salary TEXT,

    country TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""