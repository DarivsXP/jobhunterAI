"""
JobHunterAI Recruiter

Evaluates jobs against the candidate profile.

Future:
- GPT Recruiter
- Interview probability
- AI reasoning
"""

from dataclasses import dataclass, field

from candidate.profile import MY_PROFILE
from core.logger import get_logger
from core.models import Job

logger = get_logger(__name__)


@dataclass(slots=True)
class Evaluation:

    accepted: bool

    score: int

    priority: str

    reasons: list[str] = field(default_factory=list)

    matched_roles: list[str] = field(default_factory=list)

    matched_skills: list[str] = field(default_factory=list)

    missing_skills: list[str] = field(default_factory=list)


class Recruiter:

    ROLE_WEIGHT = 40

    SKILL_WEIGHT = 10

    COUNTRY_WEIGHT = 10

    RECENT_WEIGHT = 5

    def evaluate(self, job: Job) -> Evaluation:

        text = f"{job.title} {job.description} {job.country}".lower()

        score = 0

        reasons = []

        matched_roles = []

        matched_skills = []

        missing_skills = []

        #
        # Reject unwanted titles
        #

        for excluded in MY_PROFILE.excluded_titles:

            if excluded.lower() in text:

                logger.info(f"Rejected: {job.title}")

                return Evaluation(

                    accepted=False,

                    score=0,

                    priority="IGNORE",

                    reasons=[
                        f"Excluded title: {excluded}"
                    ]

                )

        #
        # Preferred roles
        #

        for role in MY_PROFILE.preferred_roles:

            if role.lower() in text:

                score += self.ROLE_WEIGHT

                matched_roles.append(role)

                reasons.append(f"Role match: {role}")

        #
        # Skills
        #

        for skill in MY_PROFILE.preferred_skills:

            if skill.lower() in text:

                score += self.SKILL_WEIGHT

                matched_skills.append(skill)

                reasons.append(f"Skill: {skill}")

            else:

                missing_skills.append(skill)

        #
        # Countries
        #

        for country in MY_PROFILE.preferred_countries:

            if country.lower() in text:

                score += self.COUNTRY_WEIGHT

                reasons.append(f"Country: {country}")

                break

        #
        # Remote bonus
        #

        if job.remote:

            score += 5

            reasons.append("Remote")

        #
        # Priority
        #

        if score >= 90:

            priority = "HOT"

        elif score >= 75:

            priority = "HIGH"

        elif score >= MY_PROFILE.minimum_score:

            priority = "GOOD"

        else:

            priority = "LOW"

        accepted = score >= MY_PROFILE.minimum_score

        logger.info(

            f"{job.title[:45]:45}"

            f"| {score:3}"

            f" | {priority}"

        )

        job.score = score

        job.priority = priority

        job.matched_roles = matched_roles

        job.matched_skills = matched_skills

        job.missing_skills = missing_skills

        job.reasons = reasons

        job.interview_probability = min(score, 95)

        return Evaluation(

            accepted=accepted,

            score=score,

            priority=priority,

            reasons=reasons,

            matched_roles=matched_roles,

            matched_skills=matched_skills,

            missing_skills=missing_skills,

        )