"""
Recruiter Service
"""

from __future__ import annotations

import time
from typing import Protocol

from core.logger import get_logger
from core.models import Job
from core.ranker import JobRanker
from core.recruiter import Recruiter
from services.ai_recruiter_service import AIRecruiterService

logger = get_logger(__name__)


class DuplicateChecker(Protocol):
    def exists(self, fingerprint: str) -> bool:
        """Return True when a job fingerprint is already stored."""


class RecruiterService:
    def __init__(
        self,
        ai_recruiter: AIRecruiterService | None = None,
    ) -> None:
        self.recruiter = Recruiter()
        self.ranker = JobRanker()
        self.ai_recruiter = ai_recruiter or AIRecruiterService()

    def process(
        self,
        jobs: list[Job],
        database: DuplicateChecker,
    ) -> list[Job]:
        accepted: list[Job] = []

        for job in jobs:
            try:
                if database.exists(job.fingerprint):
                    logger.debug(
                        "Stored duplicate skipped: %s (%s)",
                        job.title,
                        job.company,
                    )
                    continue

                evaluation = self.recruiter.evaluate(job)

                if not evaluation.accepted:
                    continue

                job.score = evaluation.score
                job.priority = evaluation.priority
                job.interview_probability = evaluation.interview_probability
                job.reasons = evaluation.reasons
                job.matched_roles = evaluation.matched_roles
                job.matched_skills = evaluation.matched_skills
                job.missing_skills = evaluation.missing_skills

                self._enrich_with_ai(job)
                accepted.append(job)

                # Small pause between AI calls to stay under OpenAI's RPM limit
                if self.ai_recruiter.is_enabled():
                    time.sleep(2)

            except Exception:
                logger.exception(
                    "Recruiter failed evaluating job: %s (%s)",
                    getattr(job, "title", "Unknown"),
                    getattr(job, "company", "Unknown"),
                )

        return self.ranker.sort(accepted)

    def _enrich_with_ai(self, job: Job) -> None:
        analysis = self.ai_recruiter.evaluate(job)

        if analysis is None:
            return

        if analysis.interview_probability > 0:
            job.interview_probability = analysis.interview_probability

        if analysis.matched_skills:
            job.matched_skills = analysis.matched_skills

        if analysis.missing_skills:
            job.missing_skills = analysis.missing_skills

        job.ai_recommendation = analysis.recommendation
        job.ai_reasoning = analysis.reasoning
