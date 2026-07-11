"""
JobHunterAI Web Server
"""

from __future__ import annotations

import csv
import datetime
import io
import threading
import time
from typing import Any

from flask import Flask, Response, jsonify, render_template, request

from core.database import Database
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
last_scan_at: str | None = None


# ---------------------------------------------------------------------------
# Background Workers
# ---------------------------------------------------------------------------

def run_scan_worker() -> None:
    global scanning, last_scan_at
    try:
        logger.info("Background manual scan triggered from Web UI.")
        orchestrator = JobOrchestrator()
        orchestrator.run()
        last_scan_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    except Exception:
        logger.exception("Manual scan worker failed.")
    finally:
        with scan_lock:
            scanning = False


def run_scheduler_worker() -> None:
    global last_scan_at
    logger.info("Initializing Background Scheduler...")
    scheduler = Scheduler()
    # Run initial scan
    scheduler.scan()
    last_scan_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    import schedule

    def _scan_and_record():
        global last_scan_at
        scheduler.scan()
        last_scan_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    schedule.every(30).minutes.do(_scan_and_record)

    while True:
        schedule.run_pending()
        time.sleep(10)


def run_keepalive_worker() -> None:
    """Ping our own /ping endpoint every 10 minutes to prevent HF Spaces from sleeping."""
    import os
    import requests as _requests

    port = int(os.environ.get("PORT", 7860))
    ping_url = f"http://localhost:{port}/ping"

    # Wait for the server to be ready before pinging
    time.sleep(30)

    while True:
        try:
            _requests.get(ping_url, timeout=10)
            logger.debug("Keep-alive ping sent.")
        except Exception as exc:
            logger.warning("Keep-alive ping failed: %s", exc)
        time.sleep(600)  # 10 minutes


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index() -> Any:
    return render_template("index.html")


@app.route("/ping")
def ping() -> Any:
    """Health-check endpoint — also used by keep-alive thread to prevent HF sleep."""
    return jsonify({"status": "alive", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})


@app.route("/api/telegram/test", methods=["POST"])
def test_telegram() -> Any:
    """Send a test Telegram message to verify token and chat_id are valid."""
    try:
        from services.notification_service import NotificationService
        svc = NotificationService()
        ok = svc.test()
        if ok:
            return jsonify({"success": True, "message": "Test message sent to Telegram!"})
        else:
            return jsonify({
                "success": False,
                "message": "Failed — check that TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set correctly. See HF logs for details.",
            }), 500
    except Exception as e:
        logger.exception("Telegram test failed")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def stats() -> Any:
    try:
        data = db_service.stats()
        data["last_scan_at"] = last_scan_at
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
                posted_str = str(job.get("created_at") or "")
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


@app.route("/api/jobs/export")
def export_jobs() -> Any:
    """Download all jobs as a CSV file."""
    try:
        status = request.args.get("status", default=None, type=str)
        jobs = db_service.list_jobs(limit=10000, application_status=status)

        output = io.StringIO()
        fieldnames = [
            "id", "title", "company", "country", "source", "score", "priority",
            "interview_probability", "application_status", "salary",
            "posted_at", "created_at", "url", "ai_recommendation", "notes",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(jobs)

        csv_content = output.getvalue()
        filename = f"jobs_{datetime.date.today().isoformat()}.csv"

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
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


@app.route("/api/jobs/<int:job_id>/archive", methods=["POST"])
def archive_job(job_id: int) -> Any:
    """Shortcut to immediately archive a job."""
    try:
        success = db_service.mark_application_status(job_id, "archived")
        if success:
            return jsonify({"success": True, "job_id": job_id, "status": "archived"})
        else:
            return jsonify({"error": f"Job {job_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<int:job_id>/notes", methods=["POST"])
def update_job_notes(job_id: int) -> Any:
    """Save personal notes for a job."""
    try:
        content = request.json or {}
        notes = content.get("notes", "")

        job = db_service.get_job(job_id)
        if not job:
            return jsonify({"error": f"Job {job_id} not found"}), 404

        success = db_service.update_notes(job_id, notes)
        if success:
            return jsonify({"success": True, "job_id": job_id, "notes": notes.strip()})
        else:
            return jsonify({"error": "Failed to update notes"}), 500
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
    return jsonify({"scanning": scanning, "last_scan_at": last_scan_at})


# ---------------------------------------------------------------------------
# Server startup
# ---------------------------------------------------------------------------

def start_server() -> None:
    import os

    # Initialize DB before starting
    Database().initialize()

    # Start background scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler_worker, daemon=True)
    scheduler_thread.start()

    # Start keep-alive thread to prevent HF Spaces from sleeping
    keepalive_thread = threading.Thread(target=run_keepalive_worker, daemon=True)
    keepalive_thread.start()

    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Web Server starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    start_server()
