"""
CLI reporting and dashboard summaries.
"""

from __future__ import annotations

from services.database_service import DatabaseService


class ReportService:
    def __init__(self, database: DatabaseService | None = None) -> None:
        self.database = database or DatabaseService()

    def build_dashboard(self, limit: int = 10) -> str:
        stats = self.database.stats()
        jobs = self.database.list_jobs(limit=limit)
        sources = self.database.top_sources(limit=5)

        lines = [
            "JobHunterAI Dashboard",
            "=" * 60,
            (
                f"Total jobs: {stats['total_jobs']} | "
                f"New: {stats['new_jobs']} | "
                f"Applied: {stats['applied_jobs']}"
            ),
            (
                f"HOT: {stats['hot_jobs']} | "
                f"HIGH: {stats['high_jobs']} | "
                f"GOOD: {stats['good_jobs']}"
            ),
            "",
            "Top Sources",
            "-" * 60,
        ]

        if sources:
            for item in sources:
                lines.append(
                    f"{item['source']}: {item['job_count']}"
                )
        else:
            lines.append("No jobs saved yet.")

        lines.extend(["", "Top Jobs", "-" * 60])

        if jobs:
            for job in jobs:
                skills = ", ".join(job["matched_skills"][:5]) or "None"
                lines.append(
                    f"[{job['id']}] {job['priority']} {job['score']} | "
                    f"{job['title']} @ {job['company']}"
                )
                lines.append(
                    f"Status: {job['application_status']} | "
                    f"Interview: {job['interview_probability']}% | "
                    f"Source: {job['source']}"
                )
                lines.append(f"Skills: {skills}")
                if job["ai_recommendation"]:
                    lines.append(
                        f"AI: {job['ai_recommendation']} | "
                        f"{job['ai_reasoning'][:140]}"
                    )
                lines.append(f"URL: {job['url']}")
                lines.append("")
        else:
            lines.append("No jobs saved yet.")

        return "\n".join(lines).rstrip()
