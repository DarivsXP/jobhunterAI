from __future__ import annotations

import argparse

from core.database import Database
from core.logger import logger
from core.orchestrator import JobOrchestrator
from services.database_service import DatabaseService
from services.report_service import ReportService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JobHunterAI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Run the job collection pipeline.")

    report_parser = subparsers.add_parser(
        "report",
        help="Show a local dashboard from saved jobs.",
    )
    report_parser.add_argument("--limit", type=int, default=10)

    top_parser = subparsers.add_parser(
        "top",
        help="List top saved jobs.",
    )
    top_parser.add_argument("--limit", type=int, default=10)
    top_parser.add_argument("--status", type=str, default=None)

    apply_parser = subparsers.add_parser(
        "status",
        help="Update a saved job application status.",
    )
    apply_parser.add_argument("--job-id", type=int, required=True)
    apply_parser.add_argument(
        "--value",
        type=str,
        required=True,
        choices=["new", "applied", "interviewing", "rejected", "offer"],
    )

    return parser


def run_pipeline() -> None:
    logger.info("=" * 60)
    logger.info("Starting JobHunterAI")
    logger.info("=" * 60)

    database = Database()
    database.initialize()

    orchestrator = JobOrchestrator()

    try:
        orchestrator.run()

    except KeyboardInterrupt:
        logger.warning("Application interrupted by user.")

    except Exception:
        logger.exception("Fatal application error.")

    logger.info("=" * 60)
    logger.info("JobHunterAI Finished")
    logger.info("=" * 60)


def print_top_jobs(limit: int, status: str | None) -> None:
    database = DatabaseService()
    jobs = database.list_jobs(limit=limit, application_status=status)

    if not jobs:
        print("No saved jobs found.")
        return

    for job in jobs:
        print(
            f"[{job['id']}] {job['priority']} {job['score']} | "
            f"{job['title']} @ {job['company']}"
        )
        print(
            f"Status: {job['application_status']} | "
            f"Interview: {job['interview_probability']}% | "
            f"Source: {job['source']}"
        )
        if job["ai_recommendation"]:
            print(f"AI: {job['ai_recommendation']}")
        print(f"URL: {job['url']}")
        print()


def update_status(job_id: int, status: str) -> None:
    database = DatabaseService()
    updated = database.mark_application_status(job_id, status)

    if updated:
        print(f"Updated job {job_id} to status '{status}'.")
    else:
        print(f"Job {job_id} was not found.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "run"

    if command == "run":
        run_pipeline()
        return

    if command == "report":
        report = ReportService().build_dashboard(limit=args.limit)
        print(report)
        return

    if command == "top":
        print_top_jobs(limit=args.limit, status=args.status)
        return

    if command == "status":
        update_status(job_id=args.job_id, status=args.value)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
