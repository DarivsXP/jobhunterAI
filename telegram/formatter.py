"""
Telegram message formatting helpers.
"""

from __future__ import annotations

from core.models import Job


def escape_markdown(text: str) -> str:
    escaped = text or ""

    for char in ("_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"):
        escaped = escaped.replace(char, f"\\{char}")

    return escaped


def format_job_message(job: Job) -> str:
    recommendation = (
        f"\n*AI Recommendation*: {escape_markdown(job.ai_recommendation)}"
        if job.ai_recommendation
        else ""
    )
    reasoning = (
        f"\n*AI Reasoning*: {escape_markdown(job.ai_reasoning[:300])}"
        if job.ai_reasoning
        else ""
    )
    skills = (
        f"\n*Skills*: {escape_markdown(', '.join(job.matched_skills[:6]))}"
        if job.matched_skills
        else ""
    )

    return (
        f"*{escape_markdown(job.priority)} MATCH*\n\n"
        f"*Role*: {escape_markdown(job.title)}\n"
        f"*Company*: {escape_markdown(job.company)}\n"
        f"*Score*: {job.score}\n"
        f"*Interview Probability*: {job.interview_probability}%\n"
        f"*Country*: {escape_markdown(job.country)}\n"
        f"*Source*: {escape_markdown(job.source)}"
        f"{skills}"
        f"{recommendation}"
        f"{reasoning}\n"
        f"*URL*: {escape_markdown(job.url)}"
    )


def format_digest(jobs: list[Job]) -> str:
    if not jobs:
        return "*JobHunterAI Digest*\n\nNo accepted jobs in this run."

    lines = ["*JobHunterAI Digest*", ""]

    for job in jobs[:5]:
        lines.append(
            f"- *{escape_markdown(job.priority)}* | {job.score} | "
            f"{escape_markdown(job.title)} at {escape_markdown(job.company)}"
        )

    return "\n".join(lines)
