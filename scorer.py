from config import (
    SKILL_WEIGHTS,
    ROLE_BONUS,
    COUNTRY_BONUS
)

def score_job(job):

    text = (
        job["title"] +
        " " +
        job["description"]
    ).lower()

    score = 0

    matched_skills = []
    matched_roles = []
    matched_countries = []

    for skill, weight in SKILL_WEIGHTS.items():

        if skill in text:
            score += weight
            matched_skills.append(skill)

    for role, weight in ROLE_BONUS.items():

        if role in text:
            score += weight
            matched_roles.append(role)

    for country, weight in COUNTRY_BONUS.items():

        if country in text:
            score += weight
            matched_countries.append(country)

    return {
        "score": score,
        "skills": matched_skills,
        "roles": matched_roles,
        "countries": matched_countries
    }