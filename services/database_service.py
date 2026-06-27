"""
Database Service

Handles duplicate detection, persistence, and reporting reads.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from sqlite3 import Row

from core.database import Database
from core.models import Job


class DatabaseService:
    def __init__(self) -> None:
        self.db = Database()
        self.db.initialize()

    def exists(self, fingerprint: str) -> bool:
        if not fingerprint:
            return False

        conn = self.db.connect()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM jobs WHERE fingerprint = ? LIMIT 1",
                (fingerprint,),
            )
            return cursor.fetchone() is not None

        finally:
            conn.close()

    def filter_new_jobs(self, jobs: Iterable[Job]) -> list[Job]:
        return [
            job
            for job in jobs
            if not self.exists(job.fingerprint)
        ]

    def save(self, job: Job) -> bool:
        return self.save_all([job]) == 1

    def save_all(self, jobs: Iterable[Job]) -> int:
        conn = self.db.connect()
        inserted = 0

        try:
            cursor = conn.cursor()

            for job in jobs:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO jobs
                    (
                        title,
                        company,
                        location,
                        source,
                        url,
                        fingerprint,
                        description,
                        salary,
                        country,
                        posted_at,
                        score,
                        priority,
                        interview_probability,
                        matched_skills_json,
                        missing_skills_json,
                        ai_recommendation,
                        ai_reasoning,
                        application_status,
                        applied
                    )
                    VALUES
                    (
                        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                    )
                    """,
                    (
                        job.title,
                        job.company,
                        getattr(job, "location", job.country),
                        job.source,
                        job.url,
                        job.fingerprint,
                        job.description,
                        job.salary,
                        job.country,
                        job.posted_at,
                        job.score,
                        job.priority,
                        job.interview_probability,
                        json.dumps(job.matched_skills),
                        json.dumps(job.missing_skills),
                        job.ai_recommendation,
                        job.ai_reasoning,
                        "new",
                        0,
                    ),
                )

                if cursor.rowcount:
                    inserted += 1

            conn.commit()
            return inserted

        finally:
            conn.close()

    def count(self) -> int:
        conn = self.db.connect()

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs")
            return int(cursor.fetchone()[0])

        finally:
            conn.close()

    def stats(self) -> dict[str, int]:
        conn = self.db.connect()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_jobs,
                    SUM(CASE WHEN applied = 1 THEN 1 ELSE 0 END) AS applied_jobs,
                    SUM(CASE WHEN application_status = 'new' THEN 1 ELSE 0 END) AS new_jobs,
                    SUM(CASE WHEN priority = 'HOT' THEN 1 ELSE 0 END) AS hot_jobs,
                    SUM(CASE WHEN priority = 'HIGH' THEN 1 ELSE 0 END) AS high_jobs,
                    SUM(CASE WHEN priority = 'GOOD' THEN 1 ELSE 0 END) AS good_jobs
                FROM jobs
                """
            )
            row = cursor.fetchone()
            return {
                key: int(row[key] or 0)
                for key in row.keys()
            }

        finally:
            conn.close()

    def list_jobs(
        self,
        limit: int = 10,
        application_status: str | None = None,
    ) -> list[dict[str, object]]:
        conn = self.db.connect()

        try:
            cursor = conn.cursor()
            query = """
                SELECT
                    id,
                    title,
                    company,
                    source,
                    url,
                    country,
                    score,
                    priority,
                    interview_probability,
                    matched_skills_json,
                    missing_skills_json,
                    ai_recommendation,
                    ai_reasoning,
                    application_status,
                    created_at
                FROM jobs
            """
            params: list[object] = []

            if application_status:
                query += " WHERE application_status = ?"
                params.append(application_status)

            query += " ORDER BY score DESC, created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [self._row_to_job_summary(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def top_sources(self, limit: int = 5) -> list[dict[str, object]]:
        conn = self.db.connect()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT source, COUNT(*) AS job_count
                FROM jobs
                GROUP BY source
                ORDER BY job_count DESC, source ASC
                LIMIT ?
                """,
                (limit,),
            )
            return [
                {
                    "source": row["source"],
                    "job_count": int(row["job_count"]),
                }
                for row in cursor.fetchall()
            ]

        finally:
            conn.close()

    def mark_application_status(self, job_id: int, status: str) -> bool:
        normalized_status = status.strip().lower()
        applied = 0 if normalized_status == "new" else 1

        conn = self.db.connect()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE jobs
                SET application_status = ?, applied = ?
                WHERE id = ?
                """,
                (normalized_status, applied, job_id),
            )
            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def _row_to_job_summary(self, row: Row) -> dict[str, object]:
        return {
            "id": int(row["id"]),
            "title": row["title"],
            "company": row["company"],
            "source": row["source"],
            "url": row["url"],
            "country": row["country"],
            "score": int(row["score"] or 0),
            "priority": row["priority"],
            "interview_probability": int(row["interview_probability"] or 0),
            "matched_skills": json.loads(row["matched_skills_json"] or "[]"),
            "missing_skills": json.loads(row["missing_skills_json"] or "[]"),
            "ai_recommendation": row["ai_recommendation"] or "",
            "ai_reasoning": row["ai_reasoning"] or "",
            "application_status": row["application_status"] or "new",
            "created_at": row["created_at"],
        }
