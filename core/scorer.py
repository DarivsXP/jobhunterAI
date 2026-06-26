"""
Job Scoring Engine
"""

from candidate.profile import MY_PROFILE
from core.models import Job


class JobScorer:

    ROLE_WEIGHT = 40
    SKILL_WEIGHT = 5
    COUNTRY_WEIGHT = 15
    REMOTE_WEIGHT = 10
    JUNIOR_WEIGHT = 20
    PORTFOLIO_WEIGHT = 10

    def score(self, job: Job) -> tuple[int, list[str]]:

        score = 0
        reasons = []

        text = f"{job.title} {job.description} {job.country}".lower()

        # Preferred roles
        for role in MY_PROFILE.preferred_roles:

            if role.lower() in text:

                score += self.ROLE_WEIGHT

                reasons.append(f"Role: {role}")

                break

        # Skills
        matched = 0

        for skill in MY_PROFILE.preferred_skills:

            if skill.lower() in text:

                matched += 1

        score += matched * self.SKILL_WEIGHT

        if matched:

            reasons.append(f"{matched} matching skills")

        # Preferred countries
        for country in MY_PROFILE.preferred_countries:

            if country.lower() in text:

                score += self.COUNTRY_WEIGHT

                reasons.append(country)

                break

        # Remote
        if job.remote:

            score += self.REMOTE_WEIGHT

            reasons.append("Remote")

        # Junior bonus
        if "junior" in text:

            score += self.JUNIOR_WEIGHT

            reasons.append("Junior")

        # Portfolio bonus
        score += self.PORTFOLIO_WEIGHT

        reasons.append("Portfolio Match")

        return min(score, 100), reasons