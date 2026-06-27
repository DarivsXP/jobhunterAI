"""
JobHunterAI Recruiter

Evaluates jobs against the candidate profile.
"""

from dataclasses import dataclass, field

from candidate.profile import MY_PROFILE
from core.logger import get_logger
from core.models import Job
from core.scorer import JobScorer

logger = get_logger(__name__)


@dataclass(slots=True)
class Evaluation:
    accepted: bool
    score: int
    priority: str
    interview_probability: int
    matched_roles: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class Recruiter:
    def __init__(self) -> None:
        self.scorer = JobScorer()

    def evaluate(self, job: Job) -> Evaluation:
        score, reasons = self.scorer.score(job)

        matched_roles = [
            role
            for role in MY_PROFILE.preferred_roles
            if role.lower() in job.title.lower()
        ]

        missing_skills = [
            skill
            for skill in MY_PROFILE.preferred_skills
            if skill not in job.matched_skills
        ]

        probability = self._estimate_probability(
            score,
            len(job.matched_skills),
            len(missing_skills),
        )

        accepted = score >= MY_PROFILE.minimum_score

        logger.info(
            "[%s] %s (%d)",
            "ACCEPT" if accepted else "REJECT",
            job.title,
            score,
        )

        return Evaluation(
            accepted=accepted,
            score=score,
            priority=job.priority,
            interview_probability=probability,
            matched_roles=matched_roles,
            matched_skills=job.matched_skills,
            missing_skills=missing_skills,
            reasons=reasons,
        )

    @staticmethod
    def _estimate_probability(
        score: int,
        matched: int,
        missing: int,
    ) -> int:
        probability = score + matched * 2 - missing
        return max(5, min(95, probability))
