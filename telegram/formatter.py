"""
Telegram message formatting helpers.
"""

from __future__ import annotations

from core.models import Job


# Characters that MUST be escaped in MarkdownV2 body text
_MARKDOWN_SPECIAL = r"\_*[]()~`>#+-=|{}.!"


def escape_markdown(text: str) -> str:
    """Escape all MarkdownV2 reserved characters in plain text."""
    result = str(text or "")
    for char in _MARKDOWN_SPECIAL:
        result = result.replace(char, f"\\{char}")
    return result


def escape_url(url: str) -> str:
    """
    Escape only the characters that are special INSIDE a MarkdownV2 link target.
    Inside `[text](url)` only ) and \\ need escaping.
    """
    result = str(url or "")
    result = result.replace("\\", "\\\\")
    result = result.replace(")", "\\)")
    return result


def _priority_emoji(priority: str) -> str:
    return {"HOT": "🔥", "HIGH": "⭐", "GOOD": "✅"}.get(priority, "📋")


def format_job_message(job: Job) -> str:
    emoji = _priority_emoji(job.priority)
    priority_label = escape_markdown(job.priority)
    title = escape_markdown(job.title)
    company = escape_markdown(job.company)
    country = escape_markdown(job.country or "Remote")
    source = escape_markdown(job.source or "")
    salary = escape_markdown(job.salary or "Not specified")

    lines = [
        f"{emoji} *{priority_label} MATCH*",
        "",
        f"*Role:* {title}",
        f"*Company:* {company}",
        f"*Score:* {job.score} \\| *Interview:* {job.interview_probability}%",
        f"*Country:* {country}",
        f"*Source:* {source}",
        f"*Salary:* {salary}",
    ]

    if job.matched_skills:
        skills_text = escape_markdown(", ".join(job.matched_skills[:6]))
        lines.append(f"*Skills:* {skills_text}")

    if job.ai_recommendation:
        lines.append(f"*AI Rec:* {escape_markdown(job.ai_recommendation)}")

    if job.ai_reasoning:
        truncated = job.ai_reasoning[:250]
        lines.append(f"*Reasoning:* {escape_markdown(truncated)}")

    lines.append("")
    lines.append(f"[🔗 View Job]({escape_url(job.url)})")

    return "\n".join(lines)


def format_digest(jobs: list[Job]) -> str:
    if not jobs:
        return "📋 *JobHunterAI Digest*\n\nNo new jobs found in this scan\\."

    lines = [
        "📋 *JobHunterAI Digest*",
        f"_{escape_markdown(f'{len(jobs)} new jobs found')}_",
        "",
    ]

    for i, job in enumerate(jobs[:10], start=1):
        emoji = _priority_emoji(job.priority)
        priority = escape_markdown(job.priority)
        title = escape_markdown(job.title)
        company = escape_markdown(job.company)
        lines.append(
            f"{i}\\. {emoji} *{priority}* \\| {job.score}pts \\| "
            f"{title} @ {company}"
        )

    return "\n".join(lines)


def format_scan_summary(
    total_scraped: int,
    total_kept: int,
    hot: int,
    high: int,
    good: int,
) -> str:
    return (
        "🤖 *JobHunterAI Scan Complete*\n\n"
        f"Scraped: {escape_markdown(str(total_scraped))} jobs\n"
        f"New accepted: {escape_markdown(str(total_kept))} jobs\n"
        f"🔥 HOT: {hot} \\| ⭐ HIGH: {high} \\| ✅ GOOD: {good}"
    )
