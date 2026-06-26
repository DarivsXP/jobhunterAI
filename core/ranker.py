"""
Ranks accepted jobs.
"""

from core.models import Job


class JobRanker:

    def sort(self, jobs: list[Job]) -> list[Job]:

        return sorted(

            jobs,

            key=lambda x: x.score,

            reverse=True

        )