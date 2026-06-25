import sqlite3

conn = sqlite3.connect(
    "jobs.db",
    check_same_thread=False
)

cur = conn.cursor()

# Create jobs table
cur.execute("""
CREATE TABLE IF NOT EXISTS jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    source TEXT,
    url TEXT UNIQUE,
    score INTEGER,
    posted_at TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def job_exists(url):
    cur.execute(
        "SELECT id FROM jobs WHERE url=?",
        (url,)
    )
    return cur.fetchone() is not None


def save_job(job):
    cur.execute("""
    INSERT OR IGNORE INTO jobs(
        title,
        company,
        source,
        url,
        score,
        posted_at,
        description
    )
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        job["title"],
        job["company"],
        job["source"],
        job["url"],
        job["score"],
        job["posted_at"],
        job["description"]
    ))

    conn.commit()


def get_today_jobs():
    cur.execute("""
    SELECT
        id,
        title,
        company,
        score,
        url
    FROM jobs
    WHERE DATE(created_at)=DATE('now')
    ORDER BY score DESC
    """)

    return cur.fetchall()


def get_job(job_id):
    cur.execute("""
    SELECT
        id,
        title,
        company,
        description
    FROM jobs
    WHERE id=?
    """, (job_id,))

    return cur.fetchone()