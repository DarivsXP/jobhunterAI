"""
JobHunterAI Web Server
"""

from __future__ import annotations

import datetime
import threading
import time
from typing import Any

from flask import Flask, jsonify, render_template, request

from core.logger import get_logger
from core.orchestrator import JobOrchestrator
from core.scheduler import Scheduler
from services.database_service import DatabaseService
from services.ai_recruiter_service import AIRecruiterService

logger = get_logger(__name__)
app = Flask(__name__)

db_service = DatabaseService()
ai_recruiter = AIRecruiterService()

# Global scan status tracking
scanning = False
scan_lock = threading.Lock()


def run_scan_worker() -> None:
    global scanning
    try:
        logger.info("Background manual scan triggered from Web UI.")
        orchestrator = JobOrchestrator()
        orchestrator.run()
    except Exception:
        logger.exception("Manual scan worker failed.")
    finally:
        with scan_lock:
            scanning = False


def run_scheduler_worker() -> None:
    logger.info("Initializing Background Scheduler...")
    scheduler = Scheduler()
    # Replace the blocking scheduler.start() while loop so we sleep in our own daemon loop
    scheduler.scan()  # Run initial scan
    import schedule

    schedule.every(30).minutes.do(scheduler.scan)

    while True:
        schedule.run_pending()
        time.sleep(10)


@app.route("/")
def index() -> Any:
    return render_template("index.html")


@app.route("/api/stats")
def stats() -> Any:
    try:
        data = db_service.stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs")
def get_jobs() -> Any:
    try:
        limit = request.args.get("limit", default=100, type=int)
        status = request.args.get("status", default=None, type=str)
        priority = request.args.get("priority", default=None, type=str)
        max_age_days = request.args.get("max_age_days", default=None, type=int)

        jobs = db_service.list_jobs(limit=limit, application_status=status)

        filtered_jobs = []
        now = datetime.datetime.now(datetime.timezone.utc)

        for job in jobs:
            # Apply priority filter
            if priority and job["priority"] != priority:
                continue

            # Apply date age filter if requested
            if max_age_days is not None:
                posted_str = str(job.get("created_at") or "")  # created_at is standard YYYY-MM-DD HH:MM:SS
                try:
                    posted_dt = datetime.datetime.strptime(
                        posted_str[:19], "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=datetime.timezone.utc)
                    age_days = (now - posted_dt).days
                    if age_days > max_age_days:
                        continue
                except Exception:
                    pass

            filtered_jobs.append(job)

        return jsonify(filtered_jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>/status", methods=["POST"])
def update_job_status(job_id: int) -> Any:
    try:
        content = request.json or {}
        new_status = content.get("status")
        if not new_status:
            return jsonify({"error": "Missing 'status' in request body"}), 400

        valid_statuses = {"new", "applied", "interviewing", "rejected", "offer", "archived"}
        if new_status not in valid_statuses:
            return (
                jsonify({"error": f"Invalid status. Must be one of {valid_statuses}"}),
                400,
            )

        success = db_service.mark_application_status(job_id, new_status)
        if success:
            return jsonify({"success": True, "job_id": job_id, "status": new_status})
        else:
            return jsonify({"error": f"Job {job_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>/generate_materials", methods=["POST"])
def generate_materials(job_id: int) -> Any:
    try:
        job = db_service.get_job(job_id)
        if not job:
            return jsonify({"error": f"Job {job_id} not found"}), 404
            
        materials = ai_recruiter.generate_application_materials(job)
        if not materials:
            return jsonify({"error": "Failed to generate materials. Check API keys or rate limits."}), 500
            
        return jsonify(materials)
    except Exception as e:
        logger.exception("Error generating materials")
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan", methods=["POST"])
def trigger_scan() -> Any:
    global scanning
    with scan_lock:
        if scanning:
            return jsonify({"status": "already_running", "message": "Scan is already in progress"}), 400
        scanning = True

    thread = threading.Thread(target=run_scan_worker, daemon=True)
    thread.start()
    return jsonify({"status": "started", "message": "Scan started in background"})


@app.route("/api/scan/status")
def get_scan_status() -> Any:
    global scanning
    return jsonify({"scanning": scanning})


def start_server() -> None:
    import os
    # Start background scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler_worker, daemon=True)
    scheduler_thread.start()

    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Web Server starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    start_server()
