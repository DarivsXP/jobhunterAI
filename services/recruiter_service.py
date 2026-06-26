"""
Recruiter Service
"""

from typing import List

from core.fingerprint import JobFingerprint
from core.models import Job
from core.normalizer import JobNormalizer
from core.ranker import JobRanker
from core.recruiter import Recruiter


class RecruiterService:

    def __init__(self):

        self.normalizer = JobNormalizer()

        self.recruiter = Recruiter()

        self.ranker = JobRanker()

    def process(self, jobs: List[Job], database) -> List[Job]:

        accepted = []

        for job in jobs:

            job = self.normalizer.normalize(job)

            job.fingerprint = JobFingerprint.create(job)

            if database.exists(job.fingerprint):

                continue

            evaluation = self.recruiter.evaluate(job)

            if not evaluation.accepted:

                continue

            job.score = evaluation.score
            job.priority = evaluation.priority
            job.reasons = evaluation.reasons
            job.matched_roles = evaluation.matched_roles
            job.matched_skills = evaluation.matched_skills
            job.missing_skills = evaluation.missing_skills

            accepted.append(job)

        return self.ranker.sort(accepted)