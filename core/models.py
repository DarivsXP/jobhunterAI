"""
JobHunterAI Models
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Job:

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