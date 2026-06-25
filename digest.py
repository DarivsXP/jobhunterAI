from database import get_today_jobs

def generate_digest():

    jobs = get_today_jobs()

    if not jobs:

        return (
            "No jobs found today."
        )

    message = (
        "📊 Daily Job Digest\n\n"
    )

    for job in jobs[:20]:

        message += (
            f"{job[3]} | "
            f"{job[1]}\n"
        )

    return message