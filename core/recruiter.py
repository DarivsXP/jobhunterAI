"""
JobHunterAI Recruiter

Evaluates whether a job is worth applying to.
"""

from dataclasses import dataclass, field

from core.logger import get_logger
from core.models import Job

logger = get_logger(__name__)


@dataclass(slots=True)
class Evaluation:

    accepted: bool

    score: int

    priority: str

    reasons: list[str] = field(default_factory=list)


class Recruiter:

    TARGET_ROLES = {

        "junior software engineer": 30,

        "software engineer i": 30,

        "associate software engineer": 30,

        "junior full stack developer": 30,

        "full stack developer": 20,

        "php developer": 30,

        "laravel developer": 35,

        "backend developer": 20,

        "web developer": 20,

        "software developer": 20,

        "application support engineer": 20,

        "technical support engineer": 20,

        "product support engineer": 15,
    }

    SKILLS = {

        "laravel": 20,

        "php": 20,

        "mysql": 15,

        "postgresql": 15,

        "javascript": 10,

        "typescript": 10,

        "react": 10,

        "vue": 10,

        "rest api": 10,

        "git": 5,

        "docker": 5,
    }

    EXCLUDED = [

        "senior",

        "staff",

        "lead",

        "principal",

        "architect",

        "manager",

        "director",

        "head",

        "vp",

        "ios",

        "android",

        "sales",

        "copywriter",

        "writer",

        "editor",

        "marketing",

        "designer",

        "finance",

        "account payable",

        "office assistant",
    ]

    def evaluate(self, job: Job) -> Evaluation:

        text = (
            job.title +
            " " +
            job.description
        ).lower()

        for word in self.EXCLUDED:

            if word in text:

                return Evaluation(
                    accepted=False,
                    score=0,
                    priority="IGNORE",
                    reasons=[
                        f"Contains excluded keyword '{word}'"
                    ]
                )

        score = 0

        reasons = []

        for role, points in self.TARGET_ROLES.items():

            if role in text:

                score += points

                reasons.append(role)

        for skill, points in self.SKILLS.items():

            if skill in text:

                score += points

                reasons.append(skill)

        if score >= 90:

            priority = "HOT"

        elif score >= 75:

            priority = "HIGH"

        elif score >= 60:

            priority = "GOOD"

        else:

            priority = "LOW"

        accepted = score >= 60

        logger.info(
            f"{job.title} | Score={score} | {priority}"
        )

        return Evaluation(

            accepted=accepted,

            score=score,

            priority=priority,

            reasons=reasons
        )