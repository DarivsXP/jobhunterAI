import time
import logging
import schedule

from database import (
    job_exists,
    save_job
)

from scorer import score_job

from telegram_bot import (
    send_message
)

from scrapers.remotive import (
    get_jobs
)

from pause import (
    is_paused
)

from digest import (
    generate_digest
)

# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -----------------------------
# Match Categories
# -----------------------------

HOT_MATCH = 90
HIGH_PRIORITY = 80
GOOD_MATCH = 70

# -----------------------------
# Notification
# -----------------------------

def notify(job, result):

    score = result["score"]

    age = job.get("age_label", "")

    if score >= HOT_MATCH:

        send_message(
f"""🔥 APPLY IMMEDIATELY

Role:
{job['title']}

Company:
{job['company']}

Score:
{score}

Matched Skills:
{", ".join(result["skills"])}

{age}

{job['url']}
"""
        )

    elif score >= HIGH_PRIORITY:

        send_message(
f"""⭐ HIGH PRIORITY

Role:
{job['title']}

Company:
{job['company']}

Score:
{score}

{age}

{job['url']}
"""
        )

    # GOOD_MATCHS ARE SAVED ONLY
    # They appear in the Daily Digest.

# -----------------------------
# Process Jobs
# -----------------------------

def process_jobs():

    if is_paused():

        logging.info("Notifications are paused.")

        return

    logging.info("Checking Remotive...")

    jobs = get_jobs()

    logging.info(f"{len(jobs)} jobs found.")

    for job in jobs:

        if job_exists(job["url"]):
            continue

        result = score_job(job)

        job["score"] = result["score"]

        save_job(job)

        if result["score"] >= GOOD_MATCH:

            notify(
                job,
                result
            )

# -----------------------------
# Daily Digest
# -----------------------------

def send_daily_digest():

    logging.info(
        "Sending daily digest..."
    )

    message = generate_digest()

    send_message(message)

# -----------------------------
# Scheduler
# -----------------------------

schedule.every(1).hours.do(
    process_jobs
)

schedule.every().day.at(
    "20:00"
).do(
    send_daily_digest
)

# -----------------------------
# Startup
# -----------------------------

logging.info(
    "Darivs Job Hunter Started"
)

process_jobs()

while True:

    schedule.run_pending()

    time.sleep(60)