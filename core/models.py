"""
Application Models
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Job:
    """
    Represents a single job posting.
    """

    title: str
    company: str
    description: str
    url: str
    posted_at: str
    salary: str
    country: str
    remote: bool
    source: str
    score: int = 0
    fingerprint: str = ""
    priority: str = "LOW"
    interview_probability: int = 0
    matched_roles: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    ai_reasoning: str = ""
    ai_recommendation: str = ""
    cover_letter: str = ""
